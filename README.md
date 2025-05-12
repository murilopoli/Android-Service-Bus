# Android Service Bus

Este projeto apresenta uma solução simples de comunicação via Redis, onde o consumidor roda em um aparelho Android utilizando o Ubuntu dentro do aplicativo UserLAnd, e o produtor roda em um computador com Windows. A troca de mensagens entre eles é feita pela rede local usando o Redis.

---

## Servidor (Android com UserLAnd)

### Requisitos

- Aparelho com Android 11
- Aplicativo [UserLAnd](https://play.google.com/store/apps/details?id=tech.ula) instalado
- Distribuição Ubuntu configurada dentro do UserLAnd
- Acesso ao terminal via app ou SSH (como o PuTTY)
- Python instalado em ambas as máquinas
- Redis Server instalado

---

### Etapas no Android

1. **Clone o repositório do projeto:**

```bash
git clone https://github.com/murilopoli/Android-Service-Bus.git
cd Android-Service-Bus/
```

2. **Execute o consumidor(Em outro terminal):**

```bash
cd ~/Android-Service-Bus/consumer
python3 consumer.py
```

---

## Cliente (Windows)

### Requisitos

- Python 3 instalado no sistema
- Código do projeto copiado para o Windows

---

### Etapas no Windows

1. **Abra o terminal (CMD ou PowerShell) e vá até a pasta `producer`:**

```powershell
cd C:\caminho\para\Android-Service-Bus\producer
```

2. **Crie e ative um ambiente virtual:**

```powershell
python -m venv .venv
.venv\Scripts\activate
```

3. **Execute o produtor:**

```powershell
python producer.py
```

---

## Observações importantes

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