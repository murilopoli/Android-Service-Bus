import redis
import pika
import threading
import json
from kafka import KafkaConsumer

def get_connection_info():
    print("Conexao:\n1 - Localhost\n2 - Outro IP na rede local")
    choice = input("Selecione (1/2): ").strip()
    return "localhost" if choice == "1" else input("Digite o IP do servidor: ").strip()

def select_services():
    print("Selecione os servicos a habilitar:")
    redis_on = input("Habilitar Redis? (s/n): ").strip().lower() == 's'
    rabbit_on = input("Habilitar RabbitMQ? (s/n): ").strip().lower() == 's'
    kafka_on = input("Habilitar Kafka? (s/n): ").strip().lower() == 's'
    return redis_on, rabbit_on, kafka_on

def redis_consumer(host):
    try:
        r = redis.Redis(host=host, port=6379, db=0)
        pubsub = r.pubsub()
        pubsub.subscribe("mychannel")
        print("Consumidor Redis aguardando mensagens...")
        for message in pubsub.listen():
            if message['type'] == 'message':
                data = message['data'].decode()
                message_obj = json.loads(data)
                msg = message_obj.get("message")
                response_channel = message_obj.get("response_channel")
                print(f"[Redis] Recebido: {msg}")
                if response_channel:
                    response = f"Confirmado: {msg} recebido com sucesso"
                    r.publish(response_channel, response)
                    print(f"[Redis] Resposta enviada para {response_channel}")
                if msg == "exit":
                    print("Saindo do consumidor Redis.")
                    break
    except Exception as e:
        print(f"[ERRO Redis] Nao foi possivel conectar: {e}")

def rabbitmq_consumer(host):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        channel = connection.channel()
        channel.exchange_declare(exchange='logs', exchange_type='fanout')
        channel.exchange_declare(exchange='responses', exchange_type='fanout')
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange='logs', queue=queue_name)
        print("Consumidor RabbitMQ aguardando mensagens...")

        def callback(ch, method, properties, body):
            data = body.decode()
            message_obj = json.loads(data)
            msg = message_obj.get("message")
            response_queue = message_obj.get("response_queue")
            print(f"[RabbitMQ] Recebido: {msg}")
            if response_queue:
                response = f"Confirmado: {msg} recebido com sucesso"
                ch.basic_publish(exchange='', routing_key=response_queue, body=response)
                print(f"[RabbitMQ] Resposta enviada para {response_queue}")
            if msg == "exit":
                print("Saindo do consumidor RabbitMQ.")
                connection.close()
                exit(0)

        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        channel.start_consuming()
    except Exception as e:
        print(f"[ERRO RabbitMQ] Nao foi possivel conectar: {e}")

def kafka_consumer(host):
    try:
        consumer = KafkaConsumer(
            'my-topic',
            bootstrap_servers=[f"{host}:9092"],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='my-group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        print("Consumidor Kafka aguardando mensagens...")
        for message in consumer:
            message_data = message.value
            msg = message_data.get("message")
            response_topic = message_data.get("response_topic")
            print(f"[Kafka] Recebido: {msg}")
            if response_topic:
                from kafka import KafkaProducer
                producer = KafkaProducer(
                    bootstrap_servers=[f"{host}:9092"],
                    value_serializer=lambda v: json.dumps(v).encode('utf-8')
                )
                response = {"message": f"Confirmado: {msg} recebido com sucesso"}
                producer.send(response_topic, value=response)
                producer.close()
                print(f"[Kafka] Resposta enviada para {response_topic}")
            if msg == "exit":
                print("Saindo do consumidor Kafka.")
                break
    except Exception as e:
        print(f"[ERRO Kafka] Nao foi possivel conectar: {e}")

if __name__ == "__main__":
    host = get_connection_info()
    redis_on, rabbit_on, kafka_on = select_services()
    print("\nConsumidor iniciado. Apenas servicos habilitados receberao mensagens.\n")
    threads = []
    if redis_on:
        t = threading.Thread(target=redis_consumer, args=(host,))
        t.start()
        threads.append(t)
    if rabbit_on:
        t = threading.Thread(target=rabbitmq_consumer, args=(host,))
        t.start()
        threads.append(t)
    if kafka_on:
        t = threading.Thread(target=kafka_consumer, args=(host,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
