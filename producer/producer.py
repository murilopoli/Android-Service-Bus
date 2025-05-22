import redis
import pika
import uuid
import json
import time
from kafka import KafkaProducer, KafkaConsumer

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

def get_rabbitmq_credentials():
    user = input("Usuario RabbitMQ (ex: user): ").strip()
    password = input("Senha RabbitMQ: ").strip()
    return pika.PlainCredentials(user, password)

def wait_redis_response(host, response_channel, pubsub, timeout=30):
    try:
        print(f"Aguardando resposta no canal {response_channel}...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            message = pubsub.get_message(timeout=1)
            if message and message['type'] == 'message':
                data = message['data'].decode()
                print(f"[Redis] Mensagem recebida no canal {response_channel}")
                return data
            time.sleep(0.1)
        return "Timeout: Nenhuma resposta recebida do Redis após {} segundos".format(timeout)
    except Exception as e:
        print(f"[ERRO Redis] Erro ao aguardar resposta: {e}")
        return None

def send_redis(host, msg):
    try:
        # Conexão separada para subscrição
        r_sub = redis.Redis(host=host, port=6379, db=0)
        pubsub = r_sub.pubsub()
        response_channel = f"response_{str(uuid.uuid4())}"
        # Subscrever ao canal de resposta antes de publicar a mensagem
        pubsub.subscribe(response_channel)
        print(f"Subscrevendo ao canal {response_channel} antes de enviar a mensagem...")
        time.sleep(0.5)  # Pequeno atraso para garantir subscrição
        # Conexão separada para publicar
        r_pub = redis.Redis(host=host, port=6379, db=0)
        message_data = json.dumps({"message": msg, "response_channel": response_channel})
        r_pub.publish("mychannel", message_data)
        print("Enviado via Redis.")
        # Esperar resposta com timeout de 30 segundos
        response = wait_redis_response(host, response_channel, pubsub, timeout=30)
        if response:
            print(f"[Redis] Resposta recebida: {response}")
        pubsub.unsubscribe(response_channel)
        r_sub.close()
        r_pub.close()
    except Exception as e:
        print(f"[ERRO Redis] Nao foi possivel enviar: {e}")

def send_rabbitmq(host, msg, credentials):
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, credentials=credentials)
        )
        channel = connection.channel()
        channel.exchange_declare(exchange='logs', exchange_type='fanout')
        response_queue = channel.queue_declare(queue='', exclusive=True).method.queue
        channel.queue_bind(exchange='responses', queue=response_queue)
        message_data = json.dumps({"message": msg, "response_queue": response_queue})
        channel.basic_publish(exchange='logs', routing_key='', body=message_data)
        print("Enviado via RabbitMQ.")

        def on_response(ch, method, props, body):
            data = body.decode()
            print(f"[RabbitMQ] Resposta recebida: {data}")
            ch.basic_cancel(consumer_tag='response_consumer')
            connection.close()

        channel.basic_consume(queue=response_queue, on_message_callback=on_response, auto_ack=True, consumer_tag='response_consumer')
        print("Aguardando resposta via RabbitMQ...")
        channel.start_consuming()
    except Exception as e:
        print(f"[ERRO RabbitMQ] Nao foi possivel enviar: {e}")

def wait_kafka_response(host, response_topic):
    try:
        consumer = KafkaConsumer(
            response_topic,
            bootstrap_servers=[f"{host}:9092"],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=f'response-group-{response_topic}',
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            consumer_timeout_ms=5000
        )
        print(f"Aguardando resposta no tópico {response_topic}...")
        for message in consumer:
            response = message.value.get("message", "Resposta recebida sem mensagem")
            consumer.close()
            return response
        return "Timeout: Nenhuma resposta recebida do Kafka"
    except Exception as e:
        print(f"[ERRO Kafka] Erro ao aguardar resposta: {e}")
        return None

def send_kafka(host, msg):
    try:
        response_topic = f"response_{str(uuid.uuid4())}"
        producer = KafkaProducer(
            bootstrap_servers=[f"{host}:9092"],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        message_data = {"message": msg, "response_topic": response_topic}
        producer.send('my-topic', value=message_data)
        producer.flush()
        print("Enviado via Kafka.")
        response = wait_kafka_response(host, response_topic)
        if response:
            print(f"[Kafka] Resposta recebida: {response}")
        producer.close()
    except Exception as e:
        print(f"[ERRO Kafka] Nao foi possivel enviar: {e}")

if __name__ == "__main__":
    host = get_connection_info()
    redis_on, rabbit_on, kafka_on = select_services()
    rabbitmq_credentials = None
    if rabbit_on:
        rabbitmq_credentials = get_rabbitmq_credentials()
    print("\nProdutor iniciado. Apenas servicos habilitados enviarao mensagens.\n")
    while True:
        msg = input("Mensagem para enviar (ou 'exit' para sair): ")
        if msg == "exit":
            break
        if redis_on:
            send_redis(host, msg)
        if rabbit_on:
            send_rabbitmq(host, msg, rabbitmq_credentials)
        if kafka_on:
            send_kafka(host, msg)
