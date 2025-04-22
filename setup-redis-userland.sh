#!/bin/bash

echo "🔧 Atualizando pacotes..."
sudo apt update && sudo apt upgrade -y

echo "📦 Instalando Redis, Git e Python pip..."
sudo apt install redis-server git python3-pip -y

echo "⚙️ Configurando Redis para aceitar conexões externas..."
sudo sed -i 's/^bind .*/bind 0.0.0.0/' /etc/redis/redis.conf
sudo sed -i 's/^protected-mode .*/protected-mode no/' /etc/redis/redis.conf

echo "🚀 Iniciando Redis com configurações abertas..."
nohup redis-server --protected-mode no --bind 0.0.0.0 &>/dev/null &

echo "🐍 Instalando dependências do consumer..."
cd ~/Android-Service-Bus/consumer
pip install -r requirements.txt

echo "✅ Setup concluído com sucesso! Execute o consumer com: 'python3 consumer.py' na pasta ~/Android-Service-Bus/consumer"
