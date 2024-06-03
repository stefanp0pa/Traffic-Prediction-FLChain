import pika
import time
import json
import random
import string

RABBITMQ_HOST = 'localhost'

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

WORKER_NAME = generate_random_string(10)

print(f' [*] Connecting to RabbitMQ as worker {WORKER_NAME}...')
time.sleep(3)

try:
    def network_setup_callback(ch, method, properties, body):
        try:
            payload = json.loads(body.decode())
            print(" [*] Received network setup event with payload: %s!" % payload)
            # ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(" [x] Could not retrieve network setup event with exception %s!" % e)
            # ch.basic_ack(delivery_tag=method.delivery_tag)
    
    def network_cleared_callback(ch, method, properties, body):
        try:
            payload = json.loads(body.decode())
            print(f" [*] Received network cleared event with payload: {payload}!")
            # ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(" [x] Could not retrieve network cleared event with exception %s!" % e)
            # ch.basic_ack(delivery_tag=method.delivery_tag)
    
    def data_batch_published_callback(ch, method, properties, body):
        try:
            payload = json.loads(body.decode())
            print(f" [*] Received data batch published event with payload: {payload}!")
            # ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(" [x] Could not retrieve data batch published event with exception %s!" % e)
            # ch.basic_ack(delivery_tag=method.delivery_tag)
    
    def signup_user_published_callback(ch, method, properties, body):
        try:
            payload = json.loads(body.decode())
            print(f" [*] Received signup_user event with payload: {payload}!")
            # ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(" [x] Could not retrieve signup_user event with exception %s!" % e)
            # ch.basic_ack(delivery_tag=method.delivery_tag)
    
    def user_cleared_published_callback(ch, method, properties, body):
        try:
            payload = json.loads(body.decode())
            print(f" [*] Received user_cleared event with payload: {payload}!")
            # ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(" [x] Could not retrieve user_cleared event with exception %s!" % e)
            # ch.basic_ack(delivery_tag=method.delivery_tag)
    
    def test_callback(ch, method, properties, body):
        try:
            payload = json.loads(body.decode())
            print(f" [*] Received user_cleared event with payload: {payload}!")
            # ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(" [x] Could not retrieve user_cleared event with exception %s!" % e)
        
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.exchange_declare(exchange="flchain-events-exchange", exchange_type="direct")
    
    queue_names = [
        f"{WORKER_NAME}-network_setup_event",
        f"{WORKER_NAME}-network_cleared_event",
        f"{WORKER_NAME}-data_batch_published_event",
        f"{WORKER_NAME}-signup_user_event",
        f"{WORKER_NAME}-user_cleared_event",
        f"{WORKER_NAME}-set_stage_eevent",
    ]
    
    channel.queue_declare(queue=queue_names[0], exclusive=True)
    channel.queue_declare(queue=queue_names[1], exclusive=True)
    channel.queue_declare(queue=queue_names[2], exclusive=True)
    channel.queue_declare(queue=queue_names[3], exclusive=True)
    channel.queue_declare(queue=queue_names[4], exclusive=True)
    channel.queue_declare(queue=queue_names[5], exclusive=True)
    
    channel.queue_bind(
        exchange="flchain-events-exchange", 
        queue=queue_names[0],
        routing_key="network_setup_event")
    channel.queue_bind(
        exchange="flchain-events-exchange", 
        queue=queue_names[1],
        routing_key="network_cleared_event")
    channel.queue_bind(
        exchange="flchain-events-exchange", 
        queue=queue_names[2],
        routing_key="data_batch_published_event")
    channel.queue_bind(
        exchange="flchain-events-exchange", 
        queue=queue_names[3],
        routing_key="signup_user_event")
    channel.queue_bind(
        exchange="flchain-events-exchange", 
        queue=queue_names[4],
        routing_key="user_cleared_event")
    channel.queue_bind(
        exchange="flchain-events-exchange", 
        queue=queue_names[5],
        routing_key="set_stage_event")
    
    channel.basic_consume(
        queue=queue_names[0],
        on_message_callback=network_setup_callback,
        auto_ack=True,
    )
    channel.basic_consume(
        queue=queue_names[1],
        on_message_callback=network_cleared_callback,
        auto_ack=True,
    )
    channel.basic_consume(
        queue=queue_names[2],
        on_message_callback=data_batch_published_callback,
        auto_ack=True,
    )
    channel.basic_consume(
        queue=queue_names[3],
        on_message_callback=signup_user_published_callback,
        auto_ack=True,
    )
    channel.basic_consume(
        queue=queue_names[4],
        on_message_callback=user_cleared_published_callback,
        auto_ack=True,
    )
    channel.basic_consume(
        queue=queue_names[5],
        on_message_callback=test_callback,
        auto_ack=True,
    )
    
    print(' [*] Connected to RabbitMQ successfully!')
    print(' [*] Waiting for messages.')
    channel.start_consuming()
except:
    print(' [*] Connection to RabbitMQ failed! Exiting...')
    time.sleep(5)
    exit(1)
