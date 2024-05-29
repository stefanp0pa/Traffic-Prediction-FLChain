import json

ABI_SOURCE  = '/Users/stefan/Traffic-Prediction-FLChain/trafficflchain/output/trafficflchain.abi.json'
CLIENT_DEST = '/Users/stefan/Traffic-Prediction-FLChain/flchain-events-processer/events_reader_client.py'

EVENTS_SECTION = 'events'
IGNORED_EVENTS = ['SCUpgrade', 'writeLog', 'completedTxEvent', 'signalError', 'internalVMErrors']

def read_abi_file(file_path = ABI_SOURCE):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"The file {file_path} does not exist.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the file {file_path}.")
        exit(1)

def read_utils(file_path = "converts.py"):
    try:
        with open(file_path, 'r') as file:
            data = file.read()
            return data
    except FileNotFoundError:
        print(f"The utils file {file_path} does not exist.")
        exit(1)

def choose_decode_method(param_type):
    if param_type == 'u8':
        return 'base64_string_to_numeric'
    elif param_type == 'u16':
        return 'base64_string_to_numeric'
    elif param_type == 'u32':
        return 'base64_string_to_numeric'
    elif param_type == 'u64':
        return 'base64_string_to_numeric'
    elif param_type == 'Address':
        return 'base64_string_to_bech32_address'
    else:
        return 'base64_string_to_numeric'

abi_file_content = read_abi_file()
utils_methods = read_utils()
events_section = abi_file_content[EVENTS_SECTION]

with open(CLIENT_DEST, 'w') as file:
    print(f'[*] Started generating the client file at location {CLIENT_DEST}...')
    file.write("# CODE AUTOMATICALLY GENERATED BY events-reader-generator.py\n\n")
    file.write(utils_methods)
    file.write("\n\n")
    total_event_names = []
    for event in events_section:
        event_name = event['identifier']
        total_event_names.append(event_name)
        event_inputs = event['inputs']
        print(event_inputs)
        method_name = f"def read_{event_name}(payload):\n"
        file.write(method_name)
        file.write("\tevent_name = base64_string_to_string(payload[0])\n")
        for index, input in enumerate(event_inputs):
            input_name = input['name']
            input_type = input['type']
            file.write(f"\t{input_name} = {choose_decode_method(input_type)}(payload[{index + 1}])\n")
        
        file.write("\treturn json.dumps({")
        for input in event_inputs:
            input_name = input['name']
            file.write(f"'{input_name}': {input_name}, ")
        
        file.write("'identifier': event_name})\n")   
        file.write("\n\n")
    all_event_names = ',\n'.join([f"'{name}'" for name in total_event_names])
    file.write(f"event_names = [{all_event_names}]\n\n")
    file.write(f"ignore_events = {IGNORED_EVENTS}\n\n")
    
    file.write("def show_all_event_types():\n")
    file.write("\treturn event_names\n\n")
    
    file.write("def show_all_ignore_events():\n")
    file.write("\treturn ignore_events\n\n")
    
    file.write("def use_read_method(event_name):\n")
    file.write("\tevent_read_methods = {\n")
    for event_name in total_event_names:
        file.write(f"\t\t'{event_name}': read_{event_name},\n")
    file.write("\t}\n\n")
    file.write("\tif event_name in event_read_methods:\n")
    file.write("\t\treturn event_read_methods[event_name]\n")
    file.write("\telse:\n")
    file.write("\t\tprint(f\"Event {event_name} not found in available events.\")\n")
    file.write("\t\treturn None\n\n")
    
    file.write("def read_event_payload(event_name, payload):\n")
    file.write("\tread_method = use_read_method(event_name)\n")
    file.write("\treturn read_method(payload)\n")
    print(f'[*] Finished generating the client file at location {CLIENT_DEST}...')