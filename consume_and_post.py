from kafka import KafkaConsumer, TopicPartition
from json import loads, JSONDecodeError
import requests
import json
import sys

# Kafka Consumer Configuration
KAFKA_BROKER = '1.1.1.1:9092'  # Replace with your Kafka IP and port
KAFKA_TOPIC = 'topic'         # Replace with your Kafka topic
KAFKA_GROUP_ID = 'my-group'

# Webex API Configuration
WEBEX_API_URL = "https://webexapis.com/v1/messages"
WEBEX_ACCESS_TOKEN = 'Bearer your_Webex_API_Token'  # Replace with your Webex API token
WEBEX_ROOM_ID = 'your_webex_room_id'  # Replace with your Webex Room ID

# Webex Headers
headers = {
    'Authorization': WEBEX_ACCESS_TOKEN,
    'Content-Type': 'application/json'
}

# Initialize Kafka Consumer
consumer = KafkaConsumer(
    bootstrap_servers=[KAFKA_BROKER],
    auto_offset_reset='earliest',  # Start reading from the beginning
    enable_auto_commit=True,  # Automatically commit offsets
    group_id=KAFKA_GROUP_ID,
    value_deserializer=lambda x: x.decode('utf-8', errors='ignore') if x else None,
    consumer_timeout_ms=10000  # Exit if no messages are received within 10 seconds, if you want continuous monitoring and want the code to run nonstop remove this line
)

print("Kafka Consumer initialized. Waiting for messages...")

try:
    # Manually assign partitions
    partitions = consumer.partitions_for_topic(KAFKA_TOPIC)
    if partitions:
        print("Partitions available:", partitions)
        topic_partitions = [TopicPartition(KAFKA_TOPIC, p) for p in partitions]
        consumer.assign(topic_partitions)
        consumer.seek_to_beginning()  # Start from the beginning of the topic and will post entire Topic's content, 
                                      # If you want to consume only latest alert replace it with "consumer.seek_to_end()"
    else:
        print("No partitions found for the topic. Exiting...")
        consumer.close()
        sys.exit()

    # Consume messages from Kafka and post to Webex
    for msg in consumer:
        # Check for empty messages
        if not msg.value:
            print("Received an empty message.")
            continue

        try:
            # Attempt to parse the message as JSON
            message = loads(msg.value)
            print(f"Received JSON message from partition {msg.partition}, offset {msg.offset}:")
            print(message)

            # Prepare Webex message payload
            payload_message = (
                f"Fabric={message['fabricName']}, "
                f"Category={message['category']}, "
                f"Type={message['anomalyType']}, "
                f"Object={message['entityName']}, "
                f"Description={message['description']}"
                f"Node={message['nodeNames']}"
                f"Cleared={message['cleared']}"
            )
            payload = {
                "roomId": WEBEX_ROOM_ID,
                "text": payload_message
            }

            # Post message to Webex
            response = requests.post(WEBEX_API_URL, headers=headers, json=payload)

            # Check for success
            if response.status_code == 200:
                print(f"Message posted successfully to Webex: {payload_message}")
            else:
                print(f"Failed to post to Webex. Status: {response.status_code}, Response: {response.text}")

        except JSONDecodeError as e:
            print(f"Failed to parse message from partition {msg.partition}, offset {msg.offset}: {msg.value}. Error: {e}")
        except KeyError as e:
            print(f"Missing key in message: {e}")

except Exception as e:
    print(f"Error while consuming messages: {e}")
finally:
    # Ensure the consumer is closed properly
    consumer.close()
    print("Consumer closed.")
