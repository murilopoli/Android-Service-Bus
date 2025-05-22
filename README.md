# Android Service Bus

**Android Service Bus** é uma solução de barramento de comunicação para sistemas distribuídos, utilizando smartphones Android como middleware de mensageria (Redis, RabbitMQ, Kafka). Focado em sustentabilidade, reaproveita dispositivos subutilizados, oferecendo comunicação bidirecional para feedback imediato.

## Motivação
Soluções de mensageria tradicionais são complexas para ambientes domésticos ou pequenos. Este projeto simplifica a integração de sistemas distribuídos usando dispositivos Android como servidores, promovendo acessibilidade e redução de custos.

## Arquitetura
- **Broker**: Middleware (Redis, RabbitMQ, Kafka) no Android via UserLAnd.
- **Consumidor**: Processa mensagens e envia respostas.
- **Produtor**: Publica mensagens e aguarda respostas.
A solução é independente de linguagem, garantindo flexibilidade.

## Funcionalidades
- Suporte a Redis, RabbitMQ e Kafka.
- Comunicação bidirecional.
- Portabilidade e sustentabilidade com dispositivos Android.

## Requisitos
### Servidor (Android)
- Android 11+.
- UserLAnd com Ubuntu.
- Middlewares instalados.
### Cliente (Windows/Outro)
- Python 3.
- Código do projeto.

## Instalação e Execução
### No Android (Servidor/Consumidor)

1. **Configurar UserLAnd**: Instale, configure Ubuntu, acesse terminal.

2. **Instalar Redis**:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install redis-server -y
```
Edite `/etc/redis/redis.conf`: 
```bash
bind 0.0.0.0
protected-mode no
daemonize yes
```
Inicie: `redis-server /etc/redis/redis.conf`.

3.**Instalar o RabbitMQ**:
```bash
sudo apt install rabbitmq-server -y
```
Configure usuario:
```bash
sudo rabbitmqctl add_user user pass
sudo rabbitmqctl set_user_tags user administrator
sudo rabbitmqctl set_permissions -p / user ".*" ".*" ".*"
```

Inicie: `sudo rabbitmq-server`.

4. **Kafka/ZooKeeper**:
Instale Java:
```bash
sudo apt install openjdk-17-jdk -y
```

Baixe Kafka (3.9.1):
```bash
curl "https://downloads.apache.org/kafka/3.9.1/kafka_2.13-3.9.1.tgz" -o ~/kafka.tgz
```

Extraia:
```bash
mkdir ~/kafka && cd ~/kafka
tar -xvzf ~/kafka.tgz --strip 1
```

Configure ZooKeeper:
```bash
cd ~/
mkdir ~/zookeeper-data
nano ~/kafka/config/zookeeper.properties
```
Adicione: `dataDir=/home/user/zookeeper-data`, `clientPort=2181`, `maxClientCnxns=0`.

Configure Kafka:
```bash
nano ~/kafka/config/server.properties
```
Adicione:
```bash
delete.topic.enable=true
log.dirs=/home/user/logs
broker.id=0
zookeeper.connect=localhost:2181
listeners=PLAINTEXT://0.0.0.0:9092
advertised.listeners=PLAINTEXT://IP_DO_ANDROID:9092
```
Inicie:
```bash
nohup ~/kafka/bin/zookeeper-server-start.sh ~/kafka/config/zookeeper.properties > ~/zookeeper.log 2>&1 &
sleep 5
nohup ~/kafka/bin/kafka-server-start.sh ~/kafka/config/server.properties > ~/kafka.log 2>&1 &
```

5. **Execute o consumidor:**

```bash
cd ~/Android-Service-Bus/consumer
pip install -r requirements.txt
python3 consumer.py
```

6. **Obter IP do Android**: Execute `ip addr` e anote o IP.

7. **Executar Consumidor**:
```bash
git clone https://github.com/murilopoli/Android-Service-Bus.git
cd Android-Service-Bus/consumer
pip install -r requirements.txt
python3 consumer.py
```
Selecione conexão e serviços (Redis/RabbitMQ/Kafka).

### No Cliente (Produtor)
1. **Preparar Ambiente**:

Instale Python 3, clone repositório:
```bash
git clone https://github.com/murilopoli/Android-Service-Bus.git
cd Android-Service-Bus
```
2. **Executar Produtor**:
#### Windows
```powershell
cd producer
python -m venv .venv
.venv\Scripts\activate
```
ou source .venv/bin/activate 

#### Linux/Mac
```bash
pip install -r requirements.txt
python producer.py
```
Insira IP do Android, selecione serviços, envie mensagens (digite `exit` para sair).

## Detalhes da Implementação
- **Redis**: Canal de resposta único por mensagem.
- **RabbitMQ**: Fila temporária para respostas.
- **Kafka**: Tópico de resposta único, timeout de 5s.
- **Código**: producer.py envia mensagens e espera respostas; consumer.py processa e responde.

## Observações
- Use em redes locais seguras (portas 6379/5672/9092/2181 liberadas).
- Não exponha serviços à internet; configure senhas.
- Voltado para estudo e testes.

## Vantagens
- Sustentabilidade: Reutiliza smartphones.
- Feedback imediato via respostas.
- Flexível e fácil de usar.

## Futuras Melhorias
- Retries e persistência.
- Interface gráfica.
- Análises preditivas e integração ERP.

---

Esse projeto foi desenvolvido para fins de estudo e testes locais, facilitando a troca de dados entre dispositivos Android e Windows usando Redis.
