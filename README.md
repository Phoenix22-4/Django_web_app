# AquaSavvy Solution - IoT Water Management System

AquaSavvy Solution by Vision Technology is a full-stack IoT system for dual‑tank water management with a Django + Channels backend, real‑time dashboards, pump protection, and an optional Gemini‑powered assistant.

## Key Features
- Real-time water level monitoring (WebSockets)
- Pump dry‑run prevention and overfill protection
- Device dashboards and manual pump controls
- Optional AI assistant grounded to project docs
- Secure authentication and per‑user device access

## Tech Stack
- Hardware: ESP32
- Backend: Python, Django, Django Channels (ASGI)
- Database: PostgreSQL
- Realtime: WebSockets
- Deploy: Railway

## Local Development
1) Prerequisites
- Python 3.11+
- PostgreSQL

2) Install dependencies
```bash
pip install -r requirements.txt
```

3) Environment variables
- SECRET_KEY=your_strong_secret
- DATABASE_URL=postgres://user:pass@host:5432/dbname (optional; settings has a default)
- GEMINI_API_KEY=your_api_key (optional; enables chat)

4) Migrate & run
```bash
python manage.py migrate
python manage.py runserver
```

5) Static files (for production)
```bash
python manage.py collectstatic --noinput
```

## AI Assistant (Gemini)
- UI: floating chat on public home and device dashboard (💬 icon).
- Endpoint: POST `/api/ai_chat/` (login required by default)
  - Request: `{ "message": "your question" }`
  - Response: `{ "reply": "assistant answer" }`
- Server uses `requests` to call Google Gemini REST API. If `GEMINI_API_KEY` is missing, a safe fallback reply is returned.
- Assistant is grounded to `staticfiles/docs/index.html` and limited to AquaSavvy topics (setup, monitoring, pump control, alerts, troubleshooting, usage). For technical issues, it shares support contacts.

## Real-Time Push Notifications (FCM)
- Added `django-push-notifications` and `push_notifications` app.
- Frontend: `dashboard/static/push_handler.js` registers a service worker at `/static/sw.js` and saves the FCM token via `/api/save_push_subscription/`.
- Service worker: `dashboard/static/sw.js` displays incoming notifications.
- Backend endpoint: `save_push_subscription` stores tokens in `FCMDevice` tied to the logged-in user.
- Alerts: `dashboard/notifications.py` checks critical events with cooldowns (dry-run, underground low, overhead full) and sends push to device owner.
- Integration: Alerts are triggered after each `WaterReading` in `dashboard/consumers.py`.
- Scheduled check: `dashboard/management/commands/check_connectivity.py` sends OFFLINE alert if no readings > 15 minutes.
- Firebase setup: Include Firebase SDK in `dashboard/templates/base.html` and set your firebaseConfig (already added). In Firebase Console, enable Cloud Messaging (Web) and configure Web credentials.

## Business Analytics in Admin
- Model: `DailyWaterUsage` stores daily totals per device (space efficient).
- Aggregation command: `dashboard/management/commands/aggregate_usage.py` computes yesterday totals, purges raw readings > 48h and daily usage > 35 days, with guidance for long-term monthly summaries.
- Admin dashboard: `dashboard/templates/admin/analytics_dashboard.html` (table, pie, line chart, CSV export). See custom admin view in `dashboard/admin.py` at `/admin/analytics/`.

## Security
- `@login_required` on device list, dashboard, and chat endpoint
- CSRF enforced for chat (frontend sends `X-CSRFToken`)
- `@never_cache` prevents back navigation to authenticated pages after logout

## End‑User Documentation
See `staticfiles/docs/index.html` (Quick Start, Automatic features, Indicators, Power cuts, Troubleshooting).

## Deployment (Railway)
- Set Variables: `SECRET_KEY`, `GEMINI_API_KEY` (optional), any DB variables
- Redeploy after changes

## Files of Interest
- `dashboard/templates/public_home.html` – hero/marketing, docs link, public chat
- `dashboard/templates/device_list.html` – responsive device cards
- `dashboard/templates/dashboard.html` – 2x2 grid, LED, large controls, chat
- `dashboard/static/dashboard.css` – cards, grid, LED, pump animation, chat styles
- `dashboard/static/dashboard.js` – WS UI updates, LED toggle, chat logic
- `dashboard/views.py` – `ai_chat_view` (Gemini proxy)
- `dashboard/urls.py` – routes including `/api/ai_chat/`
- `staticfiles/docs/index.html` – user manual used to ground AI

## Support
- Email: contact:vision072025@gmail.com
- WhatsApp: +254 702 715070