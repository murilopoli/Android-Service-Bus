import time
import threading
import random
from datetime import datetime

# --- Configuracao ---
# ATENCAO: Ajuste estas configuracoes de acordo com o seu ambiente de testes.
# Certifique-se de que os servicos (Redis, RabbitMQ, Kafka) estao rodando e
# acessiveis a partir da maquina onde este script sera executado, usando os
# IPs e credenciais fornecidos.

# Configuracao Redis
REDIS_HOST = "192.168.1.8" # Altere para o IP do seu servidor Redis (ex: "192.168.1.100")
REDIS_PORT = 6379 # Porta padrao do Redis
REDIS_CHANNEL = "android_service_bus_test"

# Configuracao RabbitMQ
RABBITMQ_HOST = "192.168.1.8" # Altere para o IP do seu servidor RabbitMQ (ex: "192.168.1.101")
RABBITMQ_PORT = 5672 # Porta padrao do RabbitMQ
RABBITMQ_USERNAME = "admin" # Altere para o nome de usuario administrador do RabbitMQ
RABBITMQ_PASSWORD = "admin" # Altere para a senha do usuario administrador do RabbitMQ
RABBITMQ_QUEUE = "android_service_bus_test_queue"

# Configuracao Kafka
KAFKA_BOOTSTRAP_SERVERS = ["192.168.1.8:9092"] # Lista de enderecos dos brokers Kafka (ex: ["192.168.1.102:9092"])
KAFKA_TOPIC = "android_service_bus_test_topic"
# OBS: Autenticacao Kafka (SASL/SSL) precisaria de configuracao adicional aqui se necessaria.

NUM_MESSAGES_PER_TEST = 50000
MESSAGE_SIZE_BYTES = 100
NUM_CONCURRENT_CLIENTS = 50

SAMPLE_MESSAGE = 'A' * MESSAGE_SIZE_BYTES

# --- Variavel global para o arquivo de log e metricas do resumo ---
LOG_FILE_HANDLE = None
GLOBAL_METRICS = {
    "Redis": {"produtor": {"mensagens": 0, "tempo": 0, "erros": 0}, "consumidor": {"mensagens": 0, "tempo": 0, "erros": 0}},
    "RabbitMQ": {"produtor": {"mensagens": 0, "tempo": 0, "erros": 0}, "consumidor": {"mensagens": 0, "tempo": 0, "erros": 0}},
    "Kafka": {"produtor": {"mensagens": 0, "tempo": 0, "erros": 0}, "consumidor": {"mensagens": 0, "tempo": 0, "erros": 0}},
}
GLOBAL_METRICS_LOCK = threading.Lock() # Para garantir acesso seguro as metricas globais


# --- Funcoes Auxiliares para Metricas ---
def record_metric(middleware, client_type, operation, start_time, end_time, messages_processed, errors=0):
    """
    Registra e imprime as metricas de performance de uma operacao de teste.
    Tambem escreve essas metricas no arquivo de log e atualiza as metricas globais.

    Args:
        middleware (str): O nome do middleware (ex: "Redis", "RabbitMQ", "Kafka").
        client_type (str): O tipo de cliente (ex: "Produtor", "Consumidor").
        operation (str): A operacao realizada (ex: "Publicacao", "Recebimento").
        start_time (float): Tempo de inicio da operacao (em segundos).
        end_time (float): Tempo de termino da operacao (em segundos).
        messages_processed (int): Numero de mensagens processadas.
        errors (int): Numero de erros encontrados durante a operacao.
    """
    duration_seconds = end_time - start_time
    duration_ms = duration_seconds * 1000 # Converte para milissegundos
    throughput = (messages_processed / duration_seconds) if duration_seconds > 0 else 0

    log_output = []
    log_output.append(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {middleware} - {client_type} {operation}:") # Inclui milissegundos
    log_output.append(f"  Mensagens Processadas: {messages_processed}")
    log_output.append(f"  Duracao: {duration_ms:.2f} ms") # Exibe em milissegundos
    log_output.append(f"  Throughput: {throughput:.2f} mensagens/segundo")
    log_output.append(f"  Erros: {errors}\n")

    # Imprime no console
    for line in log_output:
        print(line)

    # Escreve no arquivo de log se ele estiver aberto
    if LOG_FILE_HANDLE:
        for line in log_output:
            LOG_FILE_HANDLE.write(line + "\n")

    # Atualiza metricas globais para o resumo final
    with GLOBAL_METRICS_LOCK:
        tipo = "produtor" if "Produtor" in client_type else "consumidor"
        GLOBAL_METRICS[middleware][tipo]["mensagens"] += messages_processed
        GLOBAL_METRICS[middleware][tipo]["tempo"] += duration_seconds # Mantem em segundos para somar e depois converter para resumo
        GLOBAL_METRICS[middleware][tipo]["erros"] += errors


# --- Redis Tests ---
try:
    import redis
except ImportError:
    print("Biblioteca Redis nao encontrada. Por favor, instale: pip install redis")
    if LOG_FILE_HANDLE:
        LOG_FILE_HANDLE.write("Biblioteca Redis nao encontrada. Por favor, instale: pip install redis\n")
    redis = None

def run_redis_producer(client_id):
    if not redis: return
    try:
        r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        r.ping() # Testa a conexao
    except Exception as e:
        error_msg = f"Erro de Conexao Redis para Produtor (Cliente {client_id}): {e}"
        print(error_msg)
        if LOG_FILE_HANDLE: LOG_FILE_HANDLE.write(error_msg + "\n")
        return

    messages_sent = 0
    errors = 0
    start_time = time.time()
    for i in range(NUM_MESSAGES_PER_TEST // NUM_CONCURRENT_CLIENTS):
        try:
            message = f"redis_msg_{client_id}_{i}" + SAMPLE_MESSAGE
            r.publish(REDIS_CHANNEL, message)
            messages_sent += 1
        except Exception as e:
            errors += 1
            error_msg = f"Erro no Produtor Redis (Cliente {client_id}): {e}"
            print(error_msg)
            if LOG_FILE_HANDLE: LOG_FILE_HANDLE.write(error_msg + "\n")
    end_time = time.time()
    record_metric("Redis", f"Produtor (Cliente {client_id})", "Publicacao", start_time, end_time, messages_sent, errors)

def run_redis_consumer(client_id):
    if not redis: return
    try:
        r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        r.ping() # Testa a conexao
    except Exception as e:
        error_msg = f"Erro de Conexao Redis para Consumidor (Cliente {client_id}): {e}"
        print(error_msg)
        if LOG_FILE_HANDLE: LOG_FILE_HANDLE.write(error_msg + "\n")
        return

    pubsub = r.pubsub()
    pubsub.subscribe(REDIS_CHANNEL)
    messages_received = 0
    errors = 0
    start_time = time.time()
    for message in pubsub.listen():
        if message['type'] == 'message':
            messages_received += 1
            if messages_received >= (NUM_MESSAGES_PER_TEST // NUM_CONCURRENT_CLIENTS):
                break
        if time.time() - start_time > 30: # Timeout de 30 segundos
            timeout_msg = f"Tempo limite excedido para o Consumidor Redis (Cliente {client_id})."
            print(timeout_msg)
            if LOG_FILE_HANDLE: LOG_FILE_HANDLE.write(timeout_msg + "\n")
            break
    end_time = time.time()
    record_metric("Redis", f"Consumidor (Cliente {client_id})", "Inscricao e Recebimento", start_time, end_time, messages_received, errors)
    pubsub.unsubscribe(REDIS_CHANNEL)

def test_redis_scalability_and_stress():
    print("\n--- Rodando Testes Redis ---")
    if LOG_FILE_HANDLE: LOG_FILE_HANDLE.write("\n--- Rodando Testes Redis ---\n")
    producer_threads = []
    consumer_threads = []

    for i in range(NUM_CONCURRENT_CLIENTS):
        consumer_thread = threading.Thread(target=run_redis_consumer, args=(i,))
        consumer_threads.append(consumer_thread)
        consumer_thread.start()
    time.sleep(2)

    for i in range(NUM_CONCURRENT_CLIENTS):
        producer_thread = threading.Thread(target=run_redis_producer, args=(i,))
        producer_threads.append(producer_thread)
        producer_thread.start()

    for t in producer_threads:
        t.join()
    for t in consumer_threads:
        t.join()
    print("--- Testes Redis Finalizados ---\n")
    if LOG_FILE_HANDLE: LOG_FILE_HANDLE.write("--- Testes Redis Finalizados ---\n\n")

# --- RabbitMQ Tests ---
try:
    import pika
except ImportError:
    print("Biblioteca Pika nao encontrada. Por favor, instale: pip install pika")
    if LOG_FILE_HANDLE:
        LOG_FILE_HANDLE.write("Biblioteca Pika nao encontrada. Por favor, instale: pip install pika\n")
    pika = None

def run_rabbitmq_producer(client_id):
    if not pika: return
    connection = None
    try:
        credentials = pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials))
        channel = connection.channel()
        channel.queue_declare(queue=RABBITMQ_QUEUE)
        messages_sent = 0
        errors = 0
        start_time = time.time()
        for i in range(NUM_MESSAGES_PER_TEST // NUM_CONCURRENT_CLIENTS):
            try:
                message = f"rabbitmq_msg_{client_id}_{i}" + SAMPLE_MESSAGE
                channel.basic_publish(exchange='', routing_key=RABBITMQ_QUEUE, body=message.encode('utf-8'))
                messages_sent += 1
            except Exception as e:
                errors += 1
                error_msg = f"Erro no Produtor RabbitMQ (Cliente {client_id}): {e}"
                print(error_msg)
                if LOG_FILE_HANDLE: LOG_FILE_HANDLE.write(error_msg + "\n")
        end_time = time.time()
        record_metric("RabbitMQ", f"Produtor (Cliente {client_id})", "Publicacao", start_time, end_time, messages_sent, errors)
    except Exception as e:
        conn_error_msg = f"Erro de Conexao/Autenticacao do Produtor RabbitMQ (Cliente {client_id}): {e}"
        print(conn_error_msg)
        if LOG_FILE_HANDLE: LOG_FILE_HANDLE.write(conn_error_msg + "\n")
    finally:
        if connection:
            connection.close()

def run_rabbitmq_consumer(client_id, messages_to_consume):
    if not pika: return
    connection = None
    try:
        credentials = pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials))
        channel = connection.channel()
        channel.queue_declare(queue=RABBITMQ_QUEUE)
        messages_received = 0
        errors = 0
        start_time = time.time()

        def callback(ch, method, properties, body):
            nonlocal messages_received
            nonlocal errors
            messages_received += 1
            ch.basic_ack(delivery_tag=method.delivery_tag)
            if messages_received >= messages_to_consume:
                channel.stop_consuming()

        channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback)
        wait_msg = f"Consumidor RabbitMQ (Cliente {client_id}) esperando por mensagens..."
        print(wait_msg)
        if LOG_FILE_HANDLE: LOG_FILE_HANDLE.write(wait_msg + "\n")
        channel.start_consuming()
        end_time = time.time()
        record_metric("RabbitMQ", f"Consumidor (Cliente {client_id})", "Recebimento", start_time, end_time, messages_received, errors)
    except Exception as e:
        conn_error_msg = f"Erro de Conexao/Autenticacao do Consumidor RabbitMQ (Cliente {client_id}): {e}"
        print(conn_error_msg)
        if LOG_FILE_HANDLE: LOG_FILE_HANDLE.write(conn_error_msg + "\n")
    finally:
        if connection:
            connection.close()

def test_rabbitmq_scalability_and_stress():
    print("\n--- Rodando Testes RabbitMQ ---")
    if LOG_FILE_HANDLE: LOG_FILE_HANDLE.write("\n--- Rodando Testes RabbitMQ ---\n")
    producer_threads = []
    consumer_threads = []
    messages_per_consumer = NUM_MESSAGES_PER_TEST // NUM_CONCURRENT_CLIENTS

    for i in range(NUM_CONCURRENT_CLIENTS):
        consumer_thread = threading.Thread(target=run_rabbitmq_consumer, args=(i, messages_per_consumer))
        consumer_threads.append(consumer_thread)
        consumer_thread.start()
    time.sleep(2)

    for i in range(NUM_CONCURRENT_CLIENTS):
        producer_thread = threading.Thread(target=run_rabbitmq_producer, args=(i,))
        producer_threads.append(producer_thread)
        producer_thread.start()

    for t in producer_threads:
        t.join()
    for t in consumer_threads:
        t.join()
    print("--- Testes RabbitMQ Finalizados ---\n")
    if LOG_FILE_HANDLE: LOG_FILE_HANDLE.write("--- Testes RabbitMQ Finalizados ---\n\n")

# --- Kafka Tests ---
try:
    from kafka import KafkaProducer, KafkaConsumer
    from kafka.errors import NoBrokersAvailable
except ImportError:
    print("Biblioteca Kafka nao encontrada. Por favor, instale: pip install kafka-python")
    if LOG_FILE_HANDLE:
        LOG_FILE_HANDLE.write("Biblioteca Kafka nao encontrada. Por favor, instale: pip install kafka-python\n")
    KafkaProducer, KafkaConsumer, NoBrokersAvailable = None, None, None

def run_kafka_producer(client_id):
    if not KafkaProducer: return
    producer = None
    try:
        producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
        messages_sent = 0
        errors = 0
        start_time = time.time()
        for i in range(NUM_MESSAGES_PER_TEST // NUM_CONCURRENT_CLIENTS):
            try:
                message = f"kafka_msg_{client_id}_{i}" + SAMPLE_MESSAGE
                future = producer.send(KAFKA_TOPIC, message.encode('utf-8'))
                _ = future.get(timeout=10)
                messages_sent += 1
            except Exception as e:
                errors += 1
                error_msg = f"Erro no Produtor Kafka (Cliente {client_id}): {e}"
                print(error_msg)
                if LOG_FILE_HANDLE: LOG_FILE_HANDLE.write(error_msg + "\n")
        end_time = time.time()
        record_metric("Kafka", f"Produtor (Cliente {client_id})", "Envio", start_time, end_time, messages_sent, errors)
    except NoBrokersAvailable:
        conn_error_msg = f"Produtor Kafka (Cliente {client_id}): Nenhum broker Kafka disponivel em {KAFKA_BOOTSTRAP_SERVERS}. O Kafka esta rodando?"
        print(conn_error_msg)
        if LOG_FILE_HANDLE: LOG_FILE_HANDLE.write(conn_error_msg + "\n")
    except Exception as e:
        conn_error_msg = f"Erro de Conexao do Produtor Kafka (Cliente {client_id}): {e}"
        print(conn_error_msg)
        if LOG_FILE_HANDLE: LOG_FILE_HANDLE.write(conn_error_msg + "\n")
    finally:
        if producer:
            producer.close()

def run_kafka_consumer(client_id, messages_to_consume):
    if not KafkaConsumer: return
    consumer = None
    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            group_id=f'test_group_{random.randint(0,9999)}',
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            consumer_timeout_ms=5000
        )
        messages_received = 0
        errors = 0
        start_time = time.time()
        for message in consumer:
            messages_received += 1
            if messages_received >= messages_to_consume:
                break
        end_time = time.time()
        record_metric("Kafka", f"Consumidor (Cliente {client_id})", "Recebimento", start_time, end_time, messages_received, errors)
    except NoBrokersAvailable:
        conn_error_msg = f"Consumidor Kafka (Cliente {client_id}): Nenhum broker Kafka disponivel em {KAFKA_BOOTSTRAP_SERVERS}. O Kafka esta rodando?"
        print(conn_error_msg)
        if LOG_FILE_HANDLE: LOG_FILE_HANDLE.write(conn_error_msg + "\n")
    except Exception as e:
        errors += 1
        error_msg = f"Erro no Consumidor Kafka (Cliente {client_id}): {e}"
        print(error_msg)
        if LOG_FILE_HANDLE: LOG_FILE_HANDLE.write(error_msg + "\n")
    finally:
        if consumer:
            consumer.close()

def test_kafka_scalability_and_stress():
    print("\n--- Rodando Testes Kafka ---")
    if LOG_FILE_HANDLE: LOG_FILE_HANDLE.write("\n--- Rodando Testes Kafka ---\n")
    producer_threads = []
    consumer_threads = []
    messages_per_consumer = NUM_MESSAGES_PER_TEST // NUM_CONCURRENT_CLIENTS

    for i in range(NUM_CONCURRENT_CLIENTS):
        consumer_thread = threading.Thread(target=run_kafka_consumer, args=(i, messages_per_consumer))
        consumer_threads.append(consumer_thread)
        consumer_thread.start()
    time.sleep(5)

    for i in range(NUM_CONCURRENT_CLIENTS):
        producer_thread = threading.Thread(target=run_kafka_producer, args=(i,))
        producer_threads.append(producer_thread)
        producer_thread.start()

    for t in producer_threads:
        t.join()
    for t in consumer_threads:
        t.join()
    print("--- Testes Kafka Finalizados ---\n")
    if LOG_FILE_HANDLE: LOG_FILE_HANDLE.write("--- Testes Kafka Finalizados ---\n\n")

# --- Resumo Final ---
def generate_final_summary():
    """
    Gera e imprime um resumo final dos testes, incluindo as metricas consolidadas.
    """
    summary_output = []
    summary_output.append("\n" + "="*50)
    summary_output.append("RESUMO FINAL DOS TESTES DE MIDDLEWARE")
    summary_output.append("="*50 + "\n")
    summary_output.append(f"Data e Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary_output.append(f"Numero de Clientes Concorrentes: {NUM_CONCURRENT_CLIENTS}")
    summary_output.append(f"Numero de Mensagens por Teste (Total): {NUM_MESSAGES_PER_TEST}\n")

    for middleware, data in GLOBAL_METRICS.items():
        summary_output.append(f"--- {middleware} ---")
        # Produtor
        prod_msg = data["produtor"]["mensagens"]
        prod_time = data["produtor"]["tempo"]
        prod_errors = data["produtor"]["erros"]
        prod_throughput = (prod_msg / prod_time) if prod_time > 0 else 0
        summary_output.append(f"  Produtor:")
        summary_output.append(f"    Total de Mensagens Enviadas: {prod_msg}")
        summary_output.append(f"    Tempo Total de Envio: {prod_time * 1000:.2f} ms")
        summary_output.append(f"    Throughput Medio (Envio): {prod_throughput:.2f} mensagens/segundo")
        summary_output.append(f"    Erros de Envio: {prod_errors}")

        # Consumidor
        cons_msg = data["consumidor"]["mensagens"]
        cons_time = data["consumidor"]["tempo"]
        cons_errors = data["consumidor"]["erros"]
        cons_throughput = (cons_msg / cons_time) if cons_time > 0 else 0
        summary_output.append(f"  Consumidor:")
        summary_output.append(f"    Total de Mensagens Recebidas: {cons_msg}")
        summary_output.append(f"    Tempo Total de Recebimento: {cons_time * 1000:.2f} ms")
        summary_output.append(f"    Throughput Medio (Recebimento): {cons_throughput:.2f} mensagens/segundo")
        summary_output.append(f"    Erros de Recebimento: {cons_errors}\n")
    
    summary_output.append("="*50 + "\n")

    for line in summary_output:
        print(line)
        if LOG_FILE_HANDLE:
            LOG_FILE_HANDLE.write(line + "\n")


# --- Execucao Principal ---
if __name__ == "__main__":
    # Define o nome do arquivo de log com base nas configuracoes
    log_filename = f"log_clientes_{NUM_CONCURRENT_CLIENTS}_mensagens_{NUM_MESSAGES_PER_TEST}.txt"

    # Abre o arquivo de log no inicio do script
    try:
        LOG_FILE_HANDLE = open(log_filename, "w", encoding="utf-8")
        print(f"Log do teste sera salvo em: {log_filename}\n")
        LOG_FILE_HANDLE.write(f"Inicio do Teste - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        LOG_FILE_HANDLE.write(f"Configuracao: Clientes Concorrentes={NUM_CONCURRENT_CLIENTS}, Mensagens por Teste={NUM_MESSAGES_PER_TEST}, Tamanho da Mensagem={MESSAGE_SIZE_BYTES} bytes\n")
        LOG_FILE_HANDLE.write(f"Redis Host: {REDIS_HOST}:{REDIS_PORT}\n")
        LOG_FILE_HANDLE.write(f"RabbitMQ Host: {RABBITMQ_HOST}:{RABBITMQ_PORT} | Usuario: {RABBITMQ_USERNAME}\n")
        LOG_FILE_HANDLE.write(f"Kafka Brokers: {', '.join(KAFKA_BOOTSTRAP_SERVERS)}\n\n")

    except IOError as e:
        print(f"Erro ao abrir o arquivo de log {log_filename}: {e}")
        LOG_FILE_HANDLE = None # Garante que o handle seja None se houver erro

    print("Este script ira realizar testes de escalabilidade e estresse em Redis, RabbitMQ e Kafka.")
    print("Por favor, garanta que estes servicos estejam rodando e acessiveis nos hosts/portas especificados.")
    print("Instale as bibliotecas Python necessarias: pip install redis pika kafka-python\n")

    test_redis_scalability_and_stress()
    test_rabbitmq_scalability_and_stress()
    test_kafka_scalability_and_stress()

    # Gera e salva o resumo final
    generate_final_summary()

    print("Todos os testes foram concluidos.")
    if LOG_FILE_HANDLE:
        LOG_FILE_HANDLE.write(f"Fim do Teste - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        LOG_FILE_HANDLE.close()
        print(f"Log salvo com sucesso em {log_filename}")