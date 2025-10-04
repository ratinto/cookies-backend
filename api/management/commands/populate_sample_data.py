from django.core.management.base import BaseCommand
from api.models import ContributorProfile, Issue, Repository
from datetime import datetime, timezone


class Command(BaseCommand):
    help = 'Populate database with sample data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create sample repositories
        repositories_data = [
            {
                "name": "awesome-project",
                "full_name": "johndoe/awesome-project",
                "github_id": 1001,
                "owner": "johndoe",
                "description": "An awesome open source project",
                "url": "https://github.com/johndoe/awesome-project",
                "language": "Python",
                "stars_count": 1250,
                "forks_count": 89
            },
            {
                "name": "cool-library",
                "full_name": "janedoe/cool-library",
                "github_id": 1002,
                "owner": "janedoe",
                "description": "A cool JavaScript library",
                "url": "https://github.com/janedoe/cool-library",
                "language": "JavaScript",
                "stars_count": 856,
                "forks_count": 45
            },
            {
                "name": "utility-tools",
                "full_name": "devuser/utility-tools",
                "github_id": 1003,
                "owner": "devuser",
                "description": "Collection of utility tools",
                "url": "https://github.com/devuser/utility-tools",
                "language": "TypeScript",
                "stars_count": 324,
                "forks_count": 28
            }
        ]

        for data in repositories_data:
            repo, created = Repository.objects.get_or_create(
                name=data["name"],
                defaults=data
            )
            if created:
                self.stdout.write(f'Created repository: {repo.name}')
            else:
                self.stdout.write(f'Repository already exists: {repo.name}')

        # Create sample contributors
        contributors_data = [
            {
                "username": "johndoe",
                "github_id": 2001,
                "profile_url": "https://github.com/johndoe",
                "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=johndoe",
                "trust_score": 8.5,
                "activity_score": 7.8,
                "total_claims": 25,
                "completed_claims": 24,
                "ai_tags": ["reliable", "experienced"]
            },
            {
                "username": "janedoe",
                "github_id": 2002,
                "profile_url": "https://github.com/janedoe",
                "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=janedoe",
                "trust_score": 9.2,
                "activity_score": 8.5,
                "total_claims": 18,
                "completed_claims": 18,
                "ai_tags": ["reliable", "expert", "helpful"]
            },
            {
                "username": "devuser",
                "github_id": 2003,
                "profile_url": "https://github.com/devuser",
                "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=devuser",
                "trust_score": 7.6,
                "activity_score": 6.8,
                "total_claims": 20,
                "completed_claims": 17,
                "ai_tags": ["moderate", "improving"]
            },
            {
                "username": "opensourcefan",
                "github_id": 2004,
                "profile_url": "https://github.com/opensourcefan",
                "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=opensourcefan",
                "trust_score": 6.8,
                "activity_score": 5.5,
                "total_claims": 25,
                "completed_claims": 20,
                "ai_tags": ["inconsistent", "needs_guidance"]
            },
            {
                "username": "codelover",
                "github_id": 2005,
                "profile_url": "https://github.com/codelover",
                "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=codelover",
                "trust_score": 8.8,
                "activity_score": 9.1,
                "total_claims": 30,
                "completed_claims": 30,
                "ai_tags": ["reliable", "expert", "prolific"]
            }
        ]

        for data in contributors_data:
            contributor, created = ContributorProfile.objects.get_or_create(
                username=data["username"],
                defaults=data
            )
            if created:
                self.stdout.write(f'Created contributor: {contributor.username}')
            else:
                self.stdout.write(f'Contributor already exists: {contributor.username}')

        # Create sample issues
        repositories = Repository.objects.all()
        contributors = ContributorProfile.objects.all()

        issues_data = [
            {
                "issue_id": 1001,
                "issue_number": 1,
                "title": "Add dark mode support",
                "body": "Users have requested dark mode support for better user experience",
                "state": "open",
                "assignee": "johndoe",
                "labels": ["enhancement", "ui"],
                "url": "https://github.com/johndoe/awesome-project/issues/1",
                "complexity_score": 3.5
            },
            {
                "issue_id": 1002,
                "issue_number": 5,
                "title": "Fix memory leak in data processing",
                "body": "Memory usage keeps increasing during large data processing operations",
                "state": "open",
                "assignee": "janedoe",
                "labels": ["bug", "performance"],
                "url": "https://github.com/janedoe/cool-library/issues/5",
                "complexity_score": 5.0
            },
            {
                "issue_id": 1003,
                "issue_number": 12,
                "title": "Update documentation for new API",
                "body": "Documentation needs to be updated to reflect the new API changes",
                "state": "open",
                "assignee": "",
                "labels": ["documentation"],
                "url": "https://github.com/devuser/utility-tools/issues/12",
                "complexity_score": 2.0
            },
            {
                "issue_id": 1004,
                "issue_number": 23,
                "title": "Implement user authentication",
                "body": "Add JWT-based authentication system for the application",
                "state": "open",
                "assignee": "devuser",
                "labels": ["feature", "security"],
                "url": "https://github.com/johndoe/awesome-project/issues/23",
                "complexity_score": 7.5
            },
            {
                "issue_id": 1005,
                "issue_number": 8,
                "title": "Optimize database queries",
                "body": "Some database queries are running slowly and need optimization",
                "state": "open",
                "assignee": "codelover",
                "labels": ["performance", "database"],
                "url": "https://github.com/janedoe/cool-library/issues/8",
                "complexity_score": 6.0
            }
        ]

        for i, data in enumerate(issues_data):
            repo = repositories[i % len(repositories)]
            issue, created = Issue.objects.get_or_create(
                title=data["title"],
                defaults={
                    **data,
                    "repository": repo
                }
            )
            if created:
                self.stdout.write(f'Created issue: {issue.title}')
            else:
                self.stdout.write(f'Issue already exists: {issue.title}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )
        
        # Print summary
        self.stdout.write('\nSummary:')
        self.stdout.write(f'Repositories: {Repository.objects.count()}')
        self.stdout.write(f'Contributors: {ContributorProfile.objects.count()}')
        self.stdout.write(f'Issues: {Issue.objects.count()}')
