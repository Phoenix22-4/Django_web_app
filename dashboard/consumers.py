# dashboard/consumers.py
import json
import paho.mqtt.client as mqtt
import ssl
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync, sync_to_async
from channels.layers import get_channel_layer
from .models import Device, WaterReading, AutomationRule
import os
from django.utils import timezone
from datetime import datetime

# --- MQTT Setup ---
MQTT_SERVER = "a32641ary7fmuf-ats.iot.me-central-1.amazonaws.com"
MQTT_PORT = 8883 # This is the standard MQTT port, but we will use 443 for WebSockets
MQTT_WILDCARD_DATA_TOPIC = "devices/+/data"
MQTT_COMMAND_TOPIC_FORMAT = "devices/{}/commands"

mqtt_listener_client = None
mqtt_connection_attempts = 0
MAX_CONNECTION_ATTEMPTS = 5

# --- Helper function to send commands ---
def send_pump_command(device_id, command):
    command_topic = MQTT_COMMAND_TOPIC_FORMAT.format(device_id)
    payload = json.dumps({"command": command})
    client_instance = get_mqtt_client()
    client_instance.client.publish(command_topic, payload)
    print(f"Web app sent command '{command}' to device '{device_id}'")

# --- This is the Web App's Brain (Your Dynamic Logic) ---
@sync_to_async
def process_and_save_data(topic, payload_str):
    try:
        device_id = topic.split('/')[1]
        payload = json.loads(payload_str)
        
        print(f"📡 AWS IoT Data Received from device '{device_id}'")
        print(f"📊 Data: {payload}")
        
        device, created = Device.objects.get_or_create(device_id=device_id)
        if created:
            print(f"✅ AUTO-CREATED: New device '{device_id}' has connected and been added to the database.")
        else:
            print(f"🔄 Device '{device_id}' already exists, updating data...")

        # --- MODIFIED: Save new dynamic data format ---
        reading = WaterReading.objects.create(
            device=device,
            tank_data=payload.get('tanks', []), # Expects [{"name": "Tank 1", "level": 80}]
            pump_status=payload.get('pump_status', False),
            pump_current_amps=payload.get('pump_current_amps', 0.0)
        )
        
        print(f"💾 Data saved successfully for device '{device_id}' - Reading ID: {reading.id}")

        # --- DATA DELETION LOGIC (from old file) ---
        DATA_LIMIT_PER_DEVICE = 150
        reading_count = WaterReading.objects.filter(device=device).count()
        if reading_count > DATA_LIMIT_PER_DEVICE:
            oldest_reading = WaterReading.objects.filter(device=device).order_by('timestamp').first()
            if oldest_reading:
                oldest_reading.delete()

        # --- NEW: ADVANCED PUMP & AUTOMATION LOGIC ---
        now_time = timezone.now().time()
        active_rule = AutomationRule.objects.filter(
            device=device,
            enabled=True,
            start_time__lte=now_time,
            end_time__gte=now_time
        ).first()

        automation_mode_message = "System Auto-Mode"
        pump_should_be_on = payload.get('pump_status', False) # Default to current status

        if active_rule:
            # User timeslot is active. Use its logic.
            current_level = -1
            for tank in payload.get('tanks', []):
                if tank['name'] == active_rule.monitor_tank_name:
                    current_level = tank['level']
                    break
            
            if current_level != -1:
                automation_mode_message = f"Timeslot Active ({active_rule.name}): ON at {active_rule.min_level}%, OFF at {active_rule.max_level}%"
                
                if current_level < active_rule.min_level:
                    pump_should_be_on = True
                elif current_level > active_rule.max_level:
                    pump_should_be_on = False
                
        else:
            # No active rule. Use default system logic.
            # Example: fill overhead from underground
            overhead_level = -1
            underground_level = -1
            for tank in payload.get('tanks', []):
                if 'overhead' in tank['name'].lower():
                    overhead_level = tank['level']
                if 'underground' in tank['name'].lower():
                    underground_level = tank['level']

            if overhead_level != -1 and underground_level != -1:
                if overhead_level < 20 and underground_level > 10: # Min levels
                    pump_should_be_on = True
                elif overhead_level > 95: # Max level
                    pump_should_be_on = False
        
        # --- Send command ONLY if the state needs to change ---
        if device.pump_present and pump_should_be_on != payload.get('pump_status'):
            send_pump_command(device_id, 'PUMP_ON' if pump_should_be_on else 'PUMP_OFF')

        # Add the automation status to the payload
        payload['automation_mode'] = automation_mode_message
        
        # Forward data regardless of owner assignment (for admin monitoring)
        if device.owner:
            print(f"SUCCESS: Saved data for device '{device_id}' owned by '{device.owner.username}'.")
        else:
            print(f"Data received for unassigned device '{device_id}'. Stored and available for admin assignment.")
        
        return device_id, payload

    except Exception as e:
        print(f"ERROR: Could not process message. Reason: {e}")
    return None, None

# --- MQTT Callbacks ---
def on_connect(client, userdata, flags, rc, properties=None):
    global mqtt_connection_attempts
    
    try:
        if rc == 0:
            print("🔗 MQTT Successfully connected to AWS IoT Core!")
            print(f"📡 Subscribed to topic: {MQTT_WILDCARD_DATA_TOPIC}")
            print("✅ Ready to receive data from devices...")
            client.subscribe(MQTT_WILDCARD_DATA_TOPIC)
            mqtt_connection_attempts = 0  # Reset counter on successful connection
        else:
            mqtt_connection_attempts += 1
            print(f"❌ MQTT Connection failed with result code {rc} (attempt {mqtt_connection_attempts}/{MAX_CONNECTION_ATTEMPTS})")
            
            # Common error codes
            error_messages = {
                1: "Connection refused - incorrect protocol version",
                2: "Connection refused - invalid client identifier", 
                3: "Connection refused - server unavailable",
                4: "Connection refused - bad username or password",
                5: "Connection refused - not authorised"
            }
            if rc in error_messages:
                print(f"💡 Error details: {error_messages[rc]}")
                
            if mqtt_connection_attempts >= MAX_CONNECTION_ATTEMPTS:
                print("🛑 Maximum connection attempts reached. Stopping reconnection attempts.")
                print("🔧 Please check your AWS IoT Core configuration and certificates.")
                # Stop the client to prevent endless reconnection attempts
                try:
                    client.loop_stop()
                    client.disconnect()
                except:
                    pass
    except Exception as e:
        print(f"❌ MQTT on_connect error: {e}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        # Detailed error messages for common disconnect codes
        error_messages = {
            1: "Connection refused - incorrect protocol version",
            2: "Connection refused - invalid client identifier", 
            3: "Connection refused - server unavailable",
            4: "Connection refused - bad username or password",
            5: "Connection refused - not authorised",
            6: "Connection refused - not authorised (certificate issue)",
            7: "Connection refused - not authorised (policy/permission issue)"
        }
        
        error_msg = error_messages.get(rc, f"Unknown error code {rc}")
        print(f"⚠️ MQTT Disconnection (rc={rc}): {error_msg}")
        
        if rc in [5, 6, 7]:
            print("🔍 Authentication/Authorization issue detected!")
            print("💡 Possible causes:")
            print("   - Certificate files missing or corrupted")
            print("   - AWS IoT Core policy doesn't allow this connection")
            print("   - Certificate has expired")
            print("   - Wrong AWS IoT Core endpoint")
            print("   - Device not registered in AWS IoT Core")
    else:
        print("🔌 MQTT Disconnected normally")

# This function runs when a message arrives from ANY device.
def on_message(client, userdata, msg):
    print(f"📨 Message received from topic: {msg.topic}")
    device_id, payload = async_to_sync(process_and_save_data)(msg.topic, msg.payload.decode())
    
    if device_id and payload:
        channel_layer = get_channel_layer()
        group_name = f"device_{device_id}"
        async_to_sync(channel_layer.group_send)(
            group_name,
            {"type": "device.message", "message": payload}
        )

# --- Add this function for debugging ---
def on_log(client, userdata, level, buf):
    print(f"MQTT DEBUG LOG: {buf}")


class MqttClient:
    def __init__(self):
        # Use standard MQTT over TLS (more reliable than WebSockets)
        self.client = mqtt.Client(client_id="AquaGuard_Backend")
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.on_disconnect = on_disconnect
        self.client.on_log = on_log
        
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        certs_dir = os.path.join(BASE_DIR, "certs")

        # Check if certificate files exist
        ca_cert = os.path.join(certs_dir, "AmazonRootCA1.pem")
        device_cert = os.path.join(certs_dir, "7355e09287fa3fab0fbd2c16eaee80bedd61b592e42dd5b6697f59c2de643149-certificate.pem.crt")
        device_key = os.path.join(certs_dir, "7355e09287fa3fab0fbd2c16eaee80bedd61b592e42dd5b6697f59c2de643149-private.pem.key")
        
        if not all(os.path.exists(f) for f in [ca_cert, device_cert, device_key]):
            print("❌ Certificate files missing:")
            for cert_file, path in [("CA Certificate", ca_cert), ("Device Certificate", device_cert), ("Device Key", device_key)]:
                if not os.path.exists(path):
                    print(f"   - {cert_file}: {path}")
            raise FileNotFoundError("Required certificate files are missing")
        
        # Check certificate file sizes (basic validation)
        for cert_file, path in [("CA Certificate", ca_cert), ("Device Certificate", device_cert), ("Device Key", device_key)]:
            file_size = os.path.getsize(path)
            if file_size < 100:  # Certificates should be at least 100 bytes
                print(f"⚠️ Warning: {cert_file} seems too small ({file_size} bytes): {path}")
            else:
                print(f"✅ {cert_file} found ({file_size} bytes): {path}")

        # Configure TLS for secure connection
        self.client.tls_set(
            ca_certs=ca_cert,
            certfile=device_cert,
            keyfile=device_key,
            tls_version=ssl.PROTOCOL_TLSv1_2
        )

    def start(self):
        print("Web app is attempting to connect to AWS IoT Core...")
        
        try:
            # Use standard MQTT port 8883 with TLS
            self.client.connect(MQTT_SERVER, MQTT_PORT, 60)
            print("✅ MQTT connection initiated successfully")
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"❌ FATAL: MQTT connection failed: {e}")
            print("🔍 Check your certificates and network connectivity")
            print("📋 Troubleshooting steps:")
            print("   1. Verify certificate files exist in /certs/ directory")
            print("   2. Check AWS IoT Core endpoint is correct")
            print("   3. Ensure device certificates are valid and not expired")
            print("   4. Verify network connectivity to AWS IoT Core")
            return False

# --- This function ensures we only ever have one connection to AWS ---
def get_mqtt_client():
    global mqtt_listener_client
    if mqtt_listener_client is None:
        print("🔧 Creating new MQTT client instance...")
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
            # Use the helper function to send commands
            send_pump_command(self.device_id, command)

    async def device_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))

    @sync_to_async
    def user_owns_device(self):
        # Also allow superusers to connect to any device
        if self.user.is_superuser:
            return Device.objects.filter(device_id=self.device_id).exists()
        return Device.objects.filter(owner=self.user, device_id=self.device_id).exists()