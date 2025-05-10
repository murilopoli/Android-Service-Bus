import redis
import pika

def get_connection_info():
    print("Conexão:")
    print("1 - Localhost")
    print("2 - Outro IP na rede local")
    choice = input("Selecione (1/2): ").strip()
    if choice == "1":
        return "localhost"
    else:
        return input("Digite o IP do servidor: ").strip()

def select_services():
    print("Selecione os serviços a habilitar:")
    redis_on = input("Habilitar Redis? (s/n): ").strip().lower() == 's'
    rabbit_on = input("Habilitar RabbitMQ? (s/n): ").strip().lower() == 's'
    return redis_on, rabbit_on

def send_redis(host, msg):
    try:
        r = redis.Redis(host=host, port=6379, db=0)
        r.publish("mychannel", msg)
        print("Enviado via Redis.")
    except Exception as e:
        print(f"[ERRO Redis] Não foi possível enviar: {e}")

def send_rabbitmq(host, msg):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        channel = connection.channel()
        channel.exchange_declare(exchange='logs', exchange_type='fanout')
        channel.basic_publish(exchange='logs', routing_key='', body=msg)
        connection.close()
        print("Enviado via RabbitMQ.")
    except Exception as e:
        print(f"[ERRO RabbitMQ] Não foi possível enviar: {e}")

if __name__ == "__main__":
    host = get_connection_info()
    redis_on, rabbit_on = select_services()
    print("\nProdutor iniciado. Apenas serviços habilitados enviarão mensagens.\n")
    while True:
        msg = input("Mensagem para enviar (ou 'exit' para sair): ")
        if msg == "exit":
            break
        if redis_on:
            send_redis(host, msg)
        if rabbit_on:
            send_rabbitmq(host, msg)
