"""
Serializers for Google-integrated Cookie-Licking Detection system
"""
from rest_framework import serializers
from .models import (
    GoogleUser, ContributorProfile, Repository, Issue, Comment,
    ActivityLog, InactiveContributorDetection, ReminderMessage, AIAnalysisLog
)


class GoogleUserSerializer(serializers.ModelSerializer):
    """Serializer for Google authenticated users"""
    
    class Meta:
        model = GoogleUser
        fields = [
            'id', 'email', 'google_id', 'name', 'avatar_url',  
            'github_url', 'github_username', 'is_active', 'created_at', 'updated_at'
        ]
        # Exclude sensitive access_token


class ContributorProfileSerializer(serializers.ModelSerializer):
    """Serializer for contributor profiles with trust scoring"""
    completion_rate = serializers.ReadOnlyField()
    primary_tag = serializers.ReadOnlyField()
    
    class Meta:
        model = ContributorProfile
        fields = [
            'id', 'username', 'github_id', 'platform', 'profile_url', 
            'avatar_url', 'activity_score', 'total_claims', 'completed_claims',
            'comment_quality_score', 'code_quality_score', 
            'engagement_authenticity_score', 'behavioral_consistency_score',
            'trust_score', 'ai_tags', 'strengths', 'risk_factors',
            'recommendations', 'completion_rate', 'primary_tag',
            'last_activity_check', 'last_ai_analysis', 'created_at', 'updated_at'
        ]


class RepositorySerializer(serializers.ModelSerializer):
    """Serializer for repositories"""
    
    class Meta:
        model = Repository
        fields = '__all__'


class IssueSerializer(serializers.ModelSerializer):
    """Serializer for GitHub issues"""
    repository_name = serializers.CharField(source='repository.full_name', read_only=True)
    is_assigned = serializers.ReadOnlyField()
    
    class Meta:
        model = Issue
        fields = [
            'id', 'repository', 'repository_name', 'issue_id', 'issue_number',
            'title', 'body', 'state', 'assignee', 'assignees', 'labels', 'url',
            'complexity_score', 'is_assigned', 'created_at', 'updated_at',
            'last_assigned_at', 'last_reminder_sent'
        ]


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for issue comments"""
    
    class Meta:
        model = Comment
        fields = [
            'id', 'issue', 'comment_id', 'username', 'body', 'html_url',
            'sentiment_score', 'helpfulness_score', 'technical_accuracy_score',
            'created_at', 'updated_at'
        ]


class InactiveContributorDetectionSerializer(serializers.ModelSerializer):
    """Serializer for inactive contributor detections"""
    issue_title = serializers.CharField(source='issue.title', read_only=True)
    repository_name = serializers.CharField(source='issue.repository.full_name', read_only=True)
    contributor_trust_score = serializers.FloatField(source='contributor.trust_score', read_only=True)
    
    class Meta:
        model = InactiveContributorDetection
        fields = [
            'id', 'issue', 'issue_title', 'repository_name', 'assignee_username',
            'contributor', 'contributor_trust_score', 'days_inactive', 
            'last_activity_date', 'trust_score_at_detection', 'risk_factors',
            'reminder_sent', 'reminder_sent_at', 'reminder_comment_url',
            'unassigned', 'unassigned_at', 'unassign_reason',
            'contributor_responded', 'response_at', 'outcome',
            'created_at', 'updated_at'
        ]
