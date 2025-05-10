# Android Service Bus

Este projeto implementa um barramento de comunicação sustentável, portátil e de fácil replicação, integrando **Redis** e **RabbitMQ** para facilitar a troca de mensagens entre sistemas distribuídos, tanto em ambiente doméstico quanto comercial de pequeno porte.

---

## Servidor (Android com UserLAnd)

### Requisitos

- Aparelho com Android 11
- Aplicativo [UserLAnd](https://play.google.com/store/apps/details?id=tech.ula) instalado
- Distribuição Ubuntu configurada dentro do UserLAnd
- Acesso ao terminal via app ou SSH (como o PuTTY)
- **Docker** e **Docker Compose** instalados
- **Python 3** instalado
- Bibliotecas Python:
```bash
pip install redis pika
```

---

### Etapas no Android

1. **Clone o repositório do projeto:**

```bash
git clone https://github.com/murilopoli/Android-Service-Bus.git
cd Android-Service-Bus/
```

2. **Inicie todos os serviços simultaneamente:**

```bash
chmod +x start_services.sh
./start_services.sh
```

3. **Verifique o status dos serviços:**

```bash
docker-compose ps
```

---

## 2. Executando os Scripts Python

### A. Consumer (Consumidor)

1. Execute:
```bash
python3 consumer.py
```

2. Siga as instruções:
- Escolha se a conexão será `localhost` ou outro IP.
- Habilite os serviços desejados (Redis, RabbitMQ).
- O consumidor ficará aguardando mensagens nos serviços selecionados.

### B. Producer (Produtor)

1. Em outro terminal, execute:
```bash
python3 producer.py
```

2. Siga as instruções:
- Escolha se a conexão será `localhost` ou outro IP.
- Habilite os serviços desejados (os mesmos do consumidor).
- Digite mensagens para enviar. Elas serão publicadas apenas nos serviços habilitados.

---

## 3. Parando os Serviços

Para parar todos os serviços Docker:
```bash
docker-compose down
```
---

## 4. Observações Importantes

- **Portas padrão:**  
  - Redis: 6379  
  - RabbitMQ: 5672 (mensageria), 15672 (painel web)

- **Conexão em rede local:**  
  - Para rodar producer/consumer em máquinas diferentes, informe o IP do servidor Docker na inicialização dos scripts.

- **Tratamento de erros:**  
  - Os scripts informam se algum serviço não está disponível e continuam rodando com os demais habilitados.

- **Painel RabbitMQ:**  
  - Acesse em [http://localhost:15672](http://localhost:15672)  
    Usuário: `guest`  
    Senha: `guest`

---

## 5. Estrutura do Projeto
Android-Service-Bus/
├── consumer.py
├── producer.py
├── start_services.sh
├── docker-compose.yml
└── README.md
---

## 6. Solução de Problemas

- **RabbitMQ:**
  - Se a porta 5672 estiver em uso, pare o serviço RabbitMQ local ou altere a porta do container no `docker-compose.yml`.

- **Redis:**
  - Certifique-se de que a porta 6379 não está ocupada por outro serviço local.

- **Mensagens de erro nos scripts Python:**
  - Os scripts exibem mensagens detalhadas caso não consigam se conectar aos serviços.

---

Com este ambiente, você pode experimentar, estudar e integrar sistemas distribuídos de mensageria de forma sustentável, portátil e flexível, conforme a proposta do projeto.