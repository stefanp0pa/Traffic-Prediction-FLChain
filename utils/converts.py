from bech32 import bech32_encode, convertbits
import base64
import json

def hex_string_to_bech32_address(hex_str, hrp = 'erd'):
    hex_bytes = bytes.fromhex(hex_str.rstrip('\x00'))
    data = convertbits(hex_bytes, 8, 5)
    bech32_str = bech32_encode(hrp, data)
    return bech32_str
    
def base64_string_to_string(encoded_string):
    if not encoded_string:
        return 0
    decoded_bytes = base64.b64decode(encoded_string.rstrip('\x00'))
    decoded_string = decoded_bytes.decode('utf-8')
    return decoded_string

def hex_string_to_numeric(hex_string):
    if not hex_string:
        return 0
    numeric_value = int(hex_string.rstrip('\x00'), 16)
    return numeric_value

def base64_string_to_hex_string(encoded_string):
    if not encoded_string:
        return 0
    decoded_bytes = base64.b64decode(encoded_string.rstrip('\x00'))
    hex_encoded = decoded_bytes.hex()
    return hex_encoded

def base64_string_to_numeric(encoded_string):
    if not encoded_string:
        return 0
    decoded_bytes = base64_string_to_hex_string(encoded_string)
    numeric_value = hex_string_to_numeric(decoded_bytes)
    return numeric_value

def base64_string_to_bech32_address(encoded_string):
    decoded_bytes = base64_string_to_hex_string(encoded_string)
    bech32_address = hex_string_to_bech32_address(decoded_bytes)
    return bech32_address
