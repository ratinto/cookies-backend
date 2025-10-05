"""
Real GitHub API URL patterns for Cookie-Licking Detection
Implements the exact endpoints specified by the user
"""
from django.urls import path
from . import real_views

# Real GitHub Integration URLs
real_urlpatterns = [
    # Main Backend Endpoints as specified
    path('issues/', real_views.get_user_issues, name='real_get_user_issues'),
    path('issues/<int:issue_id>/', real_views.get_issue_details, name='real_get_issue_details'),
    path('contributor/<str:username>/', real_views.get_contributor_activity, name='real_get_contributor_activity'),
    path('analyze/', real_views.analyze_inactive_contributors, name='real_analyze_inactive_contributors'),
    path('remind/', real_views.send_reminder, name='real_send_reminder'),
    path('release/', real_views.unassign_inactive_user, name='real_unassign_inactive_user'),
]
