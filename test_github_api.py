#!/usr/bin/env python
"""
Test script to verify GitHub API access with personal access token
Run this to test if your GitHub token is working properly
"""
import os
import sys
import django

# Add the backend2 directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cookielicking.settings')
django.setup()

from api.services.real_github_service import RealGitHubService
from django.conf import settings

def test_github_api():
    """Test GitHub API with the configured token"""
    print("🔍 Testing GitHub API access...")
    
    # Get token from settings
    token = getattr(settings, 'GITHUB_ACCESS_TOKEN', None)
    if not token or token == 'your_github_personal_access_token_here':
        print("❌ No GitHub token configured!")
        print("Please add your GitHub Personal Access Token to the .env file:")
        print("GITHUB_ACCESS_TOKEN=your_actual_token_here")
        return False
    
    print(f"✅ Token found: {token[:8]}{'*' * (len(token) - 8)}")
    
    # Initialize service
    service = RealGitHubService(access_token=token)
    
    # Test 1: Get user events
    print("\n📊 Testing user events API...")
    try:
        events = service.get_user_events("aniket-bit7")
        print(f"✅ Successfully fetched {len(events)} events for aniket-bit7")
        
        # Show some sample events
        if events:
            print("📝 Sample events:")
            for event in events[:3]:
                print(f"  - {event.get('type', 'Unknown')} on {event.get('created_at', 'Unknown date')}")
    except Exception as e:
        print(f"❌ Failed to fetch user events: {e}")
        return False
    
    # Test 2: Get repository issues
    print("\n🐛 Testing repository issues API...")
    try:
        issues = service.get_repo_issues("microsoft", "vscode")
        print(f"✅ Successfully fetched {len(issues)} issues from microsoft/vscode")
        
        # Show some sample issues
        if issues:
            print("📝 Sample issues:")
            for issue in issues[:3]:
                print(f"  - #{issue.get('number', 'N/A')}: {issue.get('title', 'No title')[:50]}...")
    except Exception as e:
        print(f"❌ Failed to fetch repository issues: {e}")
        return False
    
    # Test 3: Check rate limits
    print("\n📈 Checking API rate limits...")
    try:
        rate_limit = service.get_rate_limit()
        if rate_limit:
            core_limit = rate_limit.get('resources', {}).get('core', {})
            remaining = core_limit.get('remaining', 0)
            limit = core_limit.get('limit', 0)
            reset_time = core_limit.get('reset', 0)
            
            print(f"✅ Rate limit status: {remaining}/{limit} requests remaining")
            print(f"📅 Resets at: {datetime.fromtimestamp(reset_time)}")
        else:
            print("⚠️  Could not fetch rate limit info")
    except Exception as e:
        print(f"❌ Failed to check rate limits: {e}")
    
    print("\n🎉 GitHub API test completed successfully!")
    return True

if __name__ == "__main__":
    from datetime import datetime
    test_github_api()
