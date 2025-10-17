# AquaSavvy Water Management System

## Overview
AquaSavvy is a comprehensive water management system that provides real-time monitoring, automated control, and intelligent assistance for water systems.

## Features

### 🏠 **Dashboard**
- **Real-time Monitoring**: Live tank levels, pump status, and system health
- **Interactive Charts**: Pump runtime and power usage visualization
- **Dynamic Tank Display**: Supports 1-4 tanks with adaptive grid layout
- **Connection Status**: WebSocket and device connectivity indicators

### 🤖 **AI Assistant**
- **Smart Chat Bot**: Integrated Gemini AI for system assistance
- **Troubleshooting Help**: Automated problem diagnosis and solutions
- **Maintenance Tips**: Proactive system care recommendations
- **24/7 Support**: Always available for user queries

### ⚙️ **Automation System**
- **4 Configurable Timeslots**: Flexible scheduling for different scenarios
- **Rule-based Control**: Set conditions for automatic pump operation
- **Tank Level Thresholds**: Customizable min/max levels for each tank
- **Time-based Scheduling**: Start/end times for automation rules

### 📱 **User Interface**
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Modern UI**: Clean, intuitive interface with color-coded elements
- **Real-time Updates**: Live data without page refresh
- **Accessibility**: Screen reader friendly and keyboard navigation

## System Architecture

### Frontend Components
- **Dashboard**: Main monitoring interface
- **Device List**: Grid view of all connected devices
- **Chat Widget**: AI assistant interface
- **Charts**: Real-time data visualization

### Backend Services
- **Django Framework**: Robust web application backend
- **WebSocket Support**: Real-time communication
- **AI Integration**: Gemini API for intelligent assistance
- **Database**: PostgreSQL for data persistence

### Device Integration
- **Sensor Support**: Tank level monitoring
- **Pump Control**: Automated water system management
- **Connectivity**: WebSocket and HTTP communication
- **Status Monitoring**: Real-time device health

## Installation & Setup

### Prerequisites
- Python 3.8+
- Django 4.0+
- PostgreSQL
- Node.js (for frontend assets)

### Environment Variables
```bash
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/aquasavvy
SECRET_KEY=your_secret_key_here
```

### Installation Steps
1. Clone the repository
2. Install Python dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Create superuser: `python manage.py createsuperuser`
5. Start development server: `python manage.py runserver`

## Usage Guide

### Getting Started
1. **Login**: Access the system with your credentials
2. **Device Setup**: Add your water system devices
3. **Dashboard**: Monitor real-time system status
4. **AI Assistant**: Get help with system questions
5. **Automation**: Set up automated control rules

### Dashboard Features
- **Tank Monitoring**: Visual representation of water levels
- **Pump Control**: Manual and automated pump operation
- **Status Messages**: System alerts and notifications
- **Automation Rules**: Configure automated responses

### AI Assistant
- **Ask Questions**: Get help with system operation
- **Troubleshooting**: Diagnose common issues
- **Maintenance**: Receive care recommendations
- **Support**: Contact information and help resources

## API Endpoints

### Chat API
- `POST /api/ai_chat/` - Send message to AI assistant
- Response: JSON with AI reply

### Automation API
- `POST /api/save_rule/` - Save automation rule
- `POST /api/delete_rule/` - Delete automation rule

## Troubleshooting

### Common Issues
1. **Connection Problems**: Check WebSocket status indicator
2. **Pump Issues**: Verify power supply and pump status
3. **Tank Monitoring**: Ensure sensors are clean and connected
4. **Automation**: Verify rule configuration and timing

### Support
- **Email**: contact:vision072025@gmail.com
- **WhatsApp**: +254 702 715070
- **AI Assistant**: Use the chat widget for instant help

## Development

### Project Structure
```
AquaGuard_Django/
├── dashboard/
│   ├── templates/          # HTML templates
│   ├── static/            # CSS, JS, images
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   └── urls.py            # URL routing
├── docs/                  # Documentation
└── requirements.txt       # Python dependencies
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License
This project is proprietary software. All rights reserved.

## Version History
- **v2.0**: Complete UI redesign with AI integration
- **v1.0**: Initial release with basic monitoring
