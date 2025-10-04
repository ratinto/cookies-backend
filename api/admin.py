"""
Django admin configuration for Cookie-Licking Detection models
"""
from django.contrib import admin
from .models import (
    GoogleUser, ContributorProfile, Repository, Issue, Comment,
    ActivityLog, InactiveContributorDetection, ReminderMessage, AIAnalysisLog
)


@admin.register(GoogleUser)
class GoogleUserAdmin(admin.ModelAdmin):
    list_display = ['name', 'google_id', 'email', 'github_url', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'email', 'github_url']
    readonly_fields = ['google_id', 'created_at', 'updated_at']


@admin.register(ContributorProfile)
class ContributorProfileAdmin(admin.ModelAdmin):
    list_display = ['username', 'trust_score', 'activity_score', 'total_claims', 'completed_claims', 'primary_tag']
    list_filter = ['platform', 'ai_tags', 'created_at']
    search_fields = ['username']
    readonly_fields = ['github_id', 'completion_rate', 'primary_tag', 'created_at', 'updated_at']


@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'language', 'stars_count', 'forks_count', 'is_private']
    list_filter = ['language', 'is_private', 'created_at']
    search_fields = ['name', 'full_name', 'owner']
    readonly_fields = ['github_id', 'created_at', 'updated_at']


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ['issue_number', 'title', 'repository', 'state', 'assignee', 'is_assigned']
    list_filter = ['state', 'repository', 'created_at']
    search_fields = ['title', 'assignee', 'issue_number']
    readonly_fields = ['issue_id', 'is_assigned', 'created_at', 'updated_at']


@admin.register(InactiveContributorDetection)
class InactiveContributorDetectionAdmin(admin.ModelAdmin):
    list_display = ['assignee_username', 'issue', 'days_inactive', 'trust_score_at_detection', 'outcome', 'reminder_sent']
    list_filter = ['outcome', 'reminder_sent', 'unassigned', 'contributor_responded', 'created_at']
    search_fields = ['assignee_username', 'issue__title']
    readonly_fields = ['created_at', 'updated_at']
