from django.core.management.base import BaseCommand
import os
import ssl
import paho.mqtt.client as mqtt
from datetime import datetime

class Command(BaseCommand):
    help = 'Test MQTT connection to AWS IoT Core and diagnose issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed connection information',
        )

    def handle(self, *args, **options):
        self.stdout.write("🔍 Testing MQTT connection to AWS IoT Core...")
        
        # Configuration
        MQTT_SERVER = "a2hspl06jd48n2-ats.iot.me-central-1.amazonaws.com"
        MQTT_PORT = 8883
        
        # Check certificate files
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        certs_dir = os.path.join(BASE_DIR, "certs")
        
        ca_cert = os.path.join(certs_dir, "AmazonRootCA1.pem")
        device_cert = os.path.join(certs_dir, "7355e09287fa3fab0fbd2c16eaee80bedd61b592e42dd5b6697f59c2de643149-certificate.pem.crt")
        device_key = os.path.join(certs_dir, "7355e09287fa3fab0fbd2c16eaee80bedd61b592e42dd5b6697f59c2de643149-private.pem.key")
        
        self.stdout.write(f"📁 Certificates directory: {certs_dir}")
        
        # Check if files exist
        cert_files = [
            ("CA Certificate", ca_cert),
            ("Device Certificate", device_cert), 
            ("Device Key", device_key)
        ]
        
        all_exist = True
        for name, path in cert_files:
            if os.path.exists(path):
                size = os.path.getsize(path)
                self.stdout.write(self.style.SUCCESS(f"✅ {name}: {path} ({size} bytes)"))
            else:
                self.stdout.write(self.style.ERROR(f"❌ {name}: {path} (MISSING)"))
                all_exist = False
        
        if not all_exist:
            self.stdout.write(self.style.ERROR("❌ Some certificate files are missing. Cannot proceed with connection test."))
            return
        
        # Test connection
        self.stdout.write(f"🔗 Testing connection to {MQTT_SERVER}:{MQTT_PORT}")
        
        connection_result = {"connected": False, "error": None}
        
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                self.stdout.write(self.style.SUCCESS("✅ Successfully connected to AWS IoT Core!"))
                connection_result["connected"] = True
            else:
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
                self.stdout.write(self.style.ERROR(f"❌ Connection failed (rc={rc}): {error_msg}"))
                connection_result["error"] = f"rc={rc}: {error_msg}"
            client.disconnect()
        
        def on_disconnect(client, userdata, rc):
            if rc != 0:
                self.stdout.write(self.style.WARNING(f"⚠️ Disconnected with code {rc}"))
        
        # Create and configure client
        client = mqtt.Client(client_id="AquaGuard_Test")
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        
        try:
            # Configure TLS
            client.tls_set(
                ca_certs=ca_cert,
                certfile=device_cert,
                keyfile=device_key,
                tls_version=ssl.PROTOCOL_TLSv1_2
            )
            
            # Attempt connection
            self.stdout.write("🔄 Attempting connection...")
            client.connect(MQTT_SERVER, MQTT_PORT, 60)
            client.loop_start()
            
            # Wait for connection result
            import time
            time.sleep(5)  # Wait 5 seconds for connection
            
            client.loop_stop()
            client.disconnect()
            
            if connection_result["connected"]:
                self.stdout.write(self.style.SUCCESS("🎉 MQTT connection test PASSED!"))
            else:
                self.stdout.write(self.style.ERROR("💥 MQTT connection test FAILED!"))
                if connection_result["error"]:
                    self.stdout.write(self.style.ERROR(f"Error: {connection_result['error']}"))
                    
                self.stdout.write("\n🔧 Troubleshooting steps:")
                self.stdout.write("1. Check if device is registered in AWS IoT Core")
                self.stdout.write("2. Verify AWS IoT Core policy allows this connection")
                self.stdout.write("3. Check if certificates have expired")
                self.stdout.write("4. Verify AWS IoT Core endpoint is correct")
                self.stdout.write("5. Check network connectivity to AWS IoT Core")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Connection test failed with exception: {e}"))
            self.stdout.write("🔧 This usually indicates a network or certificate issue.")
