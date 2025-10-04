"""
API views for Cookie-Licking Detection system
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.http import JsonResponse, HttpResponseRedirect
from django.conf import settings
import requests
import logging

from .models import GoogleUser, ContributorProfile, Issue, Repository
from .serializers import (
    GoogleUserSerializer, ContributorProfileSerializer, 
    IssueSerializer, RepositorySerializer
)

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint"""
    return Response({
        'status': 'healthy',
        'message': 'Cookie-Licking Detection API is running',
        'version': '2.0'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def api_info(request):
    """API information endpoint"""
    return Response({
        'name': 'Cookie-Licking Detection API',
        'description': 'AI-powered system to detect and resolve issue assignment abandonment',
        'features': [
            'GitHub OAuth integration',
            'AI-powered trust scoring',
            'Automated reminder system',
            'Smart contributor analysis'
        ],
        'endpoints': {
            'health': '/api/health/',
            'info': '/api/info/',
            'github_auth': '/api/auth/github/login/',
            'issues': '/api/issues/',
            'contributors': '/api/contributors/'
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def list_contributors(request):
    """List all contributor profiles"""
    contributors = ContributorProfile.objects.all().order_by('-trust_score')[:10]
    serializer = ContributorProfileSerializer(contributors, many=True)
    return Response({
        'contributors': serializer.data,
        'total_count': ContributorProfile.objects.count()
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def list_issues(request):
    """List all issues"""
    issues = Issue.objects.filter(state='open').order_by('-created_at')[:20]
    serializer = IssueSerializer(issues, many=True)
    return Response({
        'issues': serializer.data,
        'total_count': Issue.objects.filter(state='open').count()
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def stats(request):
    """Basic statistics"""
    return Response({
        'total_contributors': ContributorProfile.objects.count(),
        'total_issues': Issue.objects.count(),
        'open_issues': Issue.objects.filter(state='open').count(),
        'assigned_issues': Issue.objects.exclude(assignee__isnull=True).exclude(assignee='').count(),
        'repositories': Repository.objects.count(),
        'google_users': GoogleUser.objects.count()
    })


# Google OAuth Views
@api_view(['GET'])
@permission_classes([AllowAny])
def google_login(request):
    """Start Google OAuth flow"""
    client_id = settings.GOOGLE_CLIENT_ID
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    
    if not client_id:
        return Response({
            'error': 'Google OAuth not configured - using demo mode',
            'message': 'Demo mode: Google authentication will be simulated',
            'demo_mode': True
        })
    
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/auth"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope=openid email profile"
        f"&response_type=code"
        f"&state=random_state"
    )
    
    return Response({
        'auth_url': google_auth_url,
        'message': 'Redirect to this URL to start Google OAuth',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'configured': True
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def google_callback(request):
    """Handle Google OAuth callback"""
    code = request.GET.get('code')
    error = request.GET.get('error')
    
    if error:
        return Response({
            'error': f'Google authentication failed: {error}',
            'success': False
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not code:
        return Response({
            'error': 'Authorization code not received',
            'success': False
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # For demo mode (no Google credentials or demo code)
        if not settings.GOOGLE_CLIENT_SECRET or code.startswith('demo_'):
            # Demo user data
            user_data = {
                'id': f'demo_{hash(code) % 100000}',
                'email': f'demo.user.{code[:6]}@gmail.com',
                'name': f'Demo User {code[:6]}',
                'picture': 'https://lh3.googleusercontent.com/a/default-user=s96-c'
            }
            access_token = f'demo_google_token_{code[:10]}'
            logger.info("Using demo mode for Google OAuth")
        else:
            # Real Google OAuth flow
            logger.info(f"Making token request with client_id: {settings.GOOGLE_CLIENT_ID[:10]}...")
            token_response = requests.post('https://oauth2.googleapis.com/token', {
                'client_id': settings.GOOGLE_CLIENT_ID,
                'client_secret': settings.GOOGLE_CLIENT_SECRET,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': settings.GOOGLE_REDIRECT_URI,
            })
            
            logger.info(f"Token response status: {token_response.status_code}")
            token_data = token_response.json()
            logger.info(f"Token data: {token_data}")
            
            access_token = token_data.get('access_token')
            
            if access_token:
                # Fetch user data from Google
                user_response = requests.get('https://www.googleapis.com/oauth2/v2/userinfo',
                    headers={'Authorization': f'Bearer {access_token}'})
                user_data = user_response.json()
            else:
                error_msg = token_data.get('error_description', token_data.get('error', 'Unknown error'))
                raise Exception(f"Failed to get access token: {error_msg}")
        
        # Create or update GoogleUser
        google_user, created = GoogleUser.objects.get_or_create(
            google_id=user_data['id'],
            defaults={
                'email': user_data['email'],
                'name': user_data['name'],
                'avatar_url': user_data.get('picture', ''),
                'access_token': access_token,
            }
        )
        
        # Redirect to frontend with user data in URL parameters
        user_data = {
            'id': google_user.id,
            'email': google_user.email,
            'name': google_user.name,
            'avatar_url': google_user.avatar_url,
            'created': created,
            'needs_github_url': not google_user.github_url
        }
        
        # Encode user data as URL parameters
        from urllib.parse import urlencode
        import json
        
        frontend_url = "http://localhost:5173"  # Updated to match Vite dev server port
        redirect_params = {
            'auth_success': 'true',
            'user_data': json.dumps(user_data)
        }
        
        redirect_url = f"{frontend_url}?{urlencode(redirect_params)}"
        return HttpResponseRedirect(redirect_url)
        
    except Exception as e:
        logger.error(f"Google OAuth error: {e}")
        return Response({
            'error': 'Failed to process Google authentication',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def submit_github_url(request):
    """Submit GitHub URL after Google authentication"""
    user_id = request.data.get('user_id')
    github_url = request.data.get('github_url')
    
    if not user_id or not github_url:
        return Response({
            'error': 'user_id and github_url are required',
            'success': False
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        google_user = GoogleUser.objects.get(id=user_id)
        
        # Validate GitHub URL format
        import re
        if not re.match(r'https://github\.com/[^/]+/?$', github_url.rstrip('/')):
            return Response({
                'error': 'Invalid GitHub URL format. Please use: https://github.com/username',
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract username from URL
        username = github_url.rstrip('/').split('/')[-1]
        
        # Update Google user with GitHub info
        google_user.github_url = github_url
        google_user.github_username = username
        google_user.save()
        
        # Create ContributorProfile
        contributor, created = ContributorProfile.objects.get_or_create(
            username=username,
            defaults={
                'profile_url': github_url,
                'avatar_url': google_user.avatar_url,
                'google_user': google_user,
            }
        )
        
        return Response({
            'success': True,
            'message': 'GitHub URL saved successfully!',
            'contributor': {
                'username': contributor.username,
                'profile_url': contributor.profile_url,
                'trust_score': contributor.trust_score,
                'created': created
            }
        })
        
    except GoogleUser.DoesNotExist:
        return Response({
            'error': 'User not found',
            'success': False
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"GitHub URL submission error: {e}")
        return Response({
            'error': 'Failed to save GitHub URL',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def user_profile(request):
    """Get user profile"""
    user_id = request.GET.get('user_id')
    
    if not user_id:
        return Response({
            'error': 'user_id parameter required',
            'found': False
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        google_user = GoogleUser.objects.get(id=user_id)
        
        response_data = {
            'user': {
                'id': google_user.id,
                'email': google_user.email,
                'name': google_user.name,
                'avatar_url': google_user.avatar_url,
                'github_url': google_user.github_url,
                'github_username': google_user.github_username,
            },
            'found': True
        }
        
        # Add contributor data if available
        if google_user.github_username:
            try:
                contributor = ContributorProfile.objects.get(username=google_user.github_username)
                response_data['contributor'] = ContributorProfileSerializer(contributor).data
            except ContributorProfile.DoesNotExist:
                pass
        
        return Response(response_data)
        
    except GoogleUser.DoesNotExist:
        return Response({
            'error': 'User not found',
            'found': False
        }, status=status.HTTP_404_NOT_FOUND)
