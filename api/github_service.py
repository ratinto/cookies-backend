"""
GitHub API service for fetching user data, issues, and performing actions
"""
import requests
import json
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class GitHubService:
    """Service class for GitHub API interactions"""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            'Authorization': f'token {access_token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'CookieLickingDetector/1.0'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_user_info(self) -> Dict:
        """Get authenticated user information"""
        response = self.session.get(f"{self.BASE_URL}/user")
        response.raise_for_status()
        return response.json()

    def get_user_repos(self, username: str = None, per_page: int = 100) -> List[Dict]:
        """Get user's repositories"""
        if username:
            url = f"{self.BASE_URL}/users/{username}/repos"
        else:
            url = f"{self.BASE_URL}/user/repos"
        
        url += f"?per_page={per_page}&sort=updated"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_repo_issues(self, owner: str, repo: str, state: str = "all", per_page: int = 100) -> List[Dict]:
        """Get repository issues"""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/issues"
        params = {
            'state': state,
            'per_page': per_page,
            'sort': 'updated',
            'direction': 'desc'
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_issue_comments(self, owner: str, repo: str, issue_number: int) -> List[Dict]:
        """Get comments for a specific issue"""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/issues/{issue_number}/comments"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_user_activity(self, username: str, per_page: int = 30) -> List[Dict]:
        """Get user's public activity events"""
        url = f"{self.BASE_URL}/users/{username}/events/public"
        params = {'per_page': per_page}
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_user_profile(self, username: str) -> Dict:
        """Get detailed user profile"""
        url = f"{self.BASE_URL}/users/{username}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def unassign_issue(self, owner: str, repo: str, issue_number: int) -> Dict:
        """Remove all assignees from an issue"""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/issues/{issue_number}"
        data = {'assignees': []}
        
        response = self.session.patch(url, json=data)
        response.raise_for_status()
        return response.json()

    def add_issue_comment(self, owner: str, repo: str, issue_number: int, body: str) -> Dict:
        """Add a comment to an issue"""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/issues/{issue_number}/comments"
        data = {'body': body}
        
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def get_user_contributions_for_repo(self, username: str, owner: str, repo: str) -> Dict:
        """Get user's contributions to a specific repository"""
        # Get commits by user
        commits_url = f"{self.BASE_URL}/repos/{owner}/{repo}/commits"
        commits_params = {'author': username, 'per_page': 100}
        
        try:
            commits_response = self.session.get(commits_url, params=commits_params)
            commits = commits_response.json() if commits_response.status_code == 200 else []
        except:
            commits = []

        # Get pull requests by user
        prs_url = f"{self.BASE_URL}/repos/{owner}/{repo}/pulls"
        prs_params = {'creator': username, 'state': 'all', 'per_page': 100}
        
        try:
            prs_response = self.session.get(prs_url, params=prs_params)
            pull_requests = prs_response.json() if prs_response.status_code == 200 else []
        except:
            pull_requests = []

        return {
            'commits': commits,
            'pull_requests': pull_requests,
            'total_commits': len(commits),
            'total_prs': len(pull_requests)
        }

    def check_rate_limit(self) -> Dict:
        """Check current rate limit status"""
        response = self.session.get(f"{self.BASE_URL}/rate_limit")
        response.raise_for_status()
        return response.json()


class GitHubOAuthService:
    """Service for GitHub OAuth authentication"""
    
    @staticmethod
    def get_authorization_url(state: str = None) -> str:
        """Generate GitHub OAuth authorization URL"""
        base_url = "https://github.com/login/oauth/authorize"
        params = {
            'client_id': settings.GITHUB_CLIENT_ID,
            'redirect_uri': settings.GITHUB_REDIRECT_URI,
            'scope': 'repo,user:email,read:user',
            'state': state or 'random_state_string'
        }
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"

    @staticmethod
    def exchange_code_for_token(code: str) -> Dict:
        """Exchange authorization code for access token"""
        url = "https://github.com/login/oauth/access_token"
        data = {
            'client_id': settings.GITHUB_CLIENT_ID,
            'client_secret': settings.GITHUB_CLIENT_SECRET,
            'code': code,
            'redirect_uri': settings.GITHUB_REDIRECT_URI
        }
        
        headers = {'Accept': 'application/json'}
        response = requests.post(url, data=data, headers=headers)
        response.raise_for_status()
        return response.json()


class ActivityAnalyzer:
    """Analyze GitHub activity for trust scoring"""
    
    @staticmethod
    def calculate_base_activity_score(events: List[Dict]) -> float:
        """Calculate base activity score from GitHub events"""
        score = 0
        recent_cutoff = timezone.now() - timedelta(days=30)
        
        for event in events:
            event_date = datetime.fromisoformat(
                event['created_at'].replace('Z', '+00:00')
            )
            
            # Only count recent events
            if event_date < recent_cutoff:
                continue
                
            event_type = event['type']
            
            # Score different event types
            if event_type == 'PushEvent':
                score += 3
            elif event_type == 'PullRequestEvent':
                score += 2
            elif event_type == 'IssueCommentEvent':
                score += 2
            elif event_type == 'PullRequestReviewEvent':
                score += 2
            elif event_type == 'CreateEvent':
                score += 1
            elif event_type == 'WatchEvent':
                score += 0.5
            elif event_type == 'ForkEvent':
                score += 1
        
        return min(score, 50)  # Cap at 50 for base score

    @staticmethod
    def get_last_activity_date(events: List[Dict]) -> Optional[datetime]:
        """Get the date of last meaningful activity"""
        meaningful_events = [
            'PushEvent', 'PullRequestEvent', 'IssueCommentEvent', 
            'PullRequestReviewEvent', 'CreateEvent'
        ]
        
        for event in events:
            if event['type'] in meaningful_events:
                return datetime.fromisoformat(
                    event['created_at'].replace('Z', '+00:00')
                )
        
        return None

    @staticmethod
    def is_contributor_inactive(events: List[Dict], days_threshold: int = 7) -> bool:
        """Check if contributor has been inactive for specified days"""
        last_activity = ActivityAnalyzer.get_last_activity_date(events)
        
        if not last_activity:
            return True
            
        cutoff_date = timezone.now() - timedelta(days=days_threshold)
        return last_activity < cutoff_date
