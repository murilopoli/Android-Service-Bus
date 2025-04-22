# Android Service Bus

Este projeto apresenta uma solução simples de comunicação via Redis, onde o consumidor roda em um aparelho Android utilizando o Ubuntu dentro do aplicativo UserLAnd, e o produtor roda em um computador com Windows. A troca de mensagens entre eles é feita pela rede local usando o Redis.

---

## Servidor (Android com UserLAnd)

### Requisitos

- Aparelho com Android 11
- Aplicativo [UserLAnd](https://play.google.com/store/apps/details?id=tech.ula) instalado
- Distribuição Ubuntu configurada dentro do UserLAnd
- Acesso ao terminal via app ou SSH (como o PuTTY)

---

### Etapas no Android

1. **Clone o repositório do projeto:**

```bash
git clone https://github.com/murilopoli/Android-Service-Bus.git
cd Android-Service-Bus/
```

2. **Dê permissão e execute o script de configuração:**

```bash
chmod +x setup-redis-userland.sh
./setup-redis-userland.sh
```

> O script altera as configurações do Redis para permitir conexões de outros dispositivos na mesma rede local.

3. **Execute o consumidor(Em outro terminal):**

```bash
cd ~/Android-Service-Bus/consumer
pip install -r requirements.txt
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

3. **Instale as dependências necessárias:**

```powershell
pip install -r requirements.txt
```

4. **Execute o produtor:**

```powershell
python producer.py
```

---

## Observações importantes

- Verifique se a porta 6379 está liberada na rede local para permitir a comunicação entre os dispositivos.
- Não é recomendado expor o Redis diretamente para a internet. Essa configuração foi feita para funcionar dentro de uma rede segura.
- Para reforçar a segurança, considere definir uma senha no arquivo `redis.conf`.

---

Esse projeto foi desenvolvido para fins de estudo e testes locais, facilitando a troca de dados entre dispositivos Android e Windows usando Redis.
