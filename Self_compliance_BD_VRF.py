from kafka import KafkaConsumer, TopicPartition
from json import loads, JSONDecodeError
import requests
import json
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ----------------------------- CONFIGURATION -----------------------------

# Kafka Configuration
KAFKA_BROKER = 'X.X.X.X:9092'
KAFKA_TOPIC = '<your_topic>'
KAFKA_GROUP_ID = '<your_group>'

# Webex Configuration
ENABLE_WEBEX_ALERT = True
WEBEX_API_URL = "https://webexapis.com/v1/messages"
WEBEX_ACCESS_TOKEN = 'Bearer <you_token>'
WEBEX_ROOM_ID = '<your_room_id>'
webex_headers = {
    'Authorization': WEBEX_ACCESS_TOKEN,
    'Content-Type': 'application/json'
}

# APIC Credentials
APIC_HOST = "https://X.X.X.X"
APIC_USER = "<username>"
APIC_PASS = "<password>"

# ------------------------------------------------------------------------

def post_to_webex(message_text):
    payload = {
        "roomId": WEBEX_ROOM_ID,
        "text": message_text
    }
    response = requests.post(WEBEX_API_URL, headers=webex_headers, json=payload)
    if response.status_code == 200:
        print("✅ Webex message posted successfully.")
    else:
        print(f"❌ Failed to post Webex message. Status: {response.status_code}, Response: {response.text}")

def login_to_apic():
    login_url = f"{APIC_HOST}/api/aaaLogin.json"
    payload = {
        "aaaUser": {
            "attributes": {
                "name": APIC_USER,
                "pwd": APIC_PASS
            }
        }
    }
    try:
        response = requests.post(login_url, json=payload, verify=False)
        if response.status_code == 200:
            return response.cookies
        else:
            print(f"❌ APIC login failed. Status: {response.status_code}, Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception during APIC login: {e}")
        return None

def patch_bd_setting(cookies, dn):
    patch_url = f"{APIC_HOST}/api/mo/{dn}.json"
    payload = {
        "fvBD": {
            "attributes": {
                "unkMacUcastAct": "flood"  # Change if needed
            }
        }
    }
    try:
        response = requests.post(patch_url, cookies=cookies, json=payload, verify=False)
        if response.status_code == 200:
            print(f"✅ Successfully remediated BD: {dn}")
        else:
            print(f"❌ Failed to remediate BD: {dn}. Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"❌ Exception while patching BD {dn}: {e}")

def patch_vrf_enforcement(cookies, dn):
    patch_url = f"{APIC_HOST}/api/mo/{dn}.json"
    payload = {
        "fvCtx": {
            "attributes": {
                "pcEnfPref": "enforced"
            }
        }
    }
    try:
        response = requests.post(patch_url, cookies=cookies, json=payload, verify=False)
        if response.status_code == 200:
            print(f"✅ Successfully enforced VRF: {dn}")
        else:
            print(f"❌ Failed to enforce VRF: {dn}. Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"❌ Exception while patching VRF {dn}: {e}")

def fix_compliance_violation(message):
    cookies = login_to_apic()
    if not cookies:
        print("⚠️ Skipping remediation due to APIC login failure.")
        return

    bds_fixed = 0
    vrfs_fixed = 0

    for obj in message.get('anomalyObjectsList', []):
        obj_type = obj.get('objectType')
        dn = obj.get('identifier')

        if obj_type == 'bd':
            patch_bd_setting(cookies, dn)
            bds_fixed += 1

        elif obj_type == 'vrf':
            patch_vrf_enforcement(cookies, dn)
            vrfs_fixed += 1

    if ENABLE_WEBEX_ALERT:
        text = f"🔧 Auto-remediated {bds_fixed} BD(s) and {vrfs_fixed} VRF(s) in fabric: {message.get('fabricName')}"
        post_to_webex(text)

# ----------------------------- MAIN CONSUMER -----------------------------

consumer = KafkaConsumer(
    bootstrap_servers=[KAFKA_BROKER],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id=KAFKA_GROUP_ID,
    value_deserializer=lambda x: x.decode('utf-8', errors='ignore') if x else None,
)

print("📥 Kafka Consumer initialized. Waiting for compliance anomalies...")

try:
    partitions = consumer.partitions_for_topic(KAFKA_TOPIC)
    if partitions:
        topic_partitions = [TopicPartition(KAFKA_TOPIC, p) for p in partitions]
        consumer.assign(topic_partitions)
        consumer.seek_to_end()
    else:
        print("❌ No partitions found. Exiting.")
        sys.exit()

    for msg in consumer:
        if not msg.value:
            continue

        try:
            message = loads(msg.value)

            # Build alert message for Webex
            webex_text = (
                f"🔔 Alert from Fabric: {message.get('fabricName')}\n"
                f"• Category: {message.get('category')}\n"
                f"• Type: {message.get('anomalyType')}\n"
                f"• Object: {message.get('entityName')}\n"
                f"• Description: {message.get('description')}\n"
                f"• Nodes: {', '.join(message.get('nodeNames', []))}\n"
                f"• Severity: {message.get('severity')}"
            )

            # Always post to Webex first
            if ENABLE_WEBEX_ALERT:
                if (
                    message.get("category") == "COMPLIANCE" and
                    message.get("anomalyType") == "CONFIGURATION_COMPLIANCE_VIOLATED"
                ):
                    webex_text += "\n\n⚙️ *Auto-remediation is being triggered for affected objects...*"
                post_to_webex(webex_text)

            # Trigger remediation if needed
            if (
                message.get("category") == "COMPLIANCE" and
                message.get("anomalyType") == "CONFIGURATION_COMPLIANCE_VIOLATED"
            ):
                fix_compliance_violation(message)
            else:
                print(f"Ignored non-compliance alert at offset {msg.offset}")

        except JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
        except Exception as e:
            print(f"❌ General exception: {e}")

except Exception as e:
    print(f"❌ Error in Kafka consumption: {e}")
finally:
    consumer.close()
    print("🛑 Kafka Consumer closed.")
