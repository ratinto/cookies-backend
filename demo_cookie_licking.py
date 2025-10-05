#!/usr/bin/env python
"""
Cookie-Licking Detection Demo Script
Demonstrates the real GitHub API integration and cookie-licking detection capabilities
"""

import requests
import json
import time
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000/api"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_json(data, title="Response"):
    """Pretty print JSON data"""
    print(f"\n{title}:")
    print(json.dumps(data, indent=2))

def test_health_check():
    """Test the API health check"""
    print_section("API HEALTH CHECK")
    
    response = requests.get(f"{BASE_URL}/health/")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API is healthy: {data['message']}")
        print(f"📊 Version: {data['version']}")
    else:
        print(f"❌ API health check failed: {response.status_code}")

def test_enhanced_stats():
    """Test the enhanced stats endpoint with GitHub integration"""
    print_section("ENHANCED STATISTICS WITH GITHUB INTEGRATION")
    
    response = requests.get(f"{BASE_URL}/stats/")
    if response.status_code == 200:
        data = response.json()
        
        print(f"📈 Database Statistics:")
        print(f"   • Contributors: {data['total_contributors']}")
        print(f"   • Issues: {data['total_issues']} (Open: {data['open_issues']})")
        print(f"   • Assigned Issues: {data['assigned_issues']}")
        print(f"   • Repositories: {data['repositories']}")
        print(f"   • Google Users: {data['google_users']}")
        
        print(f"\n🍪 Cookie-Licking Detection:")
        detection = data['cookie_licking_detection']
        print(f"   • Issues Analyzed: {detection['total_analyzed']}")
        print(f"   • High Risk: {detection['high_risk']}")
        print(f"   • Medium Risk: {detection['medium_risk']}")
        print(f"   • Low Risk: {detection['low_risk']}")
        print(f"   • Patterns Detected: {detection['patterns_detected']}")
        
        print(f"\n🔗 GitHub API Status: {data['github_api_status']}")
        
        print(f"\n🎯 Trust Score Distribution:")
        trust = data['trust_score_distribution']
        print(f"   • High Trust (80-100): {trust['high_trust']}")
        print(f"   • Medium Trust (50-79): {trust['medium_trust']}")
        print(f"   • Low Trust (<50): {trust['low_trust']}")
        print(f"   • Average Trust Score: {trust['average_trust']:.2f}")
    else:
        print(f"❌ Stats request failed: {response.status_code}")

def test_enhanced_contributors():
    """Test the enhanced contributors endpoint"""
    print_section("ENHANCED CONTRIBUTORS WITH GITHUB ANALYSIS")
    
    response = requests.get(f"{BASE_URL}/contributors/")
    if response.status_code == 200:
        data = response.json()
        
        print(f"👥 Found {data['total_count']} contributors")
        print(f"🔬 Enhanced with GitHub: {data['enhanced_with_github']}")
        
        for contributor in data['contributors'][:3]:  # Show top 3
            print(f"\n👤 {contributor['username']}:")
            print(f"   • Trust Score: {contributor['trust_score']}")
            print(f"   • Completion Rate: {contributor['completion_rate']}%")
            print(f"   • Primary Tag: {contributor['primary_tag']}")
            print(f"   • Claims: {contributor['completed_claims']}/{contributor['total_claims']}")
            
            # Show GitHub data if available
            if 'github_data' in contributor:
                gh = contributor['github_data']
                print(f"   • GitHub: {gh.get('public_repos', 0)} repos, {gh.get('followers', 0)} followers")
            
            if 'real_trust_score' in contributor:
                print(f"   • Real GitHub Trust Score: {contributor['real_trust_score']}")
    else:
        print(f"❌ Contributors request failed: {response.status_code}")

def test_enhanced_issues():
    """Test the enhanced issues endpoint with cookie-licking detection"""
    print_section("ISSUES WITH COOKIE-LICKING DETECTION")
    
    response = requests.get(f"{BASE_URL}/issues/")
    if response.status_code == 200:
        data = response.json()
        
        print(f"📋 Found {data['total_count']} issues")
        print(f"🍪 Cookie-licking detection: {data['cookie_licking_enabled']}")
        
        for issue in data['issues']:
            print(f"\n🎫 Issue #{issue['issue_number']}: {issue['title']}")
            print(f"   • Repository: {issue['repository_name']}")
            print(f"   • Assignee: {issue['assignee'] or 'Unassigned'}")
            print(f"   • Complexity: {issue['complexity_score']}")
            
            # Show cookie-licking analysis
            analysis = issue.get('cookie_licking_analysis', {})
            if 'error' in analysis:
                print(f"   • Analysis: ⚠️  {analysis['error']}")
            elif 'status' in analysis:
                print(f"   • Analysis: ℹ️  {analysis['message']}")
            else:
                risk = analysis.get('risk_level', 'unknown')
                print(f"   • Risk Level: {risk}")
                if analysis.get('recommendation'):
                    print(f"   • Recommendation: {analysis['recommendation']}")
    else:
        print(f"❌ Issues request failed: {response.status_code}")

def test_contributor_analysis():
    """Test the new contributor analysis endpoint"""
    print_section("REAL-TIME CONTRIBUTOR ANALYSIS")
    
    # Test with some well-known GitHub users
    test_users = ["torvalds", "defunkt", "mojombo"]
    
    for username in test_users:
        print(f"\n🔍 Analyzing GitHub user: {username}")
        
        response = requests.post(
            f"{BASE_URL}/analyze/contributor/",
            json={"username": username},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                user = data['user_details']
                trust = data['trust_analysis']
                activity = data['activity_analysis']
                
                print(f"   ✅ Found: {user['name']} (@{user['login']})")
                print(f"   • Account created: {user['created_at'][:10]}")
                print(f"   • Public repos: {user['public_repos']}")
                print(f"   • Followers: {user['followers']}")
                
                if trust['success']:
                    print(f"   • Trust Score: {trust['trust_score']}/100")
                    factors = trust['factors']
                    print(f"   • Account age: {factors['account_age_days']} days")
                    print(f"   • Recent events: {factors['recent_events']}")
                
                print(f"   • Active in {len(activity['repositories_active_in'])} repositories")
            else:
                print(f"   ❌ Analysis failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ Request failed: {response.status_code}")
        
        time.sleep(1)  # Rate limiting

def test_repository_analysis():
    """Test the repository analysis endpoint"""
    print_section("REPOSITORY HEALTH ANALYSIS")
    
    test_repos = ["microsoft/vscode", "facebook/react", "nodejs/node"]
    
    for repo in test_repos:
        print(f"\n🏛️  Analyzing repository: {repo}")
        
        response = requests.post(
            f"{BASE_URL}/analyze/repository/",
            json={"repository_url": repo},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                analysis = data['analysis']
                print(f"   ✅ Repository: {data['repository']}")
                print(f"   • Health Score: {analysis['health_score']}/100")
                print(f"   • Recommendations:")
                for rec in analysis['recommendations']:
                    print(f"     - {rec}")
            else:
                print(f"   ❌ Analysis failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ Request failed: {response.status_code}")
        
        time.sleep(1)  # Rate limiting

def demo_summary():
    """Print demo summary and next steps"""
    print_section("COOKIE-LICKING DETECTION SYSTEM SUMMARY")
    
    print("🎉 Demonstration Complete!")
    print("\n✨ Key Features Demonstrated:")
    print("   • Real GitHub API integration for user and repository analysis")
    print("   • Cookie-licking pattern detection in issue comments")
    print("   • Trust score calculation based on GitHub activity")
    print("   • Risk assessment for assigned but inactive issues")
    print("   • Enhanced dashboard with live GitHub data")
    print("   • Repository health monitoring")
    
    print("\n🔗 System Components:")
    print("   • Django backend with GitHub API service")
    print("   • React frontend with TypeScript and Tailwind CSS")
    print("   • Google OAuth authentication")
    print("   • Real-time GitHub data analysis")
    print("   • Cookie-licking detection algorithms")
    
    print("\n🌐 Access Points:")
    print("   • Frontend: http://localhost:5173")
    print("   • Backend API: http://localhost:8002/api")
    print("   • API Documentation: http://localhost:8002/api/info/")
    
    print("\n🚀 Next Steps:")
    print("   • Add GitHub API token for higher rate limits")
    print("   • Implement automated reminder system")
    print("   • Add email notifications for cookie-licking detection")
    print("   • Expand pattern recognition algorithms")
    print("   • Add machine learning for behavior prediction")

def main():
    """Run the complete demo"""
    print("🍪 Cookie-Licking Detection System Demo")
    print("=" * 60)
    print("This demo showcases the AI-powered system for detecting")
    print("and resolving issue assignment abandonment on GitHub.")
    print("\n⚡ Starting comprehensive system demonstration...")
    
    try:
        # Core API tests
        test_health_check()
        test_enhanced_stats()
        test_enhanced_contributors()
        test_enhanced_issues()
        
        # Real GitHub API tests (may hit rate limits without token)
        print("\n⚠️  Note: The following tests use real GitHub API calls")
        print("   and may hit rate limits without authentication.")
        
        test_contributor_analysis()
        test_repository_analysis()
        
        # Summary
        demo_summary()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
    
    print("\n🎯 Demo completed! Check the frontend at http://localhost:5173")

if __name__ == "__main__":
    main()
