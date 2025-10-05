#!/usr/bin/env python
"""
Simple test to isolate the GitHub API error
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

def simple_test():
    """Simple test to isolate the error"""
    print("🔍 Testing simple GitHub API call...")
    
    # Get token from settings
    token = getattr(settings, 'GITHUB_ACCESS_TOKEN', None)
    service = RealGitHubService(access_token=token)
    
    try:
        # Test 1: Get a small number of issues
        print("📋 Getting issues...")
        issues = service.get_repo_issues("microsoft", "vscode")
        print(f"✅ Got {len(issues)} issues")
        
        if issues:
            first_issue = issues[0]
            print(f"📝 First issue: #{first_issue.get('number')} - {first_issue.get('title', '')[:50]}")
            print(f"📅 Created: {first_issue.get('created_at')}")
            print(f"📅 Updated: {first_issue.get('updated_at')}")
            print(f"🆔 ID: {first_issue.get('id')} (type: {type(first_issue.get('id'))})")
            
            # Test 2: Get comments for this issue
            print(f"\n💬 Getting comments for issue #{first_issue.get('number')}...")
            comments = service.get_issue_comments("microsoft", "vscode", first_issue.get('number'))
            print(f"✅ Got {len(comments)} comments")
            
            if comments:
                first_comment = comments[0]
                print(f"👤 First comment by: {first_comment.get('user_login')}")
                print(f"🆔 User ID: {first_comment.get('user_id')} (type: {type(first_comment.get('user_id'))})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_test()
