import os
import pika
import json
import base64
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("BEACONX_HOST")
port = os.getenv("BEACONX_PORT")
username = os.getenv("BEACONX_USER")
password = os.getenv("BEACONX_PASSWORD")
virtual_host = '/'

# Queue settings
queue_name = os.getenv("BEACONX_QUEUE")

def process_message(channel, method, properties, body):
    events = json.loads(body.decode('utf-8'))
    just_events = events.get('events', [])

    possible_events = ["start_session", "end_session", "signup"]

    for event in just_events:
        if event['identifier'] in possible_events:
            print(event['identifier'])
            print(event['topics'])

# Establishing a durable connection
credentials = pika.PlainCredentials(username, password)
parameters = pika.ConnectionParameters(host=host, port=port, virtual_host=virtual_host, credentials=credentials)
connection = pika.BlockingConnection(parameters)

try:
    # Creating a channel
    channel = connection.channel()

    # Start consuming messages from the queue
    channel.basic_consume(queue=queue_name, on_message_callback=process_message, auto_ack=True)

    print("Successfully connected to RabbitMQ and consuming messages from the queue.")

    # Continuously consume messages
    channel.start_consuming()

except Exception as e:
    print("Failed to connect to RabbitMQ:", str(e))

finally:
    # Close the connection
    connection.close()