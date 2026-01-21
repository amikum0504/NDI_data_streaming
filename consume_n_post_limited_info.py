from kafka import KafkaConsumer, TopicPartition
from json import loads, JSONDecodeError
import requests
import sys
import os
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables from .env file
load_dotenv()

# ----------------------------- CONFIGURATION -----------------------------

# Kafka Consumer Configuration
KAFKA_BROKER = os.getenv('KAFKA_BROKER', '10.76.92.105:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'amikum1')
KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'my-group')

# Webex API Configuration
WEBEX_API_URL = "https://webexapis.com/v1/messages"
WEBEX_ACCESS_TOKEN = os.getenv('WEBEX_ACCESS_TOKEN', '')
WEBEX_ROOM_ID = os.getenv('WEBEX_ROOM_ID', '')

if not WEBEX_ACCESS_TOKEN or not WEBEX_ROOM_ID:
    print("⚠️ WARNING: Webex credentials not found in environment variables!")

# Webex Headers
webex_headers = {
    'Authorization': WEBEX_ACCESS_TOKEN,
    'Content-Type': 'application/json'
}

# ------------------------------------------------------------------------

# Initialize Kafka Consumer
consumer = KafkaConsumer(
    bootstrap_servers=[KAFKA_BROKER],
    auto_offset_reset='earliest',  # Start reading from the beginning
    enable_auto_commit=True,  # Automatically commit offsets
    group_id=KAFKA_GROUP_ID,
    value_deserializer=lambda x: x.decode('utf-8', errors='ignore') if x else None,
)

print("📥 Kafka Consumer initialized. Waiting for messages...")

try:
    # Manually assign partitions
    partitions = consumer.partitions_for_topic(KAFKA_TOPIC)
    if partitions:
        print(f"✅ Partitions available: {partitions}")
        topic_partitions = [TopicPartition(KAFKA_TOPIC, p) for p in partitions]
        consumer.assign(topic_partitions)
        consumer.seek_to_end()  # Start from the end of the topic
    else:
        print("❌ No partitions found for the topic. Exiting...")
        consumer.close()
        sys.exit()

    # Consume messages from Kafka and post to Webex
    for msg in consumer:
        # Check for empty messages
        if not msg.value:
            print("⚠️ Received an empty message.")
            continue

        try:
            # Attempt to parse the message as JSON
            message = loads(msg.value)
            print(f"📨 Received JSON message from partition {msg.partition}, offset {msg.offset}")

            # Prepare Webex message payload with better formatting
            payload_message = (
                f"🔔 Alert from Fabric: {message.get('fabricName', 'Unknown')}\n"
                f"• Category: {message.get('category', 'N/A')}\n"
                f"• Type: {message.get('anomalyType', 'N/A')}\n"
                f"• Object: {message.get('entityName', 'N/A')}\n"
                f"• Description: {message.get('description', 'N/A')}\n"
                f"• Nodes: {', '.join(message.get('nodeNames', []))}\n"
                f"• Cleared: {message.get('cleared', 'N/A')}"
            )
            
            payload = {
                "roomId": WEBEX_ROOM_ID,
                "text": payload_message
            }

            # Post message to Webex
            response = requests.post(WEBEX_API_URL, headers=webex_headers, json=payload)

            # Check for success
            if response.status_code == 200:
                print(f"✅ Message posted successfully to Webex")
            else:
                print(f"❌ Failed to post to Webex. Status: {response.status_code}, Response: {response.text}")

        except JSONDecodeError as e:
            print(f"❌ JSON decode error at partition {msg.partition}, offset {msg.offset}: {e}")
        except KeyError as e:
            print(f"❌ Missing key in message: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

except Exception as e:
    print(f"❌ Error while consuming messages: {e}")
finally:
    # Ensure the consumer is closed properly
    consumer.close()
    print("🛑 Consumer closed.")
