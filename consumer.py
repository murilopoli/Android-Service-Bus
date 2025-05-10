import redis
import pika
import threading

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

def redis_consumer(host):
    try:
        r = redis.Redis(host=host, port=6379, db=0)
        pubsub = r.pubsub()
        pubsub.subscribe("mychannel")
        print("Consumidor Redis aguardando mensagens...")
        for message in pubsub.listen():
            if message['type'] == 'message':
                data = message['data'].decode()
                print(f"[Redis] Recebido: {data}")
                if data == "exit":
                    print("Saindo do consumidor Redis.")
                    break
    except Exception as e:
        print(f"[ERRO Redis] Não foi possível conectar: {e}")

def rabbitmq_consumer(host):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        channel = connection.channel()
        channel.exchange_declare(exchange='logs', exchange_type='fanout')
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange='logs', queue=queue_name)
        print("Consumidor RabbitMQ aguardando mensagens...")

        def callback(ch, method, properties, body):
            data = body.decode()
            print(f"[RabbitMQ] Recebido: {data}")
            if data == "exit":
                print("Saindo do consumidor RabbitMQ.")
                connection.close()
                exit(0)

        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        channel.start_consuming()
    except Exception as e:
        print(f"[ERRO RabbitMQ] Não foi possível conectar: {e}")

if __name__ == "__main__":
    host = get_connection_info()
    redis_on, rabbit_on = select_services()
    print("\nConsumidor iniciado. Apenas serviços habilitados receberão mensagens.\n")
    threads = []
    if redis_on:
        t = threading.Thread(target=redis_consumer, args=(host,))
        t.start()
        threads.append(t)
    if rabbit_on:
        t = threading.Thread(target=rabbitmq_consumer, args=(host,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
