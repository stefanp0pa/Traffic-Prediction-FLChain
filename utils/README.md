# Automatically-generated clients
This directory contains 2 scripts for generating client scrips that can interact with the SC:
- `sc-proxy-generator.py` - generates methods for interacting with all available SC endpoints
- `events-reader-generator.py` - generates methods for reading events from the SC in a pooling service

## How to use
1. Locate the ABI file of your SC, since this file contains all the necessary definitions for interacting with the SC.
2. Run either `python3 sc-proxy-generator.py` or `python3 events-reader-generator.py` to generate the client scripts at your desired location.
3. The former can be used for different clients that need direct interaction with the SC.
4. The latter can be used for services that need to read events from the SC, such as a pooling or listening service.