import multiprocessing
import os
import signal

def kill_current_process():
    os.kill(os.getpid(), signal.SIGTERM)

def worker(index, callback):
    callback(index)

def create_process(process_params, callback_child, callback_parent):
    processes = []

    for param in process_params:
        p = multiprocessing.Process(target=worker, args=(param, callback_child))
        processes.append(p)
        p.start()   
    
    for p in processes:
        p.join()

    callback_parent()