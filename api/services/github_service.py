"""
GitHub API service for Cookie-Licking Detection
Handles all GitHub API interactions for analyzing contributor behavior
"""
import requests
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class GitHubAPIService:
    """Service for interacting with GitHub API to detect cookie-licking behavior"""
    
    def __init__(self, token: str = None, base_url: str = None):
        """
        Initialize GitHub API service
        
        Args:
            token: GitHub personal access token for authenticated requests
            base_url: GitHub API base URL
        """
        self.token = token or getattr(settings, 'GITHUB_API_TOKEN', None)
        self.base_url = (base_url or getattr(settings, 'GITHUB_API_BASE_URL', 'https://api.github.com')).rstrip('/')
        self.session = requests.Session()
        
        # Set up authentication headers
        if self.token:
            self.session.headers.update({
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json'
            })
        else:
            self.session.headers.update({
                'Accept': 'application/vnd.github.v3+json'
            })

    def get_user_details(self, username: str) -> Optional[Dict]:
        """Fetch GitHub user details"""
        url = f"{self.base_url}/users/{username}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching user details for {username}: {e}")
            return None
    
    def get_repo_issues_comments(self, owner: str, repo: str) -> List[Dict]:
        """Fetch all comments from repository issues"""
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/comments"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching repo comments: {e}")
            return []

    def get_user_events(self, username: str, pages: int = 1) -> List[Dict]:
        """Fetch user's public events with pagination"""
        all_events = []
        
        for page in range(1, pages + 1):
            url = f"{self.base_url}/users/{username}/events/public"
            params = {'page': page, 'per_page': 30}
            
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                events = response.json()
                
                if not events:  # No more events
                    break
                    
                all_events.extend(events)
            except requests.RequestException as e:
                logger.error(f"Error fetching user events page {page}: {e}")
                break
                
        return all_events

    def get_issue_comments(self, owner: str, repo: str, issue_number: int) -> List[Dict]:
        """Fetch comments for a specific issue"""
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}/comments"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching issue comments: {e}")
            return []

    def search_user_comments(self, username: str) -> List[Dict]:
        """Search for comments by a specific user"""
        url = f"{self.base_url}/search/issues"
        params = {
            'q': f'commenter:{username}',
            'sort': 'updated',
            'per_page': 100
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json().get('items', [])
        except requests.RequestException as e:
            logger.error(f"Error searching user comments: {e}")
            return []

    def get_repo_commits(self, owner: str, repo: str, since: Optional[str] = None) -> List[Dict]:
        """Fetch repository commits"""
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params = {}
        
        if since:
            params['since'] = since
            
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching repo commits: {e}")
            return []


class CookieLickingDetector:
    """
    Advanced detector for cookie-licking behavior in GitHub repositories
    Analyzes patterns to identify contributors who claim issues but don't follow through
    """
    
    def __init__(self, github_service: GitHubAPIService):
        self.github_service = github_service
        
        # Patterns that indicate claiming behavior
        self.claiming_patterns = [
            r'\b(i\'ll take this|taking this|i can do this|let me handle|working on this)\b',
            r'\b(assigning? (this )?to myself|self[- ]assign)\b',
            r'\b(i\'m on it|got it|i\'ll fix)\b',
            r'\b(claiming|claim)\b',
            r'@\w+\s+(can i|may i|could i).*(take|work on|handle)',
            r'\b(i will|i\'ll)\s+(work on|fix|handle|take care of)\b'
        ]
        
        # Time thresholds (in days)
        self.inactive_threshold = 7  # Days without activity after claiming
        self.abandonment_threshold = 14  # Days considered abandoned
        
    def detect_claiming_patterns(self, comment_body: str) -> List[str]:
        """Detect claiming patterns in comment text"""
        found_patterns = []
        comment_lower = comment_body.lower()
        
        for pattern in self.claiming_patterns:
            if re.search(pattern, comment_lower, re.IGNORECASE):
                found_patterns.append(pattern)
                
        return found_patterns

    def analyze_issue_for_cookie_licking(self, owner: str, repo: str, issue_number: int, assignee: str) -> Dict:
        """Analyze a specific issue for cookie-licking behavior"""
        try:
            # Get issue comments
            comments = self.github_service.get_issue_comments(owner, repo, issue_number)
            
            if not comments:
                return {
                    'success': False,
                    'error': 'No comments found for issue'
                }
            
            # Find claiming comments by assignee
            claiming_comments = []
            assignee_comments = []
            
            for comment in comments:
                if comment.get('user', {}).get('login', '').lower() == assignee.lower():
                    assignee_comments.append(comment)
                    
                    # Check for claiming patterns
                    body = comment.get('body', '')
                    patterns = self.detect_claiming_patterns(body)
                    if patterns:
                        claiming_comments.append({
                            'comment': comment,
                            'patterns': patterns,
                            'created_at': comment.get('created_at')
                        })
            
            # Analyze activity timeline
            last_activity = None
            if assignee_comments:
                last_comment = max(assignee_comments, key=lambda x: x.get('created_at', ''))
                last_activity = last_comment.get('created_at')
            
            # Calculate days since last activity
            days_inactive = 0
            if last_activity:
                try:
                    last_date = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                    days_inactive = (datetime.now(last_date.tzinfo) - last_date).days
                except:
                    days_inactive = 0
            
            # Determine risk level
            risk_level = 'low'
            risk_factors = []
            
            if claiming_comments and days_inactive > self.inactive_threshold:
                risk_level = 'medium'
                risk_factors.append(f'Claimed issue but inactive for {days_inactive} days')
            
            if claiming_comments and days_inactive > self.abandonment_threshold:
                risk_level = 'high'
                risk_factors.append(f'Potential abandonment - {days_inactive} days inactive')
            
            if len(claiming_comments) > 1:
                risk_factors.append('Multiple claiming comments')
            
            # Generate recommendation
            recommendation = 'Monitor'
            if risk_level == 'high':
                recommendation = 'Consider unassigning and sending reminder'
            elif risk_level == 'medium':
                recommendation = 'Send gentle reminder'
            
            return {
                'success': True,
                'risk_level': risk_level,
                'patterns_detected': [c['patterns'] for c in claiming_comments],
                'days_since_assignment': days_inactive,
                'last_activity': last_activity,
                'assignee_trust_score': self.calculate_trust_score(assignee).get('trust_score', 50),
                'recommendation': recommendation,
                'risk_factors': risk_factors,
                'claiming_comments_count': len(claiming_comments),
                'total_comments_by_assignee': len(assignee_comments)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing issue {owner}/{repo}#{issue_number}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def calculate_trust_score(self, username: str) -> Dict:
        """Calculate trust score for a contributor based on their GitHub activity"""
        try:
            # Get user details
            user_details = self.github_service.get_user_details(username)
            if not user_details:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            # Get recent activity
            events = self.github_service.get_user_events(username, pages=2)
            
            # Base score calculation
            base_score = 50
            
            # Account age factor (older accounts are more trustworthy)
            try:
                created_date = datetime.fromisoformat(user_details.get('created_at', '').replace('Z', '+00:00'))
                account_age_days = (datetime.now(created_date.tzinfo) - created_date).days
                age_score = min(25, account_age_days / 365 * 10)  # Max 25 points for account age
            except:
                age_score = 0
            
            # Follower/following ratio (more followers relative to following is better)
            followers = user_details.get('followers', 0)
            following = user_details.get('following', 0)
            
            if following > 0:
                ratio_score = min(15, (followers / following) * 5)
            else:
                ratio_score = min(15, followers * 0.1)
            
            # Public repositories (more repos indicate active development)
            repo_score = min(10, user_details.get('public_repos', 0) * 0.5)
            
            # Recent activity score
            activity_score = min(20, len(events) * 0.5)
            
            # Event type diversity (different types of contributions)
            event_types = set([event.get('type') for event in events])
            diversity_score = len(event_types) * 2
            
            # Calculate final score
            trust_score = base_score + age_score + ratio_score + repo_score + activity_score + diversity_score
            trust_score = min(100, max(0, trust_score))  # Clamp between 0-100
            
            return {
                'success': True,
                'trust_score': round(trust_score, 2),
                'factors': {
                    'account_age_days': account_age_days if 'account_age_days' in locals() else 0,
                    'followers': followers,
                    'following': following,
                    'public_repos': user_details.get('public_repos', 0),
                    'recent_events': len(events),
                    'event_types': list(event_types)
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating trust score for {username}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def analyze_repository_health(self, owner: str, repo: str) -> Dict:
        """Analyze overall repository health regarding cookie-licking"""
        try:
            # This is a placeholder for repository-level analysis
            # In a real implementation, you'd analyze all issues, contributors, etc.
            
            return {
                'success': True,
                'repository': f"{owner}/{repo}",
                'analysis': 'Repository analysis placeholder - would analyze all issues and contributors',
                'health_score': 75,  # Placeholder score
                'recommendations': [
                    'Monitor long-running assigned issues',
                    'Implement automated reminders for inactive assignees',
                    'Consider contribution guidelines for issue claiming'
                ]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing repository {owner}/{repo}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
