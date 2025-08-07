# dashboard/consumers.py
import json
import paho.mqtt.client as mqtt
import ssl
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync, sync_to_async
from channels.layers import get_channel_layer
from .models import Device, WaterReading
import os

# --- MQTT Setup ---
MQTT_SERVER = "a32641ary7fmuf-ats.iot.me-central-1.amazonaws.com"
MQTT_PORT = 8883
MQTT_WILDCARD_DATA_TOPIC = "devices/+/data"
MQTT_COMMAND_TOPIC_FORMAT = "devices/{}/commands"

# --- Global variable to hold our single MQTT client instance ---
mqtt_listener_client = None

# =================================================================
# --- This is the Web App's Brain (Your Dynamic Logic) ---
# =================================================================
@sync_to_async
def process_and_save_data(topic, payload_str):
    try:
        # Step 1: The web app reads the device_id from the topic.
        device_id = topic.split('/')[1]
        payload = json.loads(payload_str)
        
        # YOUR LOGIC: The web app automatically creates a device record if it's new.
        device, created = Device.objects.get_or_create(device_id=device_id)
        if created:
            print(f"AUTO-CREATED: New device '{device_id}' has connected and been added to the database.")

        # The web app saves the data, linking it to the correct device.
        WaterReading.objects.create(
            device=device,
            overhead_level=payload.get('overhead_level', 0),
            underground_level=payload.get('underground_level', 0),
            pump_status=payload.get('pump_status', False),
            pump_current=payload.get('pump_current', 0.0),
            system_status=payload.get('system_status', 'Unknown')
        )

        # ==========================================================
        # --- NEW: AUTOMATIC DATA DELETION LOGIC ---
        # ==========================================================
        DATA_LIMIT_PER_DEVICE = 150
        reading_count = WaterReading.objects.filter(device=device).count()

        if reading_count > DATA_LIMIT_PER_DEVICE:
            # Find the oldest reading for this specific device
            oldest_reading = WaterReading.objects.filter(device=device).order_by('timestamp').first()
            if oldest_reading:
                oldest_reading.delete()
                print(f"CLEANUP: Deleted oldest reading for device '{device_id}' to stay within the {DATA_LIMIT_PER_DEVICE} limit.")
        # ==========================================================
        
        # Only forward the message if an admin has assigned a user to this device.
        if device.owner:
            print(f"SUCCESS: Saved data for device '{device_id}' owned by '{device.owner}'.")
            return device_id, payload
        else:
            print(f"Data received for unassigned device '{device_id}'. Stored, but not forwarded.")
            return None, None

    except Exception as e:
        print(f"ERROR: Could not process message. Reason: {e}")
    return None, None

# This function runs when a message arrives from ANY device.
def on_message(client, userdata, msg):
    device_id, payload = async_to_sync(process_and_save_data)(msg.topic, msg.payload.decode())
    
    # If the device has an owner, the web app forwards the data to the correct user's browser.
    if device_id and payload:
        channel_layer = get_channel_layer()
        group_name = f"device_{device_id}"
        async_to_sync(channel_layer.group_send)(
            group_name,
            {"type": "device.message", "message": payload}
        )

# This function is called when the web app connects to AWS.
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("SUCCESS: Connected to MQTT Broker!")
        client.subscribe(MQTT_WILDCARD_DATA_TOPIC)
        print(f"--> Web App is now listening for data from all devices.")
    else:
        print(f"FAILED to connect Web App, return code {rc}")

# --- This class defines the Web App's fixed identity ---
class MqttClient:
    def __init__(self):
        # The web app has one, fixed ID ("the mail van").
        self.client = mqtt.Client(client_id="AquaGuard_Backend")
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        certs_dir = os.path.join(BASE_DIR, "certs")

        self.client.tls_set(
            ca_certs=os.path.join(certs_dir, "AmazonRootCA1.pem"),
            certfile=os.path.join(certs_dir, "1a5ab48e7acac2f748a8c8909a37455d8e5879f8500a32c119067bce43f67cc6-certificate.pem.crt"),
            keyfile=os.path.join(certs_dir, "1a5ab48e7acac2f748a8c8909a37455d8e5879f8500a32c119067bce43f67cc6-private.pem.key"),
            tls_version=ssl.PROTOCOL_TLSv1_2
        )

    def start(self):
        print("Web app is attempting to connect to AWS...")
        self.client.connect(MQTT_SERVER, MQTT_PORT, 60)
        self.client.loop_start()

# --- This function ensures we only ever have one connection to AWS ---
def get_mqtt_client():
    global mqtt_listener_client
    if mqtt_listener_client is None:
        mqtt_listener_client = MqttClient()
    return mqtt_listener_client

# --- This class handles the connection to the user's browser ---
class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return
        
        self.device_id = self.scope['url_route']['kwargs']['device_id']
        self.group_name = f'device_{self.device_id}'

        # Security Check: Does this user own this device?
        is_owner = await self.user_owns_device()
        if not is_owner:
            await self.close()
            return
        
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        command = data.get('command')
        
        if command in ["PUMP_ON", "PUMP_OFF"]:
            command_topic = MQTT_COMMAND_TOPIC_FORMAT.format(self.device_id)
            payload = json.dumps({"command": command})
            client_instance = get_mqtt_client()
            client_instance.client.publish(command_topic, payload)
            print(f"Web app sent command '{command}' to device '{self.device_id}'")

    async def device_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))

    @sync_to_async
    def user_owns_device(self):
        return Device.objects.filter(owner=self.user, device_id=self.device_id).exists()