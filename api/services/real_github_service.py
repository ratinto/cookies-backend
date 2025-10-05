"""
Real GitHub API Service for Cookie-Licking Detection
Uses the exact GitHub API endpoints provided by the user
"""
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class RealGitHubService:
    """Service for real GitHub API integration using provided endpoints"""
    
    def __init__(self, access_token: str = None):
        """Initialize with GitHub access token for API calls"""
        self.access_token = access_token
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        
        if self.access_token:
            self.session.headers.update({
                'Authorization': f'token {self.access_token}',
                'Accept': 'application/vnd.github.v3+json'
            })
        else:
            self.session.headers.update({
                'Accept': 'application/vnd.github.v3+json'
            })

    def get_repo_issues(self, owner: str, repo: str) -> List[Dict]:
        """
        GET /repos/{owner}/{repo}/issues → fetch all issues
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        params = {'state': 'all', 'per_page': 100}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            issues = response.json()
            
            logger.info(f"Fetched {len(issues)} issues from {owner}/{repo}")
            return issues
            
        except requests.RequestException as e:
            logger.error(f"Error fetching issues from {owner}/{repo}: {e}")
            return []

    def get_issue_comments(self, owner: str, repo: str, issue_number: int) -> List[Dict]:
        """
        GET /repos/{owner}/{repo}/issues/{number}/comments → fetch issue comments
        Returns: user.login, body, user.id, reactions
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}/comments"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            comments = response.json()
            
            # Extract the fields you specified
            processed_comments = []
            for comment in comments:
                processed_comment = {
                    'id': comment.get('id'),
                    'user_login': comment.get('user', {}).get('login'),
                    'user_id': comment.get('user', {}).get('id'),
                    'body': comment.get('body'),
                    'reactions': comment.get('reactions', {}),
                    'created_at': comment.get('created_at')
                }
                processed_comments.append(processed_comment)
            
            logger.info(f"Fetched {len(processed_comments)} comments for issue #{issue_number}")
            return processed_comments
            
        except requests.RequestException as e:
            logger.error(f"Error fetching comments for issue #{issue_number}: {e}")
            return []

    def get_user_events(self, username: str) -> List[Dict]:
        """
        GET /users/{username}/events/public → fetch user activity
        Returns: actor.login and full event data as provided in your example
        """
        url = f"{self.base_url}/users/{username}/events/public"
        params = {'per_page': 30}  # Get recent 30 events
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            events = response.json()
            
            logger.info(f"Fetched {len(events)} events for user {username}")
            return events
            
        except requests.RequestException as e:
            logger.error(f"Error fetching events for user {username}: {e}")
            return []

    def search_user_comments(self, username: str) -> List[Dict]:
        """
        GET /search/issues?q=commenter:{username}
        """
        url = f"{self.base_url}/search/issues"
        params = {
            'q': f'commenter:{username}',
            'sort': 'updated',
            'per_page': 100
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            items = data.get('items', [])
            logger.info(f"Found {len(items)} issues with comments by {username}")
            return items
            
        except requests.RequestException as e:
            logger.error(f"Error searching comments by {username}: {e}")
            return []

    def get_repo_commits(self, owner: str, repo: str, since: str = None) -> List[Dict]:
        """
        GET /repos/{owner}/{repo}/commits
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params = {'per_page': 100}
        
        if since:
            params['since'] = since
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            commits = response.json()
            
            logger.info(f"Fetched {len(commits)} commits from {owner}/{repo}")
            return commits
            
        except requests.RequestException as e:
            logger.error(f"Error fetching commits from {owner}/{repo}: {e}")
            return []

    def get_rate_limit(self) -> Dict:
        """
        GET /rate_limit → check current rate limit status
        """
        url = f"{self.base_url}/rate_limit"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error fetching rate limit: {e}")
            return {}

    def patch_issue_assignee(self, owner: str, repo: str, issue_number: int, assignees: List[str] = None) -> bool:
        """
        PATCH /repos/{owner}/{repo}/issues/{number} → unassign issue
        """
        if not self.access_token:
            logger.error("Cannot update issue without access token")
            return False
            
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}"
        data = {'assignees': assignees or []}
        
        try:
            response = self.session.patch(url, json=data)
            response.raise_for_status()
            
            logger.info(f"Updated assignees for issue #{issue_number}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Error updating issue #{issue_number}: {e}")
            return False

    def post_issue_comment(self, owner: str, repo: str, issue_number: int, body: str) -> Optional[Dict]:
        """
        POST /repos/{owner}/{repo}/issues/{number}/comments → send reminder comment
        """
        if not self.access_token:
            logger.error("Cannot post comment without access token")
            return None
            
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}/comments"
        data = {'body': body}
        
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            
            comment = response.json()
            logger.info(f"Posted comment on issue #{issue_number}")
            return comment
            
        except requests.RequestException as e:
            logger.error(f"Error posting comment on issue #{issue_number}: {e}")
            return None


class TrustScoreCalculator:
    """Calculate trust scores exactly as specified"""
    
    def __init__(self, github_service: RealGitHubService):
        self.github_service = github_service

    def calculate_trust_score(self, username: str) -> Dict:
        """
        Logic for Trust Score Calculation:
        - Fetch recent 10 events from /users/{username}/events/public
        - PushEvent → +3 points
        - PullRequestEvent → +2 points  
        - IssueCommentEvent → +2 points
        - No event in last 7 days → -3 points
        """
        try:
            events = self.github_service.get_user_events(username)
            
            if not events:
                return {
                    'success': False,
                    'error': f'No events found for user {username}'
                }
            
            # Take only recent 10 events as specified
            recent_events = events[:10]
            
            # Calculate score
            score = 0
            event_counts = {'PushEvent': 0, 'PullRequestEvent': 0, 'IssueCommentEvent': 0}
            
            # Check for events in last 7 days
            from datetime import timezone as dt_timezone
            seven_days_ago = datetime.now(dt_timezone.utc) - timedelta(days=7)
            has_recent_activity = False
            
            for event in recent_events:
                event_type = event.get('type')
                created_at = event.get('created_at')
                
                # Parse event date
                try:
                    event_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    if event_date > seven_days_ago:
                        has_recent_activity = True
                except:
                    pass
                
                # Award points based on event type
                if event_type == 'PushEvent':
                    score += 3
                    event_counts['PushEvent'] += 1
                elif event_type == 'PullRequestEvent':
                    score += 2
                    event_counts['PullRequestEvent'] += 1
                elif event_type == 'IssueCommentEvent':
                    score += 2
                    event_counts['IssueCommentEvent'] += 1
            
            # Penalty for no recent activity
            if not has_recent_activity:
                score -= 3
            
            # Assign tags based on score
            if score > 10:
                tag = "Reliable Contributor"
            elif 5 <= score <= 10:
                tag = "Active Contributor"
            else:
                tag = "Inactive / Needs Follow-up"
            
            return {
                'success': True,
                'username': username,
                'trust_score': score,
                'tag': tag,
                'event_counts': event_counts,
                'has_recent_activity': has_recent_activity,
                'total_events_analyzed': len(recent_events)
            }
            
        except Exception as e:
            logger.error(f"Error calculating trust score for {username}: {e}")
            return {
                'success': False,
                'error': str(e)
            }


class CookieLickingDetector:
    """Cookie-licking detection logic exactly as specified"""
    
    def __init__(self, github_service: RealGitHubService, trust_calculator: TrustScoreCalculator):
        self.github_service = github_service
        self.trust_calculator = trust_calculator

    def check_inactive_contributors(self, owner: str, repo: str) -> List[Dict]:
        """
        Every 24 hours, check all issues with assigned users.
        For each issue:
        - If assignee's last GitHub activity > 7 days ago → mark as stale
        - Send polite reminder comment
        - If 3 days pass with no new comment or commit → unassign
        """
        try:
            # Get all issues from the repository
            issues = self.github_service.get_repo_issues(owner, repo)
            
            inactive_detections = []
            
            for issue in issues:
                assignee = issue.get('assignee')
                if not assignee:
                    continue  # Skip unassigned issues
                
                assignee_username = assignee.get('login')
                if not assignee_username:
                    continue
                
                # Check assignee's last activity
                trust_data = self.trust_calculator.calculate_trust_score(assignee_username)
                
                if not trust_data['success']:
                    continue
                
                # If user has no recent activity (last 7 days)
                if not trust_data['has_recent_activity']:
                    detection = {
                        'issue_number': issue.get('number'),
                        'issue_title': issue.get('title'),
                        'assignee': assignee_username,
                        'trust_score': trust_data['trust_score'],
                        'tag': trust_data['tag'],
                        'days_inactive': 7,  # At least 7 days
                        'needs_reminder': True,
                        'issue_url': issue.get('html_url')
                    }
                    
                    inactive_detections.append(detection)
            
            return inactive_detections
            
        except Exception as e:
            logger.error(f"Error checking inactive contributors for {owner}/{repo}: {e}")
            return []

    def send_reminder_comment(self, owner: str, repo: str, issue_number: int, assignee: str) -> bool:
        """Send polite reminder comment"""
        reminder_text = f"Hi @{assignee}, are you still working on this? 👋\n\nThis is a friendly reminder that you were assigned to this issue. If you need any help or would like to unassign yourself, please let us know!"
        
        comment = self.github_service.post_issue_comment(owner, repo, issue_number, reminder_text)
        return comment is not None

    def unassign_inactive_user(self, owner: str, repo: str, issue_number: int) -> bool:
        """Remove assignee from issue"""
        return self.github_service.patch_issue_assignee(owner, repo, issue_number, assignees=[])
