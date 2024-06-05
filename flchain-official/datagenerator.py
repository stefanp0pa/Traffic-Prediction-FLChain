import torch
import os
import json
import sys
from utils.utils import generate_random_string
from utils.rabbitmq import init_rabbit

torch.cuda.device_count()
torch.cuda.is_available()
os.environ["CUDA_VISIBLE_DEVICES"] = '3'
USE_CUDA = torch.cuda.is_available()
DEVICE = torch.device('cuda:0')
print("CUDA:", USE_CUDA, DEVICE)

data_agregator_id = int(sys.argv[1])
WORKER_NAME = generate_random_string(10)

def agregate_model():
    print("Start agregate models bitch")


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
        4:agregate_model
    }
    setup_queue()