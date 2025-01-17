# NDI_data_streaming

  Streaming NDI  data to Webex Space

  The Nexus Dashboard Insights service offers seamless integration with third-party applications, including Kafka, by streaming data to an existing Kafka bus. It utilizes a push mechanism to efficiently   transmit data, encoding messages in JSON format to ensure compatibility and ease of use.

  The data streamed by NDI can be retrieved from the Kafka server and can be posted to chat space of applications such as Webex Teams, enabling real-time alerting use cases tailored to customer needs.

# Step 1: Prerequisites for NDI Configuration with Kafka

  Before configuring Nexus Dashboard Insights (NDI) with Kafka, follow these steps to ensure you setup the Kafka server:

  Gain a general understanding of Kafka concepts, terminology, and configuration.
  Refer to the Kafka documentation https://kafka.apache.org/documentation/

  Set Up a Kafka Cluster.Ensure a Kafka cluster is configured and operational.
  You can use the Apache Kafka Quickstart Guide to set up a Kafka server : https://kafka.apache.org/quickstart

  The following example assumes a preconfigured Kafka server:
    Cluster: Single server
    Security: Authetication/No authentication 
    Broker IP and Port: 192.168.1.100:9093
    Topic Name: <Topic_Name>
    Ensure your Kafka setup aligns with these prerequisites before proceeding to the next step.
    
# Step 2:Configure NDI Message Bus

  Navigate to the System Settings tab on the Nexus Dashboard.
  Select Message Bus Configuration.
  Click Edit and provide your Kafka server details, including:
  Name
  IP Address
  Port
  Topic Name
  Authentication Mode
  
# Step 3: Python Script for Consuming Messages from Kafka server and Sending Them to WebEx.


  

  
