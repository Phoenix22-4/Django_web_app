# dashboard/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.views import View
from .models import Device
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.conf import settings
import os
import json
import re

# --- NEW: VIEW FOR THE PUBLIC HOMEPAGE ---
def public_home_view(request):
    """
    This is the new public-facing homepage that Google will see.
    """
    return render(request, 'public_home.html')

# --- MODIFIED: THIS VIEW NOW REDIRECTS USERS ---
def home_view(request):
    """
    This view now redirects logged-in users to their device list,
    and logged-out users to the new public homepage.
    """
    if request.user.is_authenticated:
        return redirect('device_list')
    return redirect('public_home') # Redirect to the new public page

@login_required
def device_list_view(request):
    devices = Device.objects.filter(owner=request.user)
    return render(request, 'device_list.html', {'devices': devices})

@login_required
def dashboard_view(request, device_id):
    device = get_object_or_404(Device, device_id=device_id, owner=request.user)
    last_reading = device.readings.order_by('-timestamp').first()
    return render(request, 'dashboard.html', {'device': device, 'last_reading': last_reading})

class CustomLoginView(LoginView):
    template_name = 'login.html'


# --- AI Chat Proxy (Gemini) ---
@login_required
def ai_chat_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        payload = json.loads(request.body.decode('utf-8'))
        user_message = (payload.get('message') or '').strip()
        if not user_message:
            return JsonResponse({'error': 'Empty message'}, status=400)

        # Guard: Only respond about AquaSavvy system topics
        system_preamble = (
            "You are AquaSavvy Assistant for Vision Technology. "
            "Answer only AquaSavvy SOLUTION topics: water level monitoring, pump control, alerts, setup, troubleshooting, usage. "
            "If unrelated, redirect to AquaSavvy topics. If a technical fault is suspected or you cannot help, provide support: "
            "Email contact:vision072025@gmail.com and WhatsApp +254 702 715070. "
        )

        # Simple prompt grounding from docs content (best-effort)
        try:
            docs_path = os.path.join(settings.BASE_DIR, 'staticfiles', 'docs', 'index.html')
            with open(docs_path, 'r', encoding='utf-8') as f:
                docs_html = f.read()
            # Strip HTML tags for cleaner context
            docs_text = re.sub(r'<[^>]+>', ' ', docs_html)
            docs_text = re.sub(r'\s+', ' ', docs_text).strip()
            # Truncate to reasonable length to keep prompt small
            grounded_excerpt = docs_text[:2000]
            system_preamble += f"Use this project context when answering: {grounded_excerpt} "
        except Exception:
            pass

        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            # Fallback safe response if key not configured
            return JsonResponse({
                'reply': (
                    "AI assistant is not configured yet. For assistance, email contact:vision072025@gmail.com "
                    "or WhatsApp +254 702 715070."
                )
            })

        # Minimal call to Google Generative AI (Gemini) using REST via requests
        # to avoid adding heavy SDKs if not desired.
        import requests
        endpoint = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent'
        headers = {'Content-Type': 'application/json'}
        body = {
            'contents': [
                {'parts': [{'text': system_preamble}]},
                {'parts': [{'text': user_message}]}
            ]
        }
        resp = requests.post(f"{endpoint}?key={api_key}", headers=headers, json=body, timeout=15)
        if resp.status_code != 200:
            return JsonResponse({'reply': 'Temporary AI error. Please try again or contact support.'}, status=200)
        data = resp.json()
        # Extract text safely
        reply = (
            data.get('candidates', [{}])[0]
                .get('content', {})
                .get('parts', [{}])[0]
                .get('text')
        ) or 'I could not generate a response. Please contact support.'
        return JsonResponse({'reply': reply})
    except Exception as exc:
        return JsonResponse({'reply': 'AI error. Please contact support.'}, status=200)

class CustomLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')