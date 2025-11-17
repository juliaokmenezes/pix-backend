def serializar_mensagens(msgs):
    return [
        {
            "endToEndId": m.end_to_end_id,
            "valor": float(m.valor),
            "pagador": {
                "nome": m.pagador_nome,
                "cpfCnpj": m.pagador_cpf_cnpj,
                "ispb": m.pagador_ispb,
                "agencia": m.pagador_agencia,
                "contaTransacional": m.pagador_conta_transacional,
                "tipoConta": m.pagador_tipo_conta
            },
            "recebedor": {
                "nome": m.recebedor_nome,
                "cpfCnpj": m.recebedor_cpf_cnpj,
                "ispb": m.recebedor_ispb,
                "agencia": m.recebedor_agencia,
                "contaTransacional": m.recebedor_conta_transacional,
                "tipoConta": m.recebedor_tipo_conta
            },
            "campoLivre": m.campo_livre or "",
            "txId": m.tx_id,
            "dataHoraPagamento": m.data_hora_pagamento.isoformat()
        }
        for m in msgs
    ]
