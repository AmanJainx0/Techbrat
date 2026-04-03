"""Seed initial motivation tips into the database."""
from django.core.management.base import BaseCommand
from techbrat.models import Tip


class Command(BaseCommand):
    help = 'Seed the database with curated motivation and learning tips'

    def handle(self, *args, **options):
        tips_data = [
            {
                'title': 'Code Every Day, Even 15 Minutes',
                'explanation': 'Consistency beats marathon coding sessions. Daily practice builds muscle memory and deepens understanding.',
                'action_step': 'Open your current project and write 15 lines of code today.',
                'category': 'consistency',
                'icon': 'fa-fire',
                'daily_boost': True,
            },
            {
                'title': 'Build Projects, Not Just Tutorials',
                'explanation': 'Tutorials teach concepts but projects teach you how to think like a developer. You learn problem-solving, debugging, and architecture.',
                'action_step': 'Start a small project this week using what you learned from tutorials.',
                'category': 'coding_practice',
                'icon': 'fa-code',
            },
            {
                'title': 'Read Others\' Code',
                'explanation': 'Learning from well-written code improves your problem-solving skills. Open-source projects are free universities.',
                'action_step': 'Pick a GitHub project and study 3-5 functions from a file you find interesting.',
                'category': 'learning_strategy',
                'icon': 'fa-book',
            },
            {
                'title': 'Debug Like a Detective',
                'explanation': 'Debugging is where real learning happens. Reading error messages carefully and using tools like debuggers trains your problem-solving mind.',
                'action_step': 'Next time you hit a bug, spend 10 minutes understanding the error message before searching online.',
                'category': 'coding_practice',
                'icon': 'fa-magnifying-glass',
            },
            {
                'title': 'Learn One Thing Deep, Not Ten Things Shallow',
                'explanation': 'Master fundamentals first. Depth over breadth. A strong foundation in core concepts makes everything else easier.',
                'action_step': 'Pick one concept you\'ve been learning and go 2 levels deeper this week.',
                'category': 'learning_strategy',
                'icon': 'fa-brain',
            },
            {
                'title': 'Talk About Your Code',
                'explanation': 'Explaining your code to others (or rubber duck debugging) forces you to think clearly. Bugs become obvious.',
                'action_step': 'Find someone and explain what your code does in simple terms, or write a blog post about it.',
                'category': 'productivity',
                'icon': 'fa-comments',
            },
            {
                'title': 'Break Big Problems Into Tiny Problems',
                'explanation': 'Large projects feel overwhelming. Breaking them into small, solvable pieces makes progress visible and keeps motivation high.',
                'action_step': 'Take your current biggest challenge and break it into 5 smaller subtasks.',
                'category': 'productivity',
                'icon': 'fa-sitemap',
            },
            {
                'title': 'Mistakes Are Gifts in Disguise',
                'explanation': 'Every error you encounter teaches you something. The bugs you fix are lessons you\'ll remember forever.',
                'action_step': 'Keep a "learning journal" of bugs you fixed. Revisit it when you\'re discouraged.',
                'category': 'mindset',
                'icon': 'fa-gift',
            },
            {
                'title': 'Finish What You Start',
                'explanation': 'Completing projects, even small ones, builds confidence. Unfinished projects drain motivation. Done is better than perfect.',
                'action_step': 'Commit to finishing one small project this week, no matter what.',
                'category': 'consistency',
                'icon': 'fa-check-circle',
            },
            {
                'title': 'Invest in Your Why',
                'explanation': 'Remember why you started coding. Is it freedom? Impact? Creation? On hard days, that "why" is your fuel. Reconnect with it often.',
                'action_step': 'Write down 3 reasons you\'re learning to code. Put it somewhere visible.',
                'category': 'career_growth',
                'icon': 'fa-heart',
            },
            {
                'title': 'Practice With Purpose',
                'explanation': 'Don\'t practice randomly. Identify weak areas and practice those specifically. It\'s faster and more effective.',
                'action_step': 'List 3 coding skills you want to improve. Practice one for 30 minutes with focus.',
                'category': 'coding_practice',
                'icon': 'fa-target',
            },
            {
                'title': 'Network With Other Developers',
                'explanation': 'Speaking with other developers, online or offline, exposes you to new ideas, opportunities, and keeps you motivated.',
                'action_step': 'Join a developer community (Discord, Reddit, local meetup) and introduce yourself today.',
                'category': 'career_growth',
                'icon': 'fa-users',
            },
            {
                'title': 'Celebrate Small Wins',
                'explanation': 'Learning to code is a marathon. Celebrate each win - a working function, a bug fixed, a concept understood. It builds momentum.',
                'action_step': 'Every time you finish something, even something small, take a moment to feel proud.',
                'category': 'mindset',
                'icon': 'fa-star',
            },
            {
                'title': 'Version Control Is Your Best Friend',
                'explanation': 'GitHub/Git saves you from disasters and shows your progress. It\'s not optional - it\'s essential professional practice.',
                'action_step': 'If you haven\'t already, put your current project on GitHub starting today.',
                'category': 'productivity',
                'icon': 'fa-code-branch',
            },
            {
                'title': 'Teach What You Learn',
                'explanation': 'Teaching is the best way to learn. Explaining concepts to beginners forces you to understand them deeply.',
                'action_step': 'Write a simple explanation of one concept you just learned. Share it online or with a friend.',
                'category': 'learning_strategy',
                'icon': 'fa-chalkboard-user',
            },
        ]

        created_count = 0
        skipped_count = 0

        for tip_data in tips_data:
            tip, created = Tip.objects.get_or_create(
                title=tip_data['title'],
                defaults=tip_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {tip.title}')
                )
            else:
                skipped_count += 1
                self.stdout.write(
                    self.style.WARNING(f'✗ Already exists: {tip.title}')
                )

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Tips seeding complete: {created_count} created, {skipped_count} skipped'
        ))
