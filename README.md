# pix-backend

### Para subir a base de dados utilize o comando:
docker run -d \
  -p 5432:5432 \
  --name postgres-db \
  -e POSTGRES_USER=<user> \
  -e POSTGRES_PASSWORD=<senha> \
  -e POSTGRES_DB=<postgres-db> \
  postgres
