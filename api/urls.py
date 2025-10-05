"""
URL configuration for API
"""
from django.urls import path, include
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('info/', views.api_info, name='api_info'),
    path('contributors/', views.list_contributors, name='list_contributors'),
    path('issues/', views.list_issues, name='list_issues'),
    path('stats/', views.stats, name='stats'),
    
    # Google OAuth endpoints
    path('auth/google/login/', views.google_login, name='google_login'),
    path('auth/google/callback/', views.google_callback, name='google_callback'),
    path('auth/submit-github/', views.submit_github_url, name='submit_github_url'),
    path('auth/profile/', views.user_profile, name='user_profile'),
    
    # Cookie-licking detection endpoints
    path('analyze/repository/', views.analyze_repository, name='analyze_repository'),
    path('analyze/contributor/', views.analyze_contributor, name='analyze_contributor'),
]

# Real GitHub Integration URLs (the main implementation)
from . import real_views

real_urlpatterns = [
    # Real endpoints as specified by user
    path('real/issues/', real_views.get_user_issues, name='real_get_user_issues'),
    path('real/issues/<int:issue_id>/', real_views.get_issue_details, name='real_get_issue_details'), 
    path('real/contributor-activity/', real_views.get_contributor_activity, name='contributor_activity'),
    path('real/inactive-contributors/', real_views.analyze_inactive_contributors, name='inactive_contributors'),
    path('real/trust-score/', real_views.calculate_trust_score, name='trust_score'),
    path('real/unassign-user/', real_views.unassign_user, name='unassign_user'),
    path('real/repositories/', real_views.get_repositories, name='get_repositories'),
]

# Combine both URL patterns
urlpatterns += real_urlpatterns
