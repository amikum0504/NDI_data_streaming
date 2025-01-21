# NDI_data_streaming

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
  
# Step 3: Python Script for Consuming Messages from Kafka server and post to WebEx.

  A Python script listens to messages on a Kafka bus and posts them as a specific user to a designated WebEx room for testing. You can extend this functionality by filtering messages for different rooms   or using a WebEx bot to handle the task. Learn more about WebEx API, bots, and integrations at https://developer.webex.com.
  
  Acquire a BEARER-TOKEN for accessing the WebEx API and the WebEx room ID where messages will be posted.
  
  -  To obtain the BEARER-TOKEN, refer to the steps outlined in the "Getting Started with the Webex API" guide: https://developer.webex.com/docs/getting-started
  -  To obtain the WebEx room ID:
        + Go to https://developer.webex.com/docs/api/v1/rooms/list-rooms
        + Use a personal access token; otherwise, all rooms will be retrieved.
        + Paste the access token generated in the previous step into the Bearer field.
        + You should see one or two rooms listed. Identify the room with the correct name and copy its ID into the room_id field within the Alertmanager configuration for WebEx.
          
  -  Alternatively to obtain the WebEx room ID you can also use the scrip $${\color{green}***get_webex_room_id.ipynb***}$$ uploaded on this respository.
    
  -  You can also create a bot to send message to your webex room.
      +  Go to: https://developer.webex.com/my-apps
      +  Create a new Bot
      +  (Re)generate Access Token: This the token you set in the credentials field of Alertmanager config for Webex
      +  Add the Bot to the Webex Space
          *  Go to People
          *  Add People
          *  Search the name of your Bot
            
  -  Utilize the <font color="green">BEARER-TOKEN</font> and <font color="green">ROOMID</font> obtained in the earlier steps in the python script $${\color{green}***consume_n_post.ipynb***}$$ to  stream alerts  to ur Webex space.
    

  
