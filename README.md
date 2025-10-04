# Cookie-Licking Detection Backend

A Django REST Framework backend for the Cookie-Licking Detection system that identifies and manages GitHub issue abandonment patterns.

## Features

- **Google OAuth Authentication** - Secure user authentication via Google
- **GitHub Integration** - Collect and analyze GitHub user profiles
- **AI-Powered Trust Scoring** - Advanced contributor reliability analysis
- **Issue Monitoring** - Track open issues and assignment patterns
- **RESTful API** - Complete API for frontend integration

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/aaneesa/MaintainerX-backend.git
cd MaintainerX-backend
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install django djangorestframework django-cors-headers python-decouple requests
```

### 4. Environment Configuration

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` and add your actual credentials:

```properties
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_actual_google_client_id
GOOGLE_CLIENT_SECRET=your_actual_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8002/api/auth/google/callback/

# Django Settings
SECRET_KEY=your_generated_django_secret_key
DEBUG=True

# CORS Settings (for frontend at localhost:5173)
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

#### Getting Google OAuth Credentials:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google+ API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
5. Set application type to "Web application"
6. Add authorized redirect URIs: `http://localhost:8002/api/auth/google/callback/`
7. Copy the Client ID and Client Secret to your `.env` file

### 5. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Sample Data (Optional)

```bash
python manage.py populate_sample_data
```

### 7. Run the Development Server

```bash
python manage.py runserver 8002
```

The API will be available at `http://localhost:8002/api/`

## API Endpoints

### Authentication
- `GET /api/auth/google/login/` - Start Google OAuth flow
- `GET /api/auth/google/callback/` - Google OAuth callback
- `POST /api/auth/submit-github/` - Submit GitHub profile URL
- `GET /api/auth/profile/` - Get user profile

### Data Endpoints
- `GET /api/health/` - Health check
- `GET /api/info/` - API information
- `GET /api/stats/` - Platform statistics
- `GET /api/contributors/` - List contributors with trust scores
- `GET /api/issues/` - List open issues

## Project Structure

```
backend2/
├── cookielicking/          # Django project settings
├── api/                    # Main API application
│   ├── models.py          # Database models
│   ├── views.py           # API endpoints
│   ├── serializers.py     # Data serialization
│   ├── urls.py            # URL routing
│   └── management/        # Custom management commands
├── .env.example           # Environment template
├── requirements.txt       # Python dependencies
└── manage.py             # Django management script
```

## Models

- **GoogleUser** - Google authenticated users
- **ContributorProfile** - GitHub contributor analysis
- **Repository** - Monitored repositories
- **Issue** - GitHub issues tracking
- **InactiveContributorDetection** - Cookie-licking detection results

## Development

### Adding Sample Data

The `populate_sample_data` management command creates:
- 3 sample repositories
- 6 sample contributors with varying trust scores
- 5 sample issues with different complexity levels

### Running Tests

```bash
python manage.py test
```

### API Testing

Test the API endpoints:

```bash
curl http://localhost:8002/api/health/
curl http://localhost:8002/api/stats/
curl http://localhost:8002/api/contributors/
```

## Security Notes

- Never commit the `.env` file to version control
- Use strong, unique SECRET_KEY in production
- Configure proper CORS settings for production
- Use HTTPS in production environment

## Frontend Integration

This backend is designed to work with the React + TypeScript frontend. The API supports:
- CORS for cross-origin requests
- JSON responses for all endpoints
- Error handling with proper HTTP status codes
- Google OAuth flow with frontend redirects

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure tests pass
5. Submit a pull request

## License

This project is part of the Cookie-Licking Detector system for managing GitHub issue abandonment patterns.
# cookies-backend
# cookies-backend
# cookies-backend
