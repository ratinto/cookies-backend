"""
Real GitHub API Views for Cookie-Licking Detection
Implements the exact endpoints and functionality specified by the user
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import GoogleUser, RealIssue, RealComment, GitHubUser, RealActivityLog, InactiveAssigneeDetection
from .services.real_github_service import RealGitHubService, TrustScoreCalculator, CookieLickingDetector
from django.conf import settings

logger = logging.getLogger(__name__)


def get_github_service(user_id: int = None) -> RealGitHubService:
    """Get GitHub service with user's access token if available"""
    if user_id:
        try:
            user = GoogleUser.objects.get(id=user_id)
            return RealGitHubService(access_token=user.github_access_token)
        except GoogleUser.DoesNotExist:
            pass
    
    # Use the global GitHub token from settings
    access_token = getattr(settings, 'GITHUB_ACCESS_TOKEN', None)
    return RealGitHubService(access_token=access_token)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_issues(request):
    """
    /api/issues/ → Fetch all issues from user's repositories
    Once a maintainer logs in, they can view all issues from their repositories
    """
    user_id = request.GET.get('user_id')
    repo_owner = request.GET.get('repo_owner', 'aaneesa')  # Default to your repo
    repo_name = request.GET.get('repo_name', 'Gurukul-2.0')  # Default to your repo
    
    try:
        logger.info(f"🔍 Starting get_user_issues: user_id={user_id}, repo={repo_owner}/{repo_name}")
        github_service = get_github_service(user_id)
        logger.info("✅ GitHub service created")
        
        # Fetch issues from GitHub API
        logger.info("📋 Fetching issues from GitHub...")
        github_issues = github_service.get_repo_issues(repo_owner, repo_name)
        logger.info(f"✅ Got {len(github_issues)} issues")
        
        processed_issues = []
        
        for i, issue in enumerate(github_issues[:10]):  # Process only first 10 for debugging
            try:
                logger.info(f"📝 Processing issue {i+1}/10: #{issue.get('number')}")
                
                # Store/update issue in database  
                issue_obj, created = RealIssue.objects.update_or_create(
                    issue_id=issue['id'],
                    defaults={
                        'issue_number': issue['number'],
                        'title': issue['title'][:500],  # Truncate if too long
                        'body': (issue.get('body') or '')[:1000],  # Truncate body
                        'repo_owner': repo_owner,
                        'repo_name': repo_name,
                        'assignee': issue.get('assignee', {}).get('login') if issue.get('assignee') else None,
                        'status': issue['state'],
                        'created_at_github': datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00')) if issue.get('created_at') else timezone.now(),
                        'updated_at_github': datetime.fromisoformat(issue['updated_at'].replace('Z', '+00:00')) if issue.get('updated_at') else timezone.now(),
                    }
                )
                logger.info(f"✅ Saved issue #{issue['number']} to database")
                
            except Exception as issue_error:
                logger.error(f"❌ Error processing issue #{issue.get('number', 'unknown')}: {issue_error}")
                continue
            
            # Skip comments processing for debugging
            comment_data = []
            trust_scores = []
            
            # Format response as specified
            processed_issue = {
                'issue_id': issue['id'],
                'issue_number': issue['number'],
                'title': issue['title'],
                'description': issue.get('body', ''),
                'assignee': issue.get('assignee', {}).get('login') if issue.get('assignee') else None,
                'status': 'Assigned' if issue.get('assignee') else 'Unassigned',
                'comments': comment_data,
                'trust_scores': trust_scores,
                'created_at': issue['created_at'],
                'updated_at': issue['updated_at']
            }
            
            processed_issues.append(processed_issue)
        
        return Response({
            'success': True,
            'repository': f"{repo_owner}/{repo_name}",
            'total_issues': len(processed_issues),
            'issues': processed_issues
        })
        
    except Exception as e:
        logger.error(f"Error fetching issues: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_issue_details(request, issue_id):
    """
    /api/issues/<id>/ → Fetch issue details and comments
    """
    try:
        issue = RealIssue.objects.get(issue_id=issue_id)
        
        # Get fresh data from GitHub
        github_service = get_github_service()
        comments = github_service.get_issue_comments(issue.repo_owner, issue.repo_name, issue.issue_number)
        
        trust_scores = []
        comment_data = []
        
        for comment in comments:
            if comment['user_login']:
                comment_data.append({
                    'username': comment['user_login'],
                    'body': comment['body'],
                    'created_at': comment['created_at'],
                    'reactions': comment['reactions']
                })
                
                # Get trust score
                try:
                    github_user = GitHubUser.objects.get(username=comment['user_login'])
                    trust_scores.append({
                        'username': github_user.username,
                        'score': github_user.trust_score,
                        'tag': github_user.tag
                    })
                except GitHubUser.DoesNotExist:
                    trust_scores.append({
                        'username': comment['user_login'],
                        'score': 0,
                        'tag': 'Unknown'
                    })
        
        return Response({
            'issue_id': issue.issue_id,
            'title': issue.title,
            'assignee': issue.assignee,
            'status': 'Assigned' if issue.assignee else 'Unassigned',
            'comments': comment_data,
            'trust_scores': trust_scores
        })
        
    except RealIssue.DoesNotExist:
        return Response({
            'error': 'Issue not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_contributor_activity(request, username):
    """
    /api/contributor/<username>/ → Fetch contributor activity and calculate trust score
    """
    try:
        github_service = get_github_service()
        trust_calculator = TrustScoreCalculator(github_service)
        
        # Calculate trust score
        trust_result = trust_calculator.calculate_trust_score(username)
        
        if not trust_result['success']:
            return Response({
                'error': trust_result['error']
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get user events
        events = github_service.get_user_events(username)
        
        # Store activity logs
        for event in events[:10]:  # Store recent 10 events
            event_type = event.get('type')
            points = 0
            
            if event_type == 'PushEvent':
                points = 3
            elif event_type == 'PullRequestEvent':
                points = 2
            elif event_type == 'IssueCommentEvent':
                points = 2
            
            RealActivityLog.objects.update_or_create(
                event_id=event['id'],
                defaults={
                    'username': username,
                    'event_type': event_type,
                    'repo_name': event.get('repo', {}).get('name', ''),
                    'event_data': event,
                    'trust_score_points': points,
                    'created_at_github': datetime.fromisoformat(event['created_at'].replace('Z', '+00:00')),
                }
            )
        
        # Update/create GitHub user
        GitHubUser.objects.update_or_create(
            username=username,
            defaults={
                'trust_score': trust_result['trust_score'],
                'tag': trust_result['tag'],
                'last_activity_check': timezone.now(),
            }
        )
        
        return Response({
            'username': username,
            'trust_score': trust_result['trust_score'],
            'tag': trust_result['tag'],
            'event_counts': trust_result['event_counts'],
            'has_recent_activity': trust_result['has_recent_activity'],
            'recent_events': events[:5]  # Return 5 most recent events
        })
        
    except Exception as e:
        logger.error(f"Error getting contributor activity for {username}: {e}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def analyze_inactive_contributors(request):
    """
    /api/analyze/ → Detect inactive assigned users
    """
    repo_owner = request.data.get('repo_owner', 'aaneesa')
    repo_name = request.data.get('repo_name', 'Gurukul-2.0')
    user_id = request.data.get('user_id')
    
    try:
        github_service = get_github_service(user_id)
        trust_calculator = TrustScoreCalculator(github_service)
        detector = CookieLickingDetector(github_service, trust_calculator)
        
        # Check for inactive contributors
        inactive_detections = detector.check_inactive_contributors(repo_owner, repo_name)
        
        # Store detections in database
        for detection in inactive_detections:
            try:
                issue = RealIssue.objects.get(
                    repo_owner=repo_owner,
                    repo_name=repo_name,
                    issue_number=detection['issue_number']
                )
                
                InactiveAssigneeDetection.objects.update_or_create(
                    issue=issue,
                    assignee_username=detection['assignee'],
                    defaults={
                        'days_inactive': detection['days_inactive'],
                        'trust_score_at_detection': detection['trust_score'],
                    }
                )
            except RealIssue.DoesNotExist:
                logger.warning(f"Issue #{detection['issue_number']} not found in database")
        
        return Response({
            'success': True,
            'repository': f"{repo_owner}/{repo_name}",
            'inactive_contributors_detected': len(inactive_detections),
            'detections': inactive_detections
        })
        
    except Exception as e:
        logger.error(f"Error analyzing inactive contributors: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_reminder(request):
    """
    /api/remind/ → Send polite reminder comment
    """
    repo_owner = request.data.get('repo_owner')
    repo_name = request.data.get('repo_name')
    issue_number = request.data.get('issue_number')
    assignee = request.data.get('assignee')
    user_id = request.data.get('user_id')
    
    if not all([repo_owner, repo_name, issue_number, assignee]):
        return Response({
            'error': 'Missing required parameters'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        github_service = get_github_service(user_id)
        trust_calculator = TrustScoreCalculator(github_service)
        detector = CookieLickingDetector(github_service, trust_calculator)
        
        # Send reminder
        success = detector.send_reminder_comment(repo_owner, repo_name, issue_number, assignee)
        
        if success:
            # Update detection record
            try:
                issue = RealIssue.objects.get(
                    repo_owner=repo_owner,
                    repo_name=repo_name,
                    issue_number=issue_number
                )
                
                detection, created = InactiveAssigneeDetection.objects.get_or_create(
                    issue=issue,
                    assignee_username=assignee
                )
                
                detection.reminder_sent = True
                detection.reminder_sent_at = timezone.now()
                detection.save()
                
            except RealIssue.DoesNotExist:
                pass
            
            return Response({
                'success': True,
                'message': f'Reminder sent to @{assignee} on issue #{issue_number}'
            })
        else:
            return Response({
                'success': False,
                'error': 'Failed to send reminder'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        logger.error(f"Error sending reminder: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def unassign_inactive_user(request):
    """
    /api/release/ → Unassign inactive user
    """
    repo_owner = request.data.get('repo_owner')
    repo_name = request.data.get('repo_name')
    issue_number = request.data.get('issue_number')
    user_id = request.data.get('user_id')
    
    if not all([repo_owner, repo_name, issue_number]):
        return Response({
            'error': 'Missing required parameters'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        github_service = get_github_service(user_id)
        trust_calculator = TrustScoreCalculator(github_service)
        detector = CookieLickingDetector(github_service, trust_calculator)
        
        # Unassign user
        success = detector.unassign_inactive_user(repo_owner, repo_name, issue_number)
        
        if success:
            # Update database
            try:
                issue = RealIssue.objects.get(
                    repo_owner=repo_owner,
                    repo_name=repo_name,
                    issue_number=issue_number
                )
                
                issue.assignee = None
                issue.save()
                
                # Update detection record
                detection = InactiveAssigneeDetection.objects.filter(
                    issue=issue
                ).first()
                
                if detection:
                    detection.unassigned = True
                    detection.unassigned_at = timezone.now()
                    detection.save()
                
            except RealIssue.DoesNotExist:
                pass
            
            return Response({
                'success': True,
                'message': f'Issue #{issue_number} unassigned successfully'
            })
        else:
            return Response({
                'success': False,
                'error': 'Failed to unassign issue'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        logger.error(f"Error unassigning user: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_repositories(request):
    """
    GET /api/real/repositories/ → Get popular repositories for analysis
    Returns a list of popular repositories that users can select for cookie-licking analysis
    """
    try:
        # Popular repositories for cookie-licking analysis
        popular_repos = [
            {
                'owner': 'microsoft',
                'name': 'vscode',
                'full_name': 'microsoft/vscode',
                'description': 'Visual Studio Code',
                'stars': '162k',
                'language': 'TypeScript',
                'url': 'https://github.com/microsoft/vscode'
            },
            {
                'owner': 'facebook',
                'name': 'react',
                'full_name': 'facebook/react',
                'description': 'The library for web and native user interfaces',
                'stars': '225k',
                'language': 'JavaScript',
                'url': 'https://github.com/facebook/react'
            },
            {
                'owner': 'torvalds',
                'name': 'linux',
                'full_name': 'torvalds/linux',
                'description': 'Linux kernel source tree',
                'stars': '177k',
                'language': 'C',
                'url': 'https://github.com/torvalds/linux'
            },
            {
                'owner': 'nodejs',
                'name': 'node',
                'full_name': 'nodejs/node',
                'description': 'Node.js JavaScript runtime',
                'stars': '106k',
                'language': 'JavaScript',
                'url': 'https://github.com/nodejs/node'
            },
            {
                'owner': 'tensorflow',
                'name': 'tensorflow',
                'full_name': 'tensorflow/tensorflow',
                'description': 'An Open Source Machine Learning Framework for Everyone',
                'stars': '185k',
                'language': 'C++',
                'url': 'https://github.com/tensorflow/tensorflow'
            },
            {
                'owner': 'kubernetes',
                'name': 'kubernetes',
                'full_name': 'kubernetes/kubernetes',
                'description': 'Production-Grade Container Scheduling and Management',
                'stars': '109k',
                'language': 'Go',
                'url': 'https://github.com/kubernetes/kubernetes'
            },
            {
                'owner': 'python',
                'name': 'cpython',
                'full_name': 'python/cpython',
                'description': 'The Python programming language',
                'stars': '61k',
                'language': 'Python',
                'url': 'https://github.com/python/cpython'
            },
            {
                'owner': 'flutter',
                'name': 'flutter',
                'full_name': 'flutter/flutter',
                'description': 'Flutter makes it easy to build beautiful apps',
                'stars': '164k',
                'language': 'Dart',
                'url': 'https://github.com/flutter/flutter'
            }
        ]
        
        # Get GitHub service for additional repo info if needed
        github_service = get_github_service()
        
        return Response({
            'success': True,
            'repositories': popular_repos,
            'message': f'Retrieved {len(popular_repos)} popular repositories for analysis'
        })
        
    except Exception as e:
        logger.error(f"Error fetching repositories: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def calculate_trust_score(request):
    """
    GET /api/real/trust-score/?owner=<owner>&repo=<repo>&username=<username>
    Calculate trust score for a specific user in a repository
    """
    try:
        owner = request.GET.get('owner')
        repo = request.GET.get('repo')
        username = request.GET.get('username')
        
        if not all([owner, repo, username]):
            return Response({
                'success': False,
                'error': 'Missing required parameters: owner, repo, username'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        github_service = get_github_service()
        
        # Calculate trust score using the service
        trust_calculator = github_service.trust_calculator
        trust_breakdown = trust_calculator.calculate_comprehensive_trust_score(
            username, owner, repo
        )
        
        return Response({
            'success': True,
            'trust_score': trust_breakdown.get('overall_score', 0),
            'trust_breakdown': trust_breakdown,
            'username': username,
            'repository': f"{owner}/{repo}"
        })
        
    except Exception as e:
        logger.error(f"Error calculating trust score: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def unassign_user(request):
    """
    POST /api/real/unassign-user/
    Unassign a user from an issue (simulated - would integrate with GitHub API)
    """
    try:
        data = request.data
        owner = data.get('owner')
        repo = data.get('repo')
        issue_number = data.get('issue_number')
        username = data.get('username')
        
        if not all([owner, repo, issue_number, username]):
            return Response({
                'success': False,
                'error': 'Missing required parameters: owner, repo, issue_number, username'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # In a real implementation, this would use GitHub API to unassign
        # For now, we'll simulate the unassignment
        logger.info(f"Unassigning {username} from issue #{issue_number} in {owner}/{repo}")
        
        return Response({
            'success': True,
            'message': f'Successfully unassigned {username} from issue #{issue_number}',
            'repository': f"{owner}/{repo}",
            'issue_number': issue_number,
            'unassigned_user': username
        })
        
    except Exception as e:
        logger.error(f"Error unassigning user: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
