"""
Django admin configuration for Cookie-Licking Detection models
"""
from django.contrib import admin
from .models import (
    GoogleUser, ContributorProfile, Repository, Issue, Comment,
    ActivityLog, InactiveContributorDetection, ReminderMessage, AIAnalysisLog,
    GitHubUser, RealIssue, RealComment, RealActivityLog, InactiveAssigneeDetection
)


@admin.register(GoogleUser)
class GoogleUserAdmin(admin.ModelAdmin):
    list_display = ['name', 'google_id', 'email', 'github_url', 'created_at']
    list_filter = ['created_at']
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


# Real GitHub Models Admin

@admin.register(GitHubUser)
class GitHubUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'trust_score', 'tag', 'last_activity_check', 'created_at']
    list_filter = ['tag', 'created_at']
    search_fields = ['username']
    readonly_fields = ['github_id', 'created_at', 'updated_at']


@admin.register(RealIssue)
class RealIssueAdmin(admin.ModelAdmin):
    list_display = ['title', 'repo_owner', 'repo_name', 'issue_number', 'assignee', 'status', 'created_at_github']
    list_filter = ['status', 'repo_owner', 'created_at_github']
    search_fields = ['title', 'assignee', 'repo_name']
    readonly_fields = ['issue_id', 'created_at', 'updated_at']


@admin.register(RealComment)
class RealCommentAdmin(admin.ModelAdmin):
    list_display = ['username', 'issue', 'created_at_github']
    list_filter = ['created_at_github']
    search_fields = ['username', 'body', 'issue__title']
    readonly_fields = ['comment_id', 'created_at', 'updated_at']


@admin.register(RealActivityLog)
class RealActivityLogAdmin(admin.ModelAdmin):
    list_display = ['username', 'event_type', 'repo_name', 'trust_score_points', 'created_at_github']
    list_filter = ['event_type', 'created_at_github']
    search_fields = ['username', 'repo_name']
    readonly_fields = ['event_id', 'created_at']


@admin.register(InactiveAssigneeDetection)
class InactiveAssigneeDetectionAdmin(admin.ModelAdmin):
    list_display = ['assignee_username', 'issue', 'days_inactive', 'reminder_sent', 'unassigned', 'created_at']
    list_filter = ['reminder_sent', 'unassigned', 'created_at']
    search_fields = ['assignee_username', 'issue__title']
    readonly_fields = ['created_at', 'updated_at']
