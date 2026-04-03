"""Seed initial tools into the database."""
from django.core.management.base import BaseCommand
from techbrat.models import Tool


class Command(BaseCommand):
    help = 'Seed the database with curated technology tools and platforms'

    def handle(self, *args, **options):
        tools_data = [
            {
                'name': 'GitHub',
                'description': 'Version control platform and collaboration hub for developers worldwide',
                'category': 'version_control',
                'difficulty': 'beginner',
                'use_case': 'learning',
                'link': 'https://github.com',
                'is_ai_generated': False,
            },
            {
                'name': 'VS Code',
                'description': 'Lightweight but powerful source code editor with extensive extensions',
                'category': 'development',
                'difficulty': 'beginner',
                'use_case': 'production',
                'link': 'https://code.visualstudio.com',
                'is_ai_generated': False,
            },
            {
                'name': 'Docker',
                'description': 'Containerization platform for packaging applications and dependencies',
                'category': 'devops',
                'difficulty': 'intermediate',
                'use_case': 'production',
                'link': 'https://www.docker.com',
                'is_ai_generated': False,
            },
            {
                'name': 'Git',
                'description': 'Distributed version control system for tracking code changes',
                'category': 'version_control',
                'difficulty': 'beginner',
                'use_case': 'learning',
                'link': 'https://git-scm.com',
                'is_ai_generated': False,
            },
            {
                'name': 'LeetCode',
                'description': 'Platform for solving coding problems and practicing data structures',
                'category': 'practice_platform',
                'difficulty': 'all',
                'use_case': 'practice',
                'link': 'https://leetcode.com',
                'is_ai_generated': False,
            },
            {
                'name': 'React',
                'description': 'JavaScript library for building interactive user interfaces',
                'category': 'development',
                'difficulty': 'intermediate',
                'use_case': 'learning',
                'link': 'https://react.dev',
                'is_ai_generated': False,
            },
            {
                'name': 'Node.js',
                'description': 'JavaScript runtime for building server-side applications',
                'category': 'development',
                'difficulty': 'intermediate',
                'use_case': 'production',
                'link': 'https://nodejs.org',
                'is_ai_generated': False,
            },
            {
                'name': 'Figma',
                'description': 'Cloud-based design and prototyping tool for UI/UX designers',
                'category': 'design',
                'difficulty': 'beginner',
                'use_case': 'production',
                'link': 'https://www.figma.com',
                'is_ai_generated': False,
            },
            {
                'name': 'PostgreSQL',
                'description': 'Powerful open-source relational database system',
                'category': 'databases',
                'difficulty': 'intermediate',
                'use_case': 'production',
                'link': 'https://www.postgresql.org',
                'is_ai_generated': False,
            },
            {
                'name': 'Postman',
                'description': 'API development and testing platform for building better APIs',
                'category': 'api_tools',
                'difficulty': 'beginner',
                'use_case': 'practice',
                'link': 'https://www.postman.com',
                'is_ai_generated': False,
            },
            {
                'name': 'AWS',
                'description': 'Comprehensive cloud computing platform with multiple services',
                'category': 'cloud',
                'difficulty': 'intermediate',
                'use_case': 'production',
                'link': 'https://aws.amazon.com',
                'is_ai_generated': False,
            },
            {
                'name': 'Jenkins',
                'description': 'Open-source automation server for continuous integration/delivery',
                'category': 'ci_cd',
                'difficulty': 'advanced',
                'use_case': 'production',
                'link': 'https://www.jenkins.io',
                'is_ai_generated': False,
            },
            {
                'name': 'Slack',
                'description': 'Team communication platform for real-time messaging and collaboration',
                'category': 'collaboration',
                'difficulty': 'beginner',
                'use_case': 'production',
                'link': 'https://www.slack.com',
                'is_ai_generated': False,
            },
            {
                'name': 'MongoDB',
                'description': 'NoSQL database for flexible data storage and scalability',
                'category': 'databases',
                'difficulty': 'intermediate',
                'use_case': 'production',
                'link': 'https://www.mongodb.com',
                'is_ai_generated': False,
            },
            {
                'name': 'ChatGPT',
                'description': 'AI-powered conversational model for coding assistance and learning',
                'category': 'ai_tools',
                'difficulty': 'beginner',
                'use_case': 'learning',
                'link': 'https://chat.openai.com',
                'is_ai_generated': False,
            },
        ]

        created_count = 0
        skipped_count = 0

        for tool_data in tools_data:
            tool, created = Tool.objects.get_or_create(
                name=tool_data['name'],
                defaults=tool_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {tool.name}')
                )
            else:
                skipped_count += 1
                self.stdout.write(
                    self.style.WARNING(f'✗ Already exists: {tool.name}')
                )

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Seeding complete: {created_count} created, {skipped_count} skipped'
        ))
