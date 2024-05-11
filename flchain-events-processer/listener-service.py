import pika
import time
import json
import random
import string

# time.sleep(15)

RABBITMQ_HOST = 'localhost'

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

WORKER_NAME = generate_random_string(10)

print(' [*] Connecting to RabbitMQ...')

for i in range(0, 3):
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
            
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.exchange_declare(exchange="flchain-events-exchange", exchange_type="direct")
        
        queue_names = [
            f"{WORKER_NAME}-network_setup_event",
            f"{WORKER_NAME}-network_cleared_event",
            f"{WORKER_NAME}-data_batch_published_event"
        ]
        
        channel.queue_declare(queue=queue_names[0], exclusive=True)
        channel.queue_declare(queue=queue_names[1], exclusive=True)
        channel.queue_declare(queue=queue_names[2], exclusive=True)
        
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
        
        print(' [*] Connected to RabbitMQ successfully!')
        print(' [*] Waiting for messages.')
        channel.start_consuming()
    except:
        print(' [*] Connection to RabbitMQ failed! Retrying one more time...')
        time.sleep(5)
        continue
    break
