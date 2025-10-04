"""
Models for GitHub-integrated Cookie-Licking Detection system
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class GoogleUser(models.Model):
    """Google authenticated user model"""
    email = models.EmailField(unique=True)
    google_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    avatar_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)  # User-provided GitHub profile URL
    github_username = models.CharField(max_length=100, blank=True, null=True)  # Extracted from URL
    access_token = models.TextField()  # Google access token
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"GoogleUser: {self.email}"

    def save(self, *args, **kwargs):
        # Extract GitHub username from URL if provided
        if self.github_url and not self.github_username:
            import re
            match = re.search(r'github\.com/([^/]+)', self.github_url)
            if match:
                self.github_username = match.group(1)
        super().save(*args, **kwargs)


class Repository(models.Model):
    """Repository model"""
    name = models.CharField(max_length=200)
    full_name = models.CharField(max_length=200, unique=True)
    github_id = models.IntegerField(unique=True)
    owner = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    url = models.URLField()
    is_private = models.BooleanField(default=False)
    language = models.CharField(max_length=50, blank=True, null=True)
    stars_count = models.IntegerField(default=0)
    forks_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name


class ContributorProfile(models.Model):
    """Enhanced contributor profile with AI-powered trust scoring"""
    username = models.CharField(max_length=100, unique=True)
    github_id = models.IntegerField(unique=True, null=True, blank=True)  # May not have GitHub ID initially
    platform = models.CharField(max_length=20, default='github')
    profile_url = models.URLField()
    avatar_url = models.URLField(blank=True, null=True)
    google_user = models.OneToOneField('GoogleUser', on_delete=models.CASCADE, null=True, blank=True)
    
    # Activity metrics
    activity_score = models.FloatField(default=0.0)
    total_claims = models.IntegerField(default=0)
    completed_claims = models.IntegerField(default=0)
    
    # AI-enhanced trust scores (0-10 scale)
    comment_quality_score = models.FloatField(default=5.0)
    code_quality_score = models.FloatField(default=5.0)
    engagement_authenticity_score = models.FloatField(default=5.0)
    behavioral_consistency_score = models.FloatField(default=5.0)
    trust_score = models.FloatField(default=5.0)  # Overall weighted score
    
    # AI analysis results
    ai_tags = models.JSONField(default=list)  # ['reliable', 'ghost', 'newbie', etc.]
    strengths = models.JSONField(default=list)  # Identified strengths
    risk_factors = models.JSONField(default=list)  # Potential issues
    recommendations = models.JSONField(default=list)  # AI recommendations
    
    # Timestamps
    last_activity_check = models.DateTimeField(null=True, blank=True)
    last_ai_analysis = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def completion_rate(self):
        if self.total_claims == 0:
            return 0.0
        return (self.completed_claims / self.total_claims) * 100

    @property
    def primary_tag(self):
        if not self.ai_tags:
            return 'unanalyzed'
        return self.ai_tags[0] if self.ai_tags else 'unknown'

    def __str__(self):
        return f"{self.username} (Trust: {self.trust_score:.1f})"


class Issue(models.Model):
    """GitHub issue model"""
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='issues')
    issue_id = models.IntegerField()  # GitHub issue ID
    issue_number = models.IntegerField()  # GitHub issue number
    title = models.CharField(max_length=500)
    body = models.TextField(blank=True, null=True)
    state = models.CharField(max_length=20, default='open')
    assignee = models.CharField(max_length=100, blank=True, null=True)
    assignees = models.JSONField(default=list)  # Multiple assignees
    labels = models.JSONField(default=list)
    url = models.URLField()
    complexity_score = models.FloatField(default=1.0)
    
    # Tracking fields
    last_assigned_at = models.DateTimeField(null=True, blank=True)
    last_reminder_sent = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_assigned(self):
        return bool(self.assignee or self.assignees)

    class Meta:
        unique_together = ['repository', 'issue_number']

    def __str__(self):
        return f"Issue #{self.issue_number}: {self.title[:50]}"


class Comment(models.Model):
    """Issue comment model with AI analysis"""
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    comment_id = models.IntegerField()  # GitHub comment ID
    username = models.CharField(max_length=100)
    body = models.TextField()
    html_url = models.URLField()
    
    # AI analysis scores (0-10 scale)
    sentiment_score = models.FloatField(default=5.0)
    helpfulness_score = models.FloatField(default=5.0)
    technical_accuracy_score = models.FloatField(default=5.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.username} on Issue #{self.issue.issue_number}"


class ActivityLog(models.Model):
    """GitHub activity log for contributors"""
    username = models.CharField(max_length=100, db_index=True)
    event_type = models.CharField(max_length=50)  # PushEvent, IssueCommentEvent, etc.
    event_id = models.CharField(max_length=100, unique=True)
    repo_name = models.CharField(max_length=200)
    event_data = models.JSONField()  # Full event payload
    contribution_value_score = models.FloatField(default=1.0)
    timestamp = models.DateTimeField()  # GitHub event timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.username}: {self.event_type} on {self.repo_name}"


class InactiveContributorDetection(models.Model):
    """Cookie-licking detection and tracking"""
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    assignee_username = models.CharField(max_length=100)
    contributor = models.ForeignKey(ContributorProfile, on_delete=models.SET_NULL, null=True)
    
    # Detection metrics
    days_inactive = models.IntegerField()
    last_activity_date = models.DateTimeField(null=True, blank=True)
    trust_score_at_detection = models.FloatField()
    risk_factors = models.JSONField(default=list)
    
    # Reminder tracking
    reminder_sent = models.BooleanField(default=False)
    reminder_sent_at = models.DateTimeField(null=True, blank=True)
    reminder_comment_url = models.URLField(blank=True, null=True)
    
    # Resolution tracking
    unassigned = models.BooleanField(default=False)
    unassigned_at = models.DateTimeField(null=True, blank=True)
    unassign_reason = models.CharField(max_length=200, blank=True, null=True)
    contributor_responded = models.BooleanField(default=False)
    response_at = models.DateTimeField(null=True, blank=True)
    
    # Outcome tracking
    OUTCOMES = [
        ('pending', 'Pending'),
        ('reminded', 'Reminder Sent'),
        ('responded', 'Contributor Responded'),
        ('unassigned', 'Auto-unassigned'),
        ('resolved', 'Issue Resolved'),
    ]
    outcome = models.CharField(max_length=20, choices=OUTCOMES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cookie-licking: {self.assignee_username} on Issue #{self.issue.issue_number}"


class ReminderMessage(models.Model):
    """Reminder messages sent to contributors"""
    detection = models.ForeignKey(InactiveContributorDetection, on_delete=models.CASCADE)
    message_type = models.CharField(max_length=20, default='gentle')  # gentle, urgent, final
    github_comment_id = models.IntegerField(null=True, blank=True)
    message_body = models.TextField()
    html_url = models.URLField(blank=True, null=True)
    personalized = models.BooleanField(default=False)
    ai_tone = models.CharField(max_length=50, blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reminder ({self.message_type}) to {self.detection.assignee_username}"


class AIAnalysisLog(models.Model):
    """Log of AI analysis calls for debugging and monitoring"""
    contributor = models.ForeignKey(ContributorProfile, on_delete=models.CASCADE, null=True)
    analysis_type = models.CharField(max_length=50)  # trust_score, comment_analysis, etc.
    input_data_hash = models.CharField(max_length=64)  # To avoid duplicate analyses
    gemini_prompt = models.TextField()
    gemini_response = models.TextField()
    confidence_score = models.FloatField(default=0.0)
    tokens_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        contributor_name = self.contributor.username if self.contributor else 'N/A'
        return f"AI Analysis: {self.analysis_type} for {contributor_name}"
