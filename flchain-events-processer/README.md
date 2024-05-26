# Process listening and forwarding events

### Set up RabbitMQ instance
* Run: `docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management`
* Login to RabbitMQ management console: `http://localhost:15672/` with username: `guest` and password: `guest`

### Set up pooling instance
This is the service responsible for pooling blockchain events and forwarding them via RabbitMQ to the chain participants. This service uses the generated `events_reader_client.py` script to read and decode events.
* Navigate to the `utils` directory and run: `python3 events-reader-generator.py` to generate the most updated version of the `events_reader_client.py` script. The generator reads the ABI file of the smart contract to provide the necessary methods for decoding each type of event. The events client script is created in the `flchain-events-processer` directory.
* Navigate back to the `flchain-events-processer` directory.
* Run the listener service with the following command: `python3 listener_service.py`. This acts as a dummy test listener, that in practice, would be replace by each participant's own implementation.
* Run the pooling service: `python3 pooling_service.py`, or set up a Docker container via the following commands:
  - `docker build -t pooling-service .`
  - `docker run -d --name pooling-service pooling-service`