# dashboard/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.views import View
from .models import Device
import os
import json
import google.generativeai as genai
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

# --- MODIFIED: This view now points to your new public homepage ---
def home_view(request):
    # This view is for the root URL ('/').
    # It now renders the public homepage.
    return render(request, 'public_home.html')

@login_required
def device_list_view(request):
    devices = Device.objects.filter(owner=request.user)
    return render(request, 'device_list.html', {'devices': devices})

@login_required
def dashboard_view(request, device_id):
    # Pass the full device object to the template
    device = get_object_or_404(Device, device_id=device_id, owner=request.user)
    last_reading = device.readings.order_by('-timestamp').first()
    
    # Get automation rules for this device
    automation_rules = device.rules.all()[:4] # Get up to 4 rules

    return render(request, 'dashboard.html', {
        'device': device, 
        'last_reading': last_reading,
        'automation_rules': automation_rules
    })

class CustomLoginView(LoginView):
    template_name = 'login.html'

class CustomLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')

# Service worker at /sw.js
def service_worker(request):
    content = render_to_string('sw.js')
    return HttpResponse(content, content_type='application/javascript')

# --- NEW: PUBLIC CHAT VIEW (for homepage) ---
@csrf_exempt # We use the X-CSRFToken header
def gemini_public_chat(request):
    if request.method == 'POST':
        try:
            genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
            
            data = json.loads(request.body)
            user_message = data.get('message')
            if not user_message:
                return JsonResponse({'error': 'No message provided.'}, status=400)
            
            system_prompt = """
            You are 'AquaSavvy AI', an assistant for the AquaSavvy water management system. 
            You are talking to a potential customer on the public homepage. 
            Your job is to answer questions about what the product does, its benefits (like saving money by preventing pump burnout, saving water), and its features. 
            DO NOT answer any questions that are not about this water system. 
            If asked something else, politely say 'I can only answer questions about the AquaSavvy water system.'
            """
            
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content([system_prompt, user_message])

            return JsonResponse({'reply': response.text})
        
        except Exception as e:
            # Check for API key error
            if "API_KEY" in str(e):
                 return JsonResponse({'error': 'Temporary AI error: The server API key is not configured.'}, status=500)
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)


# --- NEW: SECURE CHAT VIEW (for logged-in users) ---
@login_required
@csrf_exempt # We use the X-CSRFToken header
def gemini_chat_proxy(request):
    if request.method == 'POST':
        try:
            genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
            
            data = json.loads(request.body)
            user_message = data.get('message')
            if not user_message:
                return JsonResponse({'error': 'No message provided.'}, status=400)
            
            # This prompt is for LOGGED-IN users.
            system_prompt = f"""
            You are 'AquaSavvy AI', an expert water system assistant for a logged-in user.
            The user's username is '{request.user.username}'.
            You can answer questions about their system, give water saving tips, and explain technical concepts.
            Be helpful, friendly, and professional.
            """
            
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content([system_prompt, user_message])

            return JsonResponse({'reply': response.text})
        
        except Exception as e:
            if "API_KEY" in str(e):
                 return JsonResponse({'error': 'Temporary AI error: The server API key is not configured.'}, status=500)
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)


# --- NEW: VIEWS FOR MANAGING AUTOMATION RULES ---
@login_required
@csrf_exempt
def save_automation_rule(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        device = get_object_or_404(Device, device_id=data.get('device_id'), owner=request.user)
        
        # Logic to create or update a rule
        # ... (You'll need to implement this) ...
        
        return JsonResponse({'status': 'success', 'message': 'Rule saved!'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
@csrf_exempt
def delete_automation_rule(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # Logic to delete a rule
        # ... (You'll need to implement this) ...
        
        return JsonResponse({'status': 'success', 'message': 'Rule deleted!'})
    return JsonResponse({'error': 'Invalid request'}, status=400)