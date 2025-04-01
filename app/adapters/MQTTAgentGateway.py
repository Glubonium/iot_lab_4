import json
from venv import logger
import paho.mqtt.client as mqtt

from app.interfaces.agent_gateway import AgentGateway

class MQTTAgentGateway(AgentGateway):
    """
    A concrete implementation of the AgentGateway using MQTT protocol.
    Connects to an MQTT broker, subscribes to topics, and handles messages.
    """
    
    def __init__(self, broker_host="localhost", broker_port=1883, topic="agent/data"):
        """
        Initialize the MQTT agent gateway.
        
        Parameters:
        broker_host (str): The hostname of the MQTT broker.
        broker_port (int): The port of the MQTT broker.
        topic (str): The MQTT topic to subscribe to.
        """
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.topic = topic
        self.client = None
        self.is_running = False

    def on_message(self, client, userdata, msg):
        """
        Handle incoming messages from the agent.
        
        Parameters:
        client: MQTT client instance.
        userdata: Any additional user data passed to the MQTT client.
        msg: The MQTT message received from the agent.
        """
        try:
            logger.debug(f"Client: {client}, Userdata: {userdata}")
            payload = msg.payload.decode("utf-8")
            logger.info(f"Received message on topic {msg.topic}: {payload}")

            try:
                data = json.loads(payload)
                logger.info(f"Parsed message data: {data}")
            except json.JSONDecodeError:
                logger.warning("Message payload is not valid JSON")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback for when the client receives a CONNACK response from the broker.
        
        Parameters:
        client: MQTT client instance.
        userdata: Any additional user data.
        flags: Response flags.
        rc: Result code indicating connection status.
        """
        if rc == 0:
            logger.debug(f"Client: {client}, Userdata: {userdata}, Flags: {flags}, RC: {rc}")
            logger.info("Connected to MQTT broker successfully")
            self.client.subscribe(self.topic)
            logger.info(f"Subscribed to topic: {self.topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker with code: {rc}")


    def on_disconnect(self, client, userdata, rc):
        """
        Callback for when the client disconnects from the broker.
        
        Parameters:
        client: MQTT client instance.
        userdata: Any additional user data.
        rc: Result code indicating disconnection status.
        """
        logger.debug(f"Client: {client}, Userdata: {userdata}, RC: {rc}")
        logger.info("Disconnected from MQTT broker")
        self.is_running = False

    def connect(self):
        """
        Establish a connection to the MQTT broker.
        """
        try:
            self.client = mqtt.Client()
            
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_message = self.on_message
            
            logger.info(f"Connecting to MQTT broker at {self.broker_host}:{self.broker_port}")
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
            
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            raise

    def start(self):
        """
        Start listening for messages from the agent.
        """
        if self.client is None:
            self.connect()
        
        try:
            logger.info("Starting MQTT message loop")
            self.is_running = True
            self.client.loop_start()
        except Exception as e:
            logger.error(f"Error starting message loop: {e}")
            self.is_running = False
            raise

    def stop(self):
        """
        Stop the agent gateway and clean up resources.
        """
        try:
            if self.is_running and self.client:
                logger.info("Stopping MQTT message loop")
                self.client.loop_stop()
                self.client.disconnect()
                self.is_running = False
                logger.info("MQTT client stopped and disconnected")
        except Exception as e:
            logger.error(f"Error stopping MQTT client: {e}")
        finally:
            self.client = None