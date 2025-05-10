#!/bin/bash

# Verifica se Docker está instalado
if ! command -v docker &> /dev/null
then
    echo "Docker não está instalado. Instale o Docker antes de continuar."
    exit 1
fi

# Verifica se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null
then
    echo "Docker Compose não está instalado. Instale o Docker Compose antes de continuar."
    exit 1
fi

# Cria o arquivo docker-compose.yml se não existir
if [ ! -f docker-compose.yml ]; then
    cat <<EOF > docker-compose.yml
version: "3.8"

services:
  redis:
    image: redis
    container_name: redis
    restart: always
    ports:
      - "6379:6379"

  rabbitmq:
    image: rabbitmq:management
    container_name: rabbitmq
    restart: always
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: guest
      RABBITMQ_DEFAULT_PASS: guest
EOF
    echo "Arquivo docker-compose.yml criado."
fi

# Sobe todos os serviços
echo "Inicializando Redis e RabbitMQ..."
docker-compose up -d

echo "Todos os serviços foram inicializados em background."
echo "Verifique o status com: docker-compose ps"
