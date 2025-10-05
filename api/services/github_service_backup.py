"""
GitHub API service for Cookie-Licking Detection
Handles all     def get_user_public_events(self, username: str) -> List[Dict]:
        """Fetch user's public events"""
        url = f"{self.base_url}/users/{username}/events/public"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching user events: {e}")
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
                
        return all_eventsinteractions for analyzing contributor behavior
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
    
    def get_user_public_events(self, username: str) -> List[Dict]:
        """Fetch user's recent public activity events"""
        url = f"{self.base_url}/users/{username}/events/public"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching user events: {e}")
            return []
    
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
        """Search for all issues where user has commented"""
        url = f"{self.base_url}/search/issues"
        params = {'q': f'commenter:{username}'}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json().get('items', [])
        except requests.RequestException as e:
            logger.error(f"Error searching user comments: {e}")
            return []
    
    def get_repo_commits(self, owner: str, repo: str, since: Optional[str] = None) -> List[Dict]:
        """Fetch repository commits, optionally since a specific date"""
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
    """Main class for detecting cookie-licking behavior patterns"""
    
    def __init__(self, github_service: GitHubAPIService):
        self.github = github_service
        
        # Patterns for detecting claiming behavior
        self.claiming_patterns = [
            r"i'?ll work on this",
            r"i'?ll take this",
            r"can i work on this",
            r"can i take this",
            r"assigning myself",
            r"i'?m on it",
            r"working on it",
            r"i'?ll fix this",
            r"let me handle this",
        ]
        
        # Compile regex patterns
        self.claiming_regex = re.compile(
            '|'.join(self.claiming_patterns), 
            re.IGNORECASE
        )
    
    def detect_claiming_comment(self, comment_body: str) -> bool:
        """Check if a comment indicates the user is claiming an issue"""
        return bool(self.claiming_regex.search(comment_body))
    
    def analyze_user_behavior(self, username: str, repo_owner: str, repo_name: str) -> Dict:
        """Comprehensive analysis of a user's behavior in a repository"""
        
        # Get user's activity and comments
        user_events = self.github.get_user_public_events(username)
        user_issues = self.github.search_user_comments(username)
        
        # Filter for the specific repository
        repo_issues = [
            issue for issue in user_issues 
            if f"{repo_owner}/{repo_name}" in issue.get('repository_url', '')
        ]
        
        analysis = {
            'username': username,
            'repository': f"{repo_owner}/{repo_name}",
            'total_comments': len(repo_issues),
            'claimed_issues': [],
            'completed_issues': [],
            'abandoned_issues': [],
            'trust_score': 0.0,
            'risk_factors': [],
            'activity_pattern': self._analyze_activity_pattern(user_events),
            'claiming_behavior': {},
        }
        
        # Analyze each issue where user commented
        for issue in repo_issues:
            issue_analysis = self._analyze_issue_interaction(
                username, repo_owner, repo_name, issue
            )
            
            if issue_analysis['claimed']:
                analysis['claimed_issues'].append(issue_analysis)
                
                if issue_analysis['completed']:
                    analysis['completed_issues'].append(issue_analysis)
                elif issue_analysis['abandoned']:
                    analysis['abandoned_issues'].append(issue_analysis)
        
        # Calculate trust score
        analysis['trust_score'] = self._calculate_trust_score(analysis)
        analysis['risk_factors'] = self._identify_risk_factors(analysis)
        
        return analysis
    
    def _analyze_issue_interaction(self, username: str, owner: str, repo: str, issue: Dict) -> Dict:
        """Analyze user's interaction with a specific issue"""
        issue_number = issue['number']
        comments = self.github.get_issue_comments(owner, repo, issue_number)
        
        user_comments = [
            comment for comment in comments 
            if comment['user']['login'].lower() == username.lower()
        ]
        
        analysis = {
            'issue_number': issue_number,
            'issue_title': issue['title'],
            'issue_url': issue['html_url'],
            'claimed': False,
            'claim_date': None,
            'completed': False,
            'abandoned': False,
            'days_since_claim': 0,
            'follow_up_comments': 0,
            'technical_comments': 0,
            'user_comments': len(user_comments),
        }
        
        # Check for claiming behavior
        for comment in user_comments:
            if self.detect_claiming_comment(comment['body']):
                analysis['claimed'] = True
                analysis['claim_date'] = comment['created_at']
                break
        
        if analysis['claimed']:
            # Calculate days since claim
            claim_date = datetime.fromisoformat(analysis['claim_date'].replace('Z', '+00:00'))
            analysis['days_since_claim'] = (datetime.now().replace(tzinfo=claim_date.tzinfo) - claim_date).days
            
            # Analyze follow-up activity
            analysis['follow_up_comments'] = len([
                c for c in user_comments 
                if c['created_at'] > analysis['claim_date']
            ])
            
            # Check if issue is closed/completed
            analysis['completed'] = issue['state'] == 'closed'
            
            # Consider abandoned if claimed but no activity for 7+ days and not completed
            analysis['abandoned'] = (
                analysis['days_since_claim'] > 7 and 
                analysis['follow_up_comments'] == 0 and 
                not analysis['completed']
            )
        
        return analysis
    
    def _analyze_activity_pattern(self, events: List[Dict]) -> Dict:
        """Analyze user's general GitHub activity pattern"""
        if not events:
            return {'total_events': 0, 'recent_activity': False}
        
        # Count different types of events
        event_types = {}
        recent_activity = False
        
        for event in events:
            event_type = event.get('type', 'Unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1
            
            # Check if there's recent activity (within last 7 days)
            event_date = datetime.fromisoformat(event['created_at'].replace('Z', '+00:00'))
            if (datetime.now().replace(tzinfo=event_date.tzinfo) - event_date).days <= 7:
                recent_activity = True
        
        return {
            'total_events': len(events),
            'event_types': event_types,
            'recent_activity': recent_activity,
            'push_events': event_types.get('PushEvent', 0),
            'issue_events': event_types.get('IssuesEvent', 0),
        }
    
    def _calculate_trust_score(self, analysis: Dict) -> float:
        """Calculate trust score based on behavior analysis"""
        if not analysis['claimed_issues']:
            return 5.0  # Neutral score for users who don't claim issues
        
        total_claimed = len(analysis['claimed_issues'])
        total_completed = len(analysis['completed_issues'])
        total_abandoned = len(analysis['abandoned_issues'])
        
        # Base score calculation
        completion_rate = total_completed / total_claimed if total_claimed > 0 else 0
        abandonment_rate = total_abandoned / total_claimed if total_claimed > 0 else 0
        
        # Score components (0-10 scale)
        completion_score = completion_rate * 10
        abandonment_penalty = abandonment_rate * 5
        activity_bonus = 1 if analysis['activity_pattern']['recent_activity'] else 0
        
        # Calculate final score
        trust_score = max(0, min(10, completion_score - abandonment_penalty + activity_bonus))
        
        return round(trust_score, 1)
    
    def _identify_risk_factors(self, analysis: Dict) -> List[str]:
        """Identify risk factors that suggest cookie-licking behavior"""
        risk_factors = []
        
        if len(analysis['abandoned_issues']) > 2:
            risk_factors.append("Multiple abandoned issues")
        
        if analysis['claimed_issues']:
            avg_days_since_claim = sum(
                issue['days_since_claim'] for issue in analysis['claimed_issues']
            ) / len(analysis['claimed_issues'])
            
            if avg_days_since_claim > 10:
                risk_factors.append("Long delays after claiming issues")
        
        completion_rate = (
            len(analysis['completed_issues']) / len(analysis['claimed_issues'])
            if analysis['claimed_issues'] else 0
        )
        
        if completion_rate < 0.3:
            risk_factors.append("Low completion rate")
        
        if not analysis['activity_pattern']['recent_activity']:
            risk_factors.append("No recent GitHub activity")
        
        if analysis['activity_pattern']['push_events'] == 0:
            risk_factors.append("No recent code contributions")
        
        return risk_factors
    
    def analyze_repository_health(self, owner: str, repo: str) -> Dict:
        """Analyze overall repository health regarding issue abandonment"""
        
        # Get all issue comments
        all_comments = self.github.get_repo_issues_comments(owner, repo)
        
        # Group comments by user
        user_comments = {}
        for comment in all_comments:
            username = comment['user']['login']
            if username not in user_comments:
                user_comments[username] = []
            user_comments[username].append(comment)
        
        # Analyze each user who has commented
        user_analyses = {}
        for username in user_comments.keys():
            if len(user_comments[username]) >= 1:  # Only analyze users with multiple comments
                user_analyses[username] = self.analyze_user_behavior(username, owner, repo)
        
        # Repository health metrics
        total_users = len(user_analyses)
        high_risk_users = len([
            user for user, analysis in user_analyses.items() 
            if analysis['trust_score'] < 4.0
        ])
        
        active_claimers = len([
            user for user, analysis in user_analyses.items() 
            if analysis['claimed_issues']
        ])
        
        repo_health = {
            'repository': f"{owner}/{repo}",
            'total_contributors': total_users,
            'active_claimers': active_claimers,
            'high_risk_users': high_risk_users,
            'risk_percentage': (high_risk_users / total_users * 100) if total_users > 0 else 0,
            'user_analyses': user_analyses,
            'recommendations': self._generate_repo_recommendations(user_analyses),
        }
        
        return repo_health
    
    def _generate_repo_recommendations(self, user_analyses: Dict) -> List[str]:
        """Generate recommendations for repository maintainers"""
        recommendations = []
        
        high_risk_users = [
            username for username, analysis in user_analyses.items() 
            if analysis['trust_score'] < 4.0
        ]
        
        if high_risk_users:
            recommendations.append(
                f"Monitor {len(high_risk_users)} high-risk contributors closely"
            )
        
        abandoned_issues = sum(
            len(analysis['abandoned_issues']) 
            for analysis in user_analyses.values()
        )
        
        if abandoned_issues > 5:
            recommendations.append(
                f"Review {abandoned_issues} potentially abandoned issues"
            )
        
        return recommendations
