import base64

def base64_string_to_hex_string(encoded_string):
    decoded_bytes = base64.b64decode(encoded_string)
    hex_encoded = decoded_bytes.hex()
    return hex_encoded
    
def base64_string_to_string(encoded_string):
    decoded_bytes = base64.b64decode(encoded_string)
    decoded_string = decoded_bytes.decode('utf-8')
    return decoded_string

def hex_string_to_numeric(hex_string):
    numeric_value = int(hex_string, 16)
    return numeric_value

