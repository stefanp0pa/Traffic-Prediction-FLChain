import pika
import constants
import json
from functools import partial
from utils.utils import generate_random_string

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


def stage_callback(participant_id, stages_dict, ch, method, properties, body):
        try:
            payload = json.loads(body.decode())
            payload = json.loads(payload)
            if payload['identifier'] == 'set_stage_event':
                stage = payload['stage']
                if stage not in stages_dict:
                    print(f"Stage:{stage} is not available for trainer mode")
                    return
                stages_dict[stage](participant_id)
        
        except Exception as e:
            print(f"Error: {e}")


def setup_rabbit(participant_id, stages_dict):
    WORKER_NAME = generate_random_string(10)
    queues_name = [f"{WORKER_NAME}-set_stage_event"]
    callbacks = [partial(stage_callback, participant_id, stages_dict)]
    init_rabbit(queues=queues_name, callbacks=callbacks)

   

  