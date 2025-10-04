"""
Gemini AI service for analyzing contributor behavior and generating trust scores
"""
import google.generativeai as genai
from django.conf import settings
import json
import hashlib
from typing import Dict, List, Optional, Tuple
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class GeminiTrustAnalyzer:
    """AI-powered trust analysis using Gemini"""
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def analyze_comments_quality(self, comments: List[Dict]) -> Dict:
        """Analyze the quality of GitHub comments"""
        if not comments:
            return {
                'overall_score': 0.0,
                'helpfulness_avg': 0.0,
                'technical_accuracy_avg': 0.0,
                'communication_clarity_avg': 0.0,
                'insights': ['No comments to analyze']
            }
        
        # Prepare comment text for analysis
        comment_texts = []
        for comment in comments[:10]:  # Analyze up to 10 recent comments
            comment_texts.append({
                'body': comment.get('body', ''),
                'created_at': comment.get('created_at', ''),
                'url': comment.get('html_url', '')
            })
        
        prompt = self._create_comment_analysis_prompt(comment_texts)
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_comment_analysis_response(response.text)
        except Exception as e:
            logger.error(f"Gemini comment analysis failed: {e}")
            return self._get_default_comment_analysis()

    def analyze_behavioral_patterns(self, activity_data: Dict) -> Dict:
        """Analyze behavioral patterns from GitHub activity"""
        prompt = self._create_behavioral_analysis_prompt(activity_data)
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_behavioral_analysis_response(response.text)
        except Exception as e:
            logger.error(f"Gemini behavioral analysis failed: {e}")
            return self._get_default_behavioral_analysis()

    def detect_cookie_licking_patterns(self, contributor_history: Dict) -> Dict:
        """Detect cookie-licking behavior patterns"""
        prompt = self._create_cookie_licking_detection_prompt(contributor_history)
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_cookie_licking_response(response.text)
        except Exception as e:
            logger.error(f"Gemini cookie-licking detection failed: {e}")
            return self._get_default_cookie_licking_analysis()

    def generate_personalized_reminder(self, contributor_data: Dict, issue_data: Dict) -> str:
        """Generate a personalized reminder message"""
        prompt = self._create_reminder_generation_prompt(contributor_data, issue_data)
        
        try:
            response = self.model.generate_content(prompt)
            return self._extract_reminder_message(response.text)
        except Exception as e:
            logger.error(f"Gemini reminder generation failed: {e}")
            return self._get_default_reminder_message(contributor_data['username'])

    def _create_comment_analysis_prompt(self, comments: List[Dict]) -> str:
        """Create prompt for comment quality analysis"""
        comments_text = "\n\n".join([
            f"Comment {i+1}:\n{comment['body']}" 
            for i, comment in enumerate(comments)
        ])
        
        return f"""
Analyze these GitHub issue comments for quality and helpfulness. Rate each aspect on a scale of 0-10:

Comments to analyze:
{comments_text}

Please provide analysis in this JSON format:
{{
    "overall_score": <0-10>,
    "helpfulness_avg": <0-10>,
    "technical_accuracy_avg": <0-10>,
    "communication_clarity_avg": <0-10>,
    "insights": [
        "Key insight 1",
        "Key insight 2"
    ],
    "strengths": [
        "Strength 1",
        "Strength 2"
    ],
    "areas_for_improvement": [
        "Area 1",
        "Area 2"
    ]
}}

Consider:
- Technical accuracy and depth
- Helpfulness to issue resolution
- Communication clarity and professionalism
- Problem-solving approach
- Engagement quality (specific vs generic responses)
"""

    def _create_behavioral_analysis_prompt(self, activity_data: Dict) -> str:
        """Create prompt for behavioral pattern analysis"""
        return f"""
Analyze this GitHub contributor's behavioral patterns based on their activity:

Activity Data:
- Recent Events: {json.dumps(activity_data.get('events', [])[:10], indent=2)}
- Contribution Stats: {json.dumps(activity_data.get('stats', {}), indent=2)}
- Repository Involvement: {json.dumps(activity_data.get('repos', []), indent=2)}

Please analyze and return JSON format:
{{
    "consistency_score": <0-10>,
    "engagement_authenticity": <0-10>,
    "collaboration_quality": <0-10>,
    "reliability_indicators": [
        "Indicator 1",
        "Indicator 2"
    ],
    "risk_factors": [
        "Risk 1",
        "Risk 2"
    ],
    "behavioral_tags": [
        "Tag1",
        "Tag2"
    ]
}}

Evaluate:
- Consistency in contributions over time
- Quality of engagement (not just quantity)
- Collaboration patterns with other developers
- Signs of genuine interest vs superficial participation
- Reliability indicators from past behavior
"""

    def _create_cookie_licking_detection_prompt(self, history: Dict) -> str:
        """Create prompt for cookie-licking detection"""
        return f"""
Analyze this contributor's history to detect "cookie-licking" behavior patterns.

Cookie-licking means: claiming issues but not following through, blocking others from contributing.

Contributor History:
{json.dumps(history, indent=2)}

Analyze for these patterns and return JSON:
{{
    "cookie_licking_risk": <0-10>,
    "confidence_level": <0-10>,
    "detected_patterns": [
        "Pattern 1",
        "Pattern 2"
    ],
    "evidence": [
        "Evidence 1",
        "Evidence 2"
    ],
    "recommendations": [
        "Recommendation 1",
        "Recommendation 2"
    ]
}}

Look for:
- Claims without follow-through
- Multiple simultaneous claims across repositories
- Pattern of abandoning issues after claiming
- Generic claiming comments vs specific engagement
- Time between claim and actual work starting
"""

    def _create_reminder_generation_prompt(self, contributor_data: Dict, issue_data: Dict) -> str:
        """Create prompt for personalized reminder generation"""
        return f"""
Generate a polite, personalized reminder message for a GitHub contributor who claimed an issue but has been inactive.

Contributor Info:
- Username: {contributor_data.get('username')}
- Trust Score: {contributor_data.get('trust_score', 0)}
- Past Behavior: {contributor_data.get('behavioral_summary', 'Unknown')}

Issue Info:
- Title: {issue_data.get('title')}
- Days Since Claimed: {issue_data.get('days_since_claimed', 0)}
- Complexity: {issue_data.get('complexity', 'Unknown')}

Generate a message that is:
- Polite and encouraging
- Personalized based on their past contributions
- Offers help if needed
- Gives them an easy way to unclaim if needed
- Professional tone

Return just the message text, no additional formatting.
"""

    def _parse_comment_analysis_response(self, response: str) -> Dict:
        """Parse Gemini response for comment analysis"""
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            pass
        
        return self._get_default_comment_analysis()

    def _parse_behavioral_analysis_response(self, response: str) -> Dict:
        """Parse Gemini response for behavioral analysis"""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            pass
        
        return self._get_default_behavioral_analysis()

    def _parse_cookie_licking_response(self, response: str) -> Dict:
        """Parse Gemini response for cookie-licking detection"""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            pass
        
        return self._get_default_cookie_licking_analysis()

    def _extract_reminder_message(self, response: str) -> str:
        """Extract reminder message from Gemini response"""
        # Clean up the response and return the message
        lines = response.strip().split('\n')
        message_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('```') and not line.startswith('#'):
                message_lines.append(line)
        
        return '\n'.join(message_lines)

    def _get_default_comment_analysis(self) -> Dict:
        """Default comment analysis when AI fails"""
        return {
            'overall_score': 5.0,
            'helpfulness_avg': 5.0,
            'technical_accuracy_avg': 5.0,
            'communication_clarity_avg': 5.0,
            'insights': ['Analysis unavailable - using default scores'],
            'strengths': [],
            'areas_for_improvement': []
        }

    def _get_default_behavioral_analysis(self) -> Dict:
        """Default behavioral analysis when AI fails"""
        return {
            'consistency_score': 5.0,
            'engagement_authenticity': 5.0,
            'collaboration_quality': 5.0,
            'reliability_indicators': [],
            'risk_factors': [],
            'behavioral_tags': ['Analysis Pending']
        }

    def _get_default_cookie_licking_analysis(self) -> Dict:
        """Default cookie-licking analysis when AI fails"""
        return {
            'cookie_licking_risk': 5.0,
            'confidence_level': 0.0,
            'detected_patterns': [],
            'evidence': [],
            'recommendations': ['Requires manual review']
        }

    def _get_default_reminder_message(self, username: str) -> str:
        """Default reminder message when AI fails"""
        return f"""Hi @{username}! 

I hope you're doing well. I noticed you expressed interest in working on this issue a few days ago. 

Are you still planning to work on this? If you need any help or have questions, please let us know. If you're no longer able to work on it, no worries at all - just let us know so we can make it available for other contributors.

Thanks for your understanding! 🙂"""

    def calculate_enhanced_trust_score(self, base_score: float, ai_analyses: Dict) -> float:
        """Calculate final trust score combining base score with AI analysis"""
        # Base activity score (40% weight)
        base_weighted = base_score * 0.4
        
        # AI analysis scores (60% weight total)
        comment_quality = ai_analyses.get('comment_quality', {}).get('overall_score', 5.0)
        behavioral_score = ai_analyses.get('behavioral', {}).get('consistency_score', 5.0)
        engagement_auth = ai_analyses.get('behavioral', {}).get('engagement_authenticity', 5.0)
        cookie_licking_risk = ai_analyses.get('cookie_licking', {}).get('cookie_licking_risk', 5.0)
        
        # Weight the AI components
        ai_weighted = (
            comment_quality * 0.25 +      # 25% of total (comment quality)
            behavioral_score * 0.15 +     # 15% of total (behavioral consistency)
            engagement_auth * 0.15 +      # 15% of total (engagement authenticity)
            (10 - cookie_licking_risk) * 0.05  # 5% of total (inverse of cookie-licking risk)
        ) * 6  # Scale to 60% weight
        
        final_score = base_weighted + ai_weighted
        return min(final_score, 100.0)  # Cap at 100
