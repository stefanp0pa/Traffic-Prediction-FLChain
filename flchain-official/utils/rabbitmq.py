import pika
import constants

def init_rabbit(queues, callbacks):
    try: 
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=constants.RABBITMQ_HOST))
        channel = connection.channel()
        channel.exchange_declare(exchange="flchain-events-exchange", exchange_type="direct")

        for index, queue in enumerate(queues):
            channel.queue_declare(queue=queue, exclusive=True)
            channel.queue_bind(exchange="flchain-events-exchange", queue=queue, routing_key="set_stage_event")
            channel.basic_consume( queue=queue, on_message_callback=callbacks[index], auto_ack=True,)

        channel.start_consuming()
    except pika.exceptions.AMQPConnectionError as e:
        print("RabbitMQ deconectat")
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error:{e}")