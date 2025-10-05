"""
API views for Cookie-Licking Detection system
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.http import JsonResponse, HttpResponseRedirect
from django.conf import settings
from django.db import models
import requests
import logging
from datetime import datetime, timedelta

from .models import GoogleUser, ContributorProfile, Issue, Repository
from .serializers import (
    GoogleUserSerializer, ContributorProfileSerializer, 
    IssueSerializer, RepositorySerializer
)
from .services.github_service import GitHubAPIService, CookieLickingDetector

logger = logging.getLogger(__name__)

# Initialize GitHub services
github_service = GitHubAPIService()
cookie_detector = CookieLickingDetector(github_service)


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
    """List all contributor profiles with real GitHub analysis"""
    try:
        # Get contributors with their current data
        contributors = ContributorProfile.objects.all().order_by('-trust_score')[:10]
        
        # Enhance with real GitHub data
        enhanced_contributors = []
        for contributor in contributors:
            # Get basic serialized data
            contributor_data = ContributorProfileSerializer(contributor).data
            
            # Add real GitHub analysis if username exists
            if contributor.username and contributor.username != 'sample_user':
                try:
                    # Get user details from GitHub
                    github_user = github_service.get_user_details(contributor.username)
                    if github_user:
                        contributor_data['github_data'] = {
                            'followers': github_user.get('followers', 0),
                            'following': github_user.get('following', 0),
                            'public_repos': github_user.get('public_repos', 0),
                            'created_at': github_user.get('created_at'),
                            'updated_at': github_user.get('updated_at'),
                            'company': github_user.get('company'),
                            'location': github_user.get('location'),
                            'blog': github_user.get('blog'),
                            'bio': github_user.get('bio')
                        }
                    
                    # Get recent activity analysis
                    recent_events = github_service.get_user_events(contributor.username, pages=1)
                    if recent_events:
                        contributor_data['recent_activity'] = {
                            'total_events': len(recent_events),
                            'event_types': list(set([event.get('type') for event in recent_events])),
                            'last_activity': recent_events[0].get('created_at') if recent_events else None
                        }
                    
                    # Calculate real trust score based on GitHub data
                    trust_analysis = cookie_detector.calculate_trust_score(contributor.username)
                    if trust_analysis['success']:
                        contributor_data['real_trust_score'] = trust_analysis['trust_score']
                        contributor_data['trust_factors'] = trust_analysis['factors']
                
                except Exception as e:
                    logger.warning(f"GitHub API error for {contributor.username}: {e}")
                    contributor_data['github_error'] = str(e)
            
            enhanced_contributors.append(contributor_data)
        
        return Response({
            'contributors': enhanced_contributors,
            'total_count': ContributorProfile.objects.count(),
            'enhanced_with_github': True
        })
    
    except Exception as e:
        logger.error(f"Contributors endpoint error: {e}")
        # Fallback to basic data
        contributors = ContributorProfile.objects.all().order_by('-trust_score')[:10]
        serializer = ContributorProfileSerializer(contributors, many=True)
        return Response({
            'contributors': serializer.data,
            'total_count': ContributorProfile.objects.count(),
            'enhanced_with_github': False,
            'error': str(e)
        })


@api_view(['GET'])
@permission_classes([AllowAny])
def list_issues(request):
    """List all issues with cookie-licking detection analysis"""
    try:
        # Get issues with their current data
        issues = Issue.objects.filter(state='open').order_by('-created_at')[:20]
        
        # Enhance with real cookie-licking detection
        enhanced_issues = []
        for issue in issues:
            # Get basic serialized data
            issue_data = IssueSerializer(issue).data
            
            # Add real cookie-licking analysis if we have repo and issue number
            if issue.repository and issue.issue_number and issue.assignee:
                try:
                    repo_full_name = f"{issue.repository.owner}/{issue.repository.name}"
                    
                    # Get issue comments for analysis
                    owner, repo_name = repo_full_name.split('/')
                    comments = github_service.get_issue_comments(
                        owner, 
                        repo_name,
                        issue.issue_number
                    )
                    
                    # Analyze for cookie-licking patterns
                    cookie_analysis = cookie_detector.analyze_issue_for_cookie_licking(
                        owner,
                        repo_name,
                        issue.issue_number,
                        issue.assignee
                    )
                    
                    if cookie_analysis['success']:
                        issue_data['cookie_licking_analysis'] = {
                            'risk_level': cookie_analysis['risk_level'],
                            'patterns_detected': cookie_analysis['patterns_detected'],
                            'days_since_assignment': cookie_analysis.get('days_since_assignment', 0),
                            'last_activity': cookie_analysis.get('last_activity'),
                            'trust_score': cookie_analysis.get('assignee_trust_score', 50),
                            'recommendation': cookie_analysis.get('recommendation', 'Monitor'),
                            'risk_factors': cookie_analysis.get('risk_factors', [])
                        }
                        
                        # Add comment analysis
                        if comments:
                            claiming_patterns = []
                            for comment in comments[:5]:  # Check last 5 comments
                                patterns = cookie_detector.detect_claiming_patterns(comment.get('body', ''))
                                if patterns:
                                    claiming_patterns.extend(patterns)
                            
                            issue_data['claiming_patterns'] = claiming_patterns
                            issue_data['total_comments'] = len(comments)
                    
                    else:
                        issue_data['cookie_licking_analysis'] = {
                            'error': cookie_analysis.get('error', 'Analysis failed')
                        }
                
                except Exception as e:
                    logger.warning(f"Cookie-licking analysis error for issue {issue.issue_number}: {e}")
                    issue_data['analysis_error'] = str(e)
            
            else:
                issue_data['cookie_licking_analysis'] = {
                    'status': 'insufficient_data',
                    'message': 'Missing repository, issue number, or assignee data'
                }
            
            enhanced_issues.append(issue_data)
        
        return Response({
            'issues': enhanced_issues,
            'total_count': Issue.objects.filter(state='open').count(),
            'cookie_licking_enabled': True
        })
    
    except Exception as e:
        logger.error(f"Issues endpoint error: {e}")
        # Fallback to basic data
        issues = Issue.objects.filter(state='open').order_by('-created_at')[:20]
        serializer = IssueSerializer(issues, many=True)
        return Response({
            'issues': serializer.data,
            'total_count': Issue.objects.filter(state='open').count(),
            'cookie_licking_enabled': False,
            'error': str(e)
        })


@api_view(['GET'])
@permission_classes([AllowAny])
def stats(request):
    """Enhanced statistics with real GitHub analysis"""
    try:
        # Basic database stats
        basic_stats = {
            'total_contributors': ContributorProfile.objects.count(),
            'total_issues': Issue.objects.count(),
            'open_issues': Issue.objects.filter(state='open').count(),
            'assigned_issues': Issue.objects.exclude(assignee__isnull=True).exclude(assignee='').count(),
            'repositories': Repository.objects.count(),
            'google_users': GoogleUser.objects.count()
        }
        
        # Enhanced stats with real analysis
        enhanced_stats = basic_stats.copy()
        
        # Analyze assigned issues for cookie-licking patterns
        assigned_issues = Issue.objects.exclude(assignee__isnull=True).exclude(assignee='').filter(state='open')
        cookie_licking_stats = {
            'total_analyzed': 0,
            'high_risk': 0,
            'medium_risk': 0,
            'low_risk': 0,
            'patterns_detected': 0,
            'recommendations': {
                'unassign': 0,
                'reminder': 0,
                'monitor': 0
            }
        }
        
        for issue in assigned_issues[:10]:  # Analyze first 10 for performance
            if issue.repository and issue.issue_number and issue.assignee:
                try:
                    repo_full_name = f"{issue.repository.owner}/{issue.repository.name}"
                    analysis = cookie_detector.analyze_issue_for_cookie_licking(
                        repo_full_name,
                        issue.issue_number,
                        issue.assignee
                    )
                    
                    if analysis['success']:
                        cookie_licking_stats['total_analyzed'] += 1
                        risk_level = analysis.get('risk_level', 'low')
                        
                        if risk_level == 'high':
                            cookie_licking_stats['high_risk'] += 1
                        elif risk_level == 'medium':
                            cookie_licking_stats['medium_risk'] += 1
                        else:
                            cookie_licking_stats['low_risk'] += 1
                        
                        if analysis.get('patterns_detected'):
                            cookie_licking_stats['patterns_detected'] += len(analysis['patterns_detected'])
                        
                        # Count recommendations
                        recommendation = analysis.get('recommendation', 'monitor').lower()
                        if 'unassign' in recommendation:
                            cookie_licking_stats['recommendations']['unassign'] += 1
                        elif 'reminder' in recommendation:
                            cookie_licking_stats['recommendations']['reminder'] += 1
                        else:
                            cookie_licking_stats['recommendations']['monitor'] += 1
                
                except Exception as e:
                    logger.warning(f"Stats analysis error for issue {issue.issue_number}: {e}")
        
        enhanced_stats['cookie_licking_detection'] = cookie_licking_stats
        
        # GitHub API health check
        try:
            test_user = github_service.get_user_details('octocat')  # Test with GitHub's mascot
            enhanced_stats['github_api_status'] = 'operational' if test_user else 'limited'
        except Exception as e:
            enhanced_stats['github_api_status'] = 'error'
            enhanced_stats['github_api_error'] = str(e)
        
        # Trust score distribution
        contributors = ContributorProfile.objects.all()
        trust_distribution = {
            'high_trust': contributors.filter(trust_score__gte=80).count(),
            'medium_trust': contributors.filter(trust_score__gte=50, trust_score__lt=80).count(),
            'low_trust': contributors.filter(trust_score__lt=50).count(),
            'average_trust': contributors.aggregate(avg_trust=models.Avg('trust_score'))['avg_trust'] or 0
        }
        enhanced_stats['trust_score_distribution'] = trust_distribution
        
        return Response(enhanced_stats)
    
    except Exception as e:
        logger.error(f"Stats endpoint error: {e}")
        # Fallback to basic stats
        return Response({
            'total_contributors': ContributorProfile.objects.count(),
            'total_issues': Issue.objects.count(),
            'open_issues': Issue.objects.filter(state='open').count(),
            'assigned_issues': Issue.objects.exclude(assignee__isnull=True).exclude(assignee='').count(),
            'repositories': Repository.objects.count(),
            'google_users': GoogleUser.objects.count(),
            'enhanced_analysis': False,
            'error': str(e)
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


@api_view(['POST'])
@permission_classes([AllowAny])
def analyze_repository(request):
    """Analyze a GitHub repository for cookie-licking patterns"""
    repo_url = request.data.get('repository_url', '').strip()
    
    if not repo_url:
        return Response({
            'error': 'repository_url is required',
            'success': False
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Extract owner/repo from URL
        if 'github.com' in repo_url:
            parts = repo_url.rstrip('/').split('/')
            if len(parts) >= 2:
                owner = parts[-2]
                repo = parts[-1]
                repo_full_name = f"{owner}/{repo}"
            else:
                return Response({
                    'error': 'Invalid GitHub repository URL format',
                    'success': False
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Assume it's already in owner/repo format
            repo_full_name = repo_url
        
        # Analyze repository health
        repo_analysis = cookie_detector.analyze_repository_health(repo_full_name)
        
        if not repo_analysis['success']:
            return Response({
                'error': repo_analysis.get('error', 'Repository analysis failed'),
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get additional repository statistics
        try:
            # This would require additional GitHub API calls
            # For now, return the basic analysis
            response_data = {
                'success': True,
                'repository': repo_full_name,
                'analysis': repo_analysis,
                'timestamp': datetime.now().isoformat()
            }
            
            return Response(response_data)
        
        except Exception as e:
            logger.error(f"Repository analysis error: {e}")
            return Response({
                'error': f'Analysis failed: {str(e)}',
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f"Repository analysis endpoint error: {e}")
        return Response({
            'error': 'Failed to analyze repository',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def analyze_contributor(request):
    """Analyze a GitHub contributor for trust score and activity patterns"""
    username = request.data.get('username', '').strip()
    
    if not username:
        return Response({
            'error': 'username is required',
            'success': False
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Get user details
        user_details = github_service.get_user_details(username)
        if not user_details:
            return Response({
                'error': f'GitHub user "{username}" not found',
                'success': False
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Calculate trust score
        trust_analysis = cookie_detector.calculate_trust_score(username)
        
        # Get recent activity
        recent_events = github_service.get_user_events(username, pages=2)
        
        # Analyze activity patterns
        activity_analysis = {
            'total_events': len(recent_events) if recent_events else 0,
            'event_types': {},
            'repositories_active_in': set(),
            'last_activity': None
        }
        
        if recent_events:
            activity_analysis['last_activity'] = recent_events[0].get('created_at')
            
            for event in recent_events:
                event_type = event.get('type', 'Unknown')
                activity_analysis['event_types'][event_type] = activity_analysis['event_types'].get(event_type, 0) + 1
                
                if event.get('repo', {}).get('name'):
                    activity_analysis['repositories_active_in'].add(event['repo']['name'])
        
        activity_analysis['repositories_active_in'] = list(activity_analysis['repositories_active_in'])
        
        response_data = {
            'success': True,
            'username': username,
            'user_details': {
                'id': user_details.get('id'),
                'login': user_details.get('login'),
                'name': user_details.get('name'),
                'company': user_details.get('company'),
                'location': user_details.get('location'),
                'email': user_details.get('email'),
                'bio': user_details.get('bio'),
                'public_repos': user_details.get('public_repos', 0),
                'followers': user_details.get('followers', 0),
                'following': user_details.get('following', 0),
                'created_at': user_details.get('created_at'),
                'updated_at': user_details.get('updated_at')
            },
            'trust_analysis': trust_analysis,
            'activity_analysis': activity_analysis,
            'timestamp': datetime.now().isoformat()
        }
        
        return Response(response_data)
    
    except Exception as e:
        logger.error(f"Contributor analysis error: {e}")
        return Response({
            'error': f'Failed to analyze contributor: {str(e)}',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
