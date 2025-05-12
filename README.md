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
pip install redis
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

Com este ambiente, você pode experimentar, estudar e integrar sistemas distribuídos de mensageria de forma sustentável, portátil e flexível, conforme a proposta do projeto.