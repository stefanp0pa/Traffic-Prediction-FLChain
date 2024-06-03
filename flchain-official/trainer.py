import sys
from utils.utils import generate_random_string
import constants
import pika
import json
from utils.rabbitmq import init_rabbit

trainer_id = sys.argv[1]
WORKER_NAME = generate_random_string(10)

def train_model():
    print("Incepe antrenamentul bobita")


def stage_callback(ch, method, properties, body):
    try:
        payload = json.loads(body.decode())
        payload = json.loads(payload)
        if payload['identifier'] == 'set_stage_event':
            stage = payload['stage']
            if stage not in stages_dict:
                print(f"Stage:{stage} is not available for trainer mode")
                return
            stages_dict[stage]()
    
    except Exception as e:
        print(f"Error: {e}")


def setup_queue():
    queues_name = [f"{WORKER_NAME}-set_stage_event"]
    callbacks = [stage_callback]
    init_rabbit(queues=queues_name, callbacks=callbacks)


if __name__ == "__main__":
    stages_dict = {
        3:train_model
    }
    setup_queue()