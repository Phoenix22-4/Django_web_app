# dashboard/management/commands/init_firebase.py
from django.core.management.base import BaseCommand
import json
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Initialize Firebase Admin SDK with service account credentials'

    def handle(self, *args, **options):
        try:
            # Get Firebase service account JSON from environment
            firebase_json = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')
            
            if not firebase_json:
                self.stdout.write(
                    self.style.WARNING('FIREBASE_SERVICE_ACCOUNT_JSON environment variable not found')
                )
                return
            
            # Parse and validate JSON
            try:
                firebase_config = json.loads(firebase_json)
                
                # Fix private key format
                if 'private_key' in firebase_config and isinstance(firebase_config['private_key'], str):
                    firebase_config['private_key'] = firebase_config['private_key'].replace('\\n', '\n')
                
                # Test Firebase initialization
                import firebase_admin
                from firebase_admin import credentials
                
                if not firebase_admin._apps:
                    cred = credentials.Certificate(firebase_config)
                    firebase_admin.initialize_app(cred)
                    self.stdout.write(
                        self.style.SUCCESS('✅ Firebase Admin SDK initialized successfully')
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Firebase Admin SDK already initialized')
                    )
                    
            except json.JSONDecodeError as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Invalid JSON in FIREBASE_SERVICE_ACCOUNT_JSON: {e}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error initializing Firebase: {e}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Command failed: {e}')
            )
