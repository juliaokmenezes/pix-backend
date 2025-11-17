# Pix Message Reader

## Sobre

Este repositório contém o backend de uma aplicação desenvolvida com **Django**, voltada para leitura e geração de mensagens Pix simuladas. O projeto faz parte de um desafio técnico inspirado na Interface de Comunicação do SPI (Banco Central), adaptado para Python/Django. A aplicação é capaz de lidar com alto volume de mensagens, mantendo controle de concorrência, long polling e streams simultâneos de leitura.

---

### Camadas do Projeto

- **Models**: Contém as entidades de domínio (`Pix` e `PixStream`)
- **Serializers**: Transforma os objetos `Pix` em JSON para retorno via API
- **Service Layer**: Lógica de negócio, geração de mensagens, long polling, controle de concorrência e streams
- **Views**: Endpoints HTTP que recebem requisições, chamam os serviços e retornam respostas JSON
- **Utils**: Funções auxiliares, como geração de `iterationId`

---

## Tecnologias Utilizadas

- **Python 3.12**
- **Django 5.2.8**
- **PostgreSQL 17**
- **Docker / Docker Compose**
- **pytest / pytest-django**
- **Git** para versionamento

---

## Decisões Técnicas

### 1. Redundância proposital do `recebedor_ispb`

Optei por adicionar o campo `recebedor_ispb` diretamente na tabela `Pix`, mesmo que isso fira a normalização estrita do banco de dados. Essa decisão foi tomada considerando que:

- As consultas de mensagens Pix dependem fortemente do filtro por `recebedor_ispb`
- Ganho significativo em performance ao evitar JOINs em consultas de alto volume
- Índices compostos otimizam ainda mais as queries frequentes

**Trade-off:** Redundância controlada em troca de performance em escala.

### 2. Controle de Concorrência Pessimista

Para garantir que uma mesma mensagem Pix não seja lida por múltiplas streams simultaneamente, implementei:

- **`select_for_update(skip_locked=True)`**: Trava as linhas durante a leitura
- **`skip_locked=True`**: Permite que outros coletores pulem registros travados e busquem mensagens disponíveis
- Campo `dado_visualizado` para marcar mensagens já processadas

**Resultado:** Eliminação de race conditions e duplicatas em ambientes concorrentes.

### 3. Long Polling com Loop Simples

Implementei long polling usando um loop com `time.sleep()` que:

- Aguarda até 8 segundos antes de retornar 204 (No Content)
- Verifica mensagens a cada 0.5 segundos
- Retorna imediatamente quando encontra mensagens disponíveis

Optei pela simplicidade inicial seguindo o princípio KISS. Alternativas como EventEmitter ou Django Channels podem ser consideradas para evolução futura.

### 4. Separação em Camadas

- **Models**: Definição dos dados e estrutura do banco
- **Service**: Lógica de negócio isolada dos controllers
- **Views**: Controllers HTTP enxutos, delegando para a camada de serviço
- **Serializers**: Transformação de dados para formato JSON
- **Utils**: Funções auxiliares reutilizáveis

---

## Endpoints Disponíveis

### 1. Cadastro de mensagens Pix (para testes)

**POST** `/api/util/msgs/{ispb}/{number}`

Insere mensagens Pix aleatórias no banco de dados para testes.

**Parâmetros:**
- `ispb`: Código de 8 dígitos da instituição recebedora
- `number`: Quantidade de mensagens a serem criadas (1-1000)

**Exemplo:**
```bash
curl -X POST http://localhost:8000/api/util/msgs/32074986/50
```

**Resposta:**
```json
{
  "mensagem": "50 mensagens Pix cadastradas com sucesso para ISPB 32074986"
}
```

---

### 2. Iniciar stream de mensagens

**GET** `/api/pix/{ispb}/stream/start`

Inicia a recuperação de mensagens Pix para uma instituição.

**Headers:**
- `Accept: application/json` - Retorna 1 mensagem por vez
- `Accept: multipart/json` - Retorna até 10 mensagens por vez

**Comportamento:**
- **200**: Mensagens encontradas
- **204**: Nenhuma mensagem disponível (após 8s de espera)
- **429**: Limite de 6 coletores simultâneos atingido

**Response Headers:**
- `Pull-Next`: URI para buscar próximas mensagens

**Exemplo:**
```bash
curl -H "Accept: multipart/json" \
     http://localhost:8000/api/pix/32074986/stream/start
```

**Resposta (200):**
```json
{
  "mensagens": [
    {
      "endToEndId": "E320749862024022119277T3lEBbUM0z",
      "valor": 90.20,
      "pagador": {
        "nome": "Maria Silva",
        "cpfCnpj": "98716278190",
        "ispb": "32074986",
        "agencia": "0001",
        "contaTransacional": "1231231",
        "tipoConta": "CACC"
      },
      "recebedor": {
        "nome": "Loja Centro",
        "cpfCnpj": "77615678291",
        "ispb": "32074986",
        "agencia": "0361",
        "contaTransacional": "1210098",
        "tipoConta": "SVGS"
      },
      "campoLivre": "",
      "txId": "h7a786d8a7s6gd1hgs",
      "dataHoraPagamento": "2024-02-21T19:47:18.108Z"
    }
  ]
}
```

---

### 3. Continuar stream de mensagens

**GET** `/api/pix/{ispb}/stream/{iterationId}`

Continua a recuperação de mensagens usando o `iterationId` fornecido no header `Pull-Next`.

**Comportamento:** Idêntico ao endpoint `/stream/start`

**Exemplo:**
```bash
curl -H "Accept: multipart/json" \
     http://localhost:8000/api/pix/32074986/stream/abc123def456
```

---

### 4. Encerrar stream

**DELETE** `/api/pix/{ispb}/stream/{iterationId}/delete`

Encerra um stream de leitura ativo.

**Exemplo:**
```bash
curl -X DELETE http://localhost:8000/api/pix/32074986/stream/abc123def456/delete
```

**Resposta:**
```json
{
  "mensagem": "Stream encerrado com sucesso",
  "iterationId": "abc123def456"
}
```

---


## Pontos de Evolução e Melhorias

1. Migrar Long Polling para Abordagem Assíncrona

2. Melhorar Algoritimo de Inserção

3. Inserir Monitoramento e Observabilidade

---

## Como Rodar a Aplicação

### Pré-requisitos

- **Docker** e **Docker Compose** instalados

### Passos

1. **Clone o repositório:**

```bash
git clone https://github.com/seu-usuario/pix-backend.git
cd pix-backend
```

2. **Inicie os containers:**

```bash
docker-compose up --build
```

3. **Aguarde a inicialização** (Django + PostgreSQL)

4. **Acesse a API:**

A aplicação estará disponível em `http://localhost:8000`

---

## Como Rodar os Testes

### Opção 1: Com Docker

```bash#

# Caso a aplicação esteja Down
docker compose run web python manage.py test

#Caso a aplicação esteja Up

docker compose exec web python manage.py test

```

### Opção 2: Localmente

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar testes
python manage.py test

```


---
