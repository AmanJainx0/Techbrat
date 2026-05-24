import json
from pathlib import Path

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from techbrat.models import (
    CareerPathSnapshot,
    CompanyPrepSnapshot,
    Course,
    IssueAssistanceSnapshot,
    LearningActivity,
    RoadmapStepProgress,
    RoadmapSnapshot,
    SavedItem,
    WeeklyGoal,
)


class PublicPagesTests(TestCase):
    def test_public_pages_render(self):
        for path in ['/', '/index/', '/roadmap/', '/tools/', '/motivation/']:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)

    def test_login_required_pages_redirect_anonymous_users(self):
        for path in ['/books/', '/courses/', '/profile/', '/welcome/', '/job-readiness/', '/skill-gap/', '/action-plan/', '/portfolio-guidance/', '/application-readiness/', '/opportunity-hub/']:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 302)

    def test_roadmap_api_reads_bundled_json(self):
        response = self.client.get(reverse('techbrat:get_roadmap'))
        self.assertEqual(response.status_code, 200)

        expected = json.loads(
            (Path(__file__).resolve().parent / 'data' / 'backend_roadmap.json').read_text(
                encoding='utf-8'
            )
        )
        self.assertEqual(response.json(), expected)


class SavedItemsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='saveuser@example.com',
            email='saveuser@example.com',
            password='password123',
        )
        self.course = Course.objects.create(
            title='Django Foundations',
            platform='TechBrat',
            domain='Backend Development',
            level='beginner',
            learning_type='video',
            duration='4 hours',
            is_free=True,
            link='https://example.com/django-foundations',
            description='Learn Django fundamentals.',
        )

    def test_toggle_save_creates_and_removes_saved_item(self):
        self.client.login(username='saveuser@example.com', password='password123')

        response = self.client.post(
            reverse('techbrat:toggle_save'),
            data=json.dumps({'object_id': self.course.pk, 'content_type': 'course'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['saved'])
        self.assertTrue(SavedItem.objects.filter(user=self.user, object_id=self.course.pk).exists())

        response = self.client.post(
            reverse('techbrat:toggle_save'),
            data=json.dumps({'object_id': self.course.pk, 'content_type': 'course'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['saved'])
        self.assertFalse(SavedItem.objects.filter(user=self.user, object_id=self.course.pk).exists())

    def test_saved_items_page_uses_get_absolute_url(self):
        self.client.login(username='saveuser@example.com', password='password123')
        SavedItem.objects.create(
            user=self.user,
            content_type=ContentType.objects.get_for_model(Course),
            object_id=self.course.pk,
        )

        response = self.client.get(reverse('techbrat:saved_items'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.course.get_absolute_url())

    def test_save_career_path_creates_snapshot(self):
        self.client.login(username='saveuser@example.com', password='password123')

        response = self.client.post(
            reverse('techbrat:save_career_path'),
            data=json.dumps({
                'career': {
                    'career_name': 'Backend Developer',
                    'simple_explanation': 'Build APIs and services',
                    'why_suitable': 'Strong fit for problem solvers',
                    'future_scope': 'High demand',
                    'beginner_roadmap': ['Learn Python', 'Build APIs'],
                    'beginner_resources': [{'title': 'Docs', 'type': 'Documentation', 'link': 'https://example.com'}],
                }
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['saved'])
        self.assertEqual(CareerPathSnapshot.objects.filter(user=self.user).count(), 1)

    def test_save_roadmap_creates_snapshot(self):
        self.client.login(username='saveuser@example.com', password='password123')

        response = self.client.post(
            reverse('techbrat:save_roadmap_snapshot'),
            data=json.dumps({
                'prompt': 'MERN roadmap',
                'roadmap': {
                    'roadmap_title': 'MERN Roadmap',
                    'steps': [
                        {
                            'title': 'Learn JavaScript',
                            'description': 'Start with JS basics',
                            'resources': [{'title': 'MDN', 'link': 'https://developer.mozilla.org'}],
                        }
                    ],
                },
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['saved'])
        self.assertEqual(RoadmapSnapshot.objects.filter(user=self.user).count(), 1)

    def test_toggle_roadmap_step_progress_updates_completion(self):
        self.client.login(username='saveuser@example.com', password='password123')
        snapshot = RoadmapSnapshot.objects.create(
            user=self.user,
            title='MERN Roadmap',
            prompt='MERN roadmap',
            summary='Start with JavaScript',
            fingerprint='roadmap-fingerprint',
            payload={
                'prompt': 'MERN roadmap',
                'roadmap': {
                    'roadmap_title': 'MERN Roadmap',
                    'steps': [
                        {'title': 'Learn JavaScript', 'description': 'Basics', 'resources': []},
                        {'title': 'Learn React', 'description': 'Components', 'resources': []},
                    ],
                },
            },
        )

        response = self.client.post(
            reverse('techbrat:toggle_roadmap_step_progress'),
            data=json.dumps({'snapshot_id': snapshot.pk, 'step_index': 0}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['completed'])
        self.assertEqual(response.json()['completed_steps'], 1)
        self.assertEqual(response.json()['completion_percentage'], 50)
        self.assertTrue(RoadmapStepProgress.objects.filter(snapshot=snapshot, step_index=0).exists())

        response = self.client.post(
            reverse('techbrat:toggle_roadmap_step_progress'),
            data=json.dumps({'snapshot_id': snapshot.pk, 'step_index': 0}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['completed'])
        self.assertEqual(response.json()['completed_steps'], 0)
        self.assertFalse(RoadmapStepProgress.objects.filter(snapshot=snapshot, step_index=0).exists())

    def test_progress_dashboard_renders_saved_roadmap_progress(self):
        self.client.login(username='saveuser@example.com', password='password123')
        snapshot = RoadmapSnapshot.objects.create(
            user=self.user,
            title='Backend Roadmap',
            prompt='backend roadmap',
            summary='Start with Python',
            fingerprint='backend-roadmap-fingerprint',
            payload={
                'prompt': 'backend roadmap',
                'roadmap': {
                    'roadmap_title': 'Backend Roadmap',
                    'steps': [
                        {'title': 'Learn Python', 'description': 'Syntax', 'resources': []},
                        {'title': 'Learn Django', 'description': 'Views', 'resources': []},
                    ],
                },
            },
        )
        RoadmapStepProgress.objects.create(user=self.user, snapshot=snapshot, step_index=0)

        response = self.client.get(reverse('techbrat:progress_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Backend Roadmap')
        self.assertContains(response, '50%')
        self.assertContains(response, 'Action Plan')
        self.assertContains(response, 'Learn Django')
        self.assertContains(response, 'Project Guidance')
        self.assertContains(response, 'Backend Portfolio Builder')

    def test_toggle_roadmap_step_progress_records_learning_activity(self):
        self.client.login(username='saveuser@example.com', password='password123')
        snapshot = RoadmapSnapshot.objects.create(
            user=self.user,
            title='Python Roadmap',
            prompt='python roadmap',
            summary='Start with syntax',
            fingerprint='python-roadmap-fingerprint',
            payload={
                'prompt': 'python roadmap',
                'roadmap': {
                    'roadmap_title': 'Python Roadmap',
                    'steps': [
                        {'title': 'Learn Python Syntax', 'description': 'Syntax', 'resources': []},
                    ],
                },
            },
        )

        self.client.post(
            reverse('techbrat:toggle_roadmap_step_progress'),
            data=json.dumps({'snapshot_id': snapshot.pk, 'step_index': 0}),
            content_type='application/json',
        )
        self.assertEqual(
            LearningActivity.objects.filter(
                user=self.user,
                activity_type='roadmap_step_completed',
            ).count(),
            1,
        )

    def test_update_weekly_goal_creates_goal(self):
        self.client.login(username='saveuser@example.com', password='password123')
        response = self.client.post(
            reverse('techbrat:update_weekly_goal'),
            data=json.dumps({'target_steps': 7}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(WeeklyGoal.objects.filter(user=self.user).count(), 1)
        self.assertEqual(WeeklyGoal.objects.get(user=self.user).target_steps, 7)

    def test_profile_shows_job_readiness_summary(self):
        self.client.login(username='saveuser@example.com', password='password123')
        response = self.client.get(reverse('techbrat:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Job Readiness')
        self.assertContains(response, 'Open Guidance Tools')

    def test_guidance_pages_render_for_logged_in_user(self):
        self.client.login(username='saveuser@example.com', password='password123')

        progress_response = self.client.get(reverse('techbrat:progress_dashboard'))
        self.assertEqual(progress_response.status_code, 200)
        self.assertContains(progress_response, 'Career Growth Hub')
        self.assertContains(progress_response, 'Application Readiness')

        readiness_response = self.client.get(reverse('techbrat:job_readiness'))
        self.assertEqual(readiness_response.status_code, 302)
        self.assertIn(reverse('techbrat:progress_dashboard'), readiness_response.url)

        skill_gap_response = self.client.get(reverse('techbrat:skill_gap'))
        self.assertEqual(skill_gap_response.status_code, 302)
        self.assertIn(reverse('techbrat:progress_dashboard'), skill_gap_response.url)

        action_plan_response = self.client.get(reverse('techbrat:action_plan'))
        self.assertEqual(action_plan_response.status_code, 302)
        self.assertIn(reverse('techbrat:progress_dashboard'), action_plan_response.url)

        portfolio_response = self.client.get(reverse('techbrat:portfolio_guidance'))
        self.assertEqual(portfolio_response.status_code, 302)
        self.assertIn(reverse('techbrat:progress_dashboard'), portfolio_response.url)

        application_response = self.client.get(reverse('techbrat:application_readiness'))
        self.assertEqual(application_response.status_code, 302)
        self.assertIn(reverse('techbrat:progress_dashboard'), application_response.url)

        opportunity_response = self.client.get(reverse('techbrat:opportunity_hub'))
        self.assertEqual(opportunity_response.status_code, 200)
        self.assertContains(opportunity_response, 'Opportunity Hub')
        self.assertContains(opportunity_response, 'Matched Opportunities')

    def test_progress_dashboard_shows_main_blockers(self):
        self.client.login(username='saveuser@example.com', password='password123')
        response = self.client.get(reverse('techbrat:progress_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Main blockers')
        self.assertContains(response, 'Skill Gap Engine')
        self.assertContains(response, 'Action Plan')

    def test_save_issue_guidance_creates_snapshot(self):
        self.client.login(username='saveuser@example.com', password='password123')

        response = self.client.post(
            reverse('techbrat:save_issue_snapshot'),
            data=json.dumps({
                'issue': 'I am confused about SQL joins',
                'guidance': {
                    'issue_detected': 'SQL joins confusion',
                    'simple_explanation': 'Joins combine related rows.',
                    'alternative_learning': 'Practice with two small tables.',
                    'practice_or_example': 'Write 10 join queries.',
                    'motivation_boost': 'You will get this with repetition.',
                },
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['saved'])
        self.assertEqual(IssueAssistanceSnapshot.objects.filter(user=self.user).count(), 1)

    def test_save_company_prep_creates_snapshot(self):
        self.client.login(username='saveuser@example.com', password='password123')

        response = self.client.post(
            reverse('techbrat:save_company_prep_snapshot'),
            data=json.dumps({
                'company': 'Meta',
                'role': 'Data Analyst',
                'prep_inputs': {'hours_per_day': 2, 'total_time': '1 month'},
                'plan_text': 'Target\n- Meta - Data Analyst\n\nFinal Strategy\n- Revise daily',
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['saved'])
        self.assertEqual(CompanyPrepSnapshot.objects.filter(user=self.user).count(), 1)


class CompanyPrepTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='prepuser@example.com',
            email='prepuser@example.com',
            password='password123',
        )

    def test_company_prep_page_requires_login(self):
        response = self.client.get(reverse('techbrat:company_prep'))
        self.assertEqual(response.status_code, 302)

    def test_company_prep_post_returns_plan(self):
        self.client.login(username='prepuser@example.com', password='password123')
        response = self.client.post(
            reverse('techbrat:company_prep'),
            data=json.dumps({
                'company': 'Google',
                'role': 'Data Analyst',
                'hours_per_day': 2,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['success'])
        self.assertIn('Target', payload['data'])
        self.assertIn('Google-Specific Tips', payload['data'])
        self.assertIn('SQL', payload['data'])

    def test_company_prep_validates_required_fields(self):
        self.client.login(username='prepuser@example.com', password='password123')
        response = self.client.post(
            reverse('techbrat:company_prep'),
            data=json.dumps({
                'company': '',
                'role': '',
                'hours_per_day': 0,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_company_prep_service_company_emphasizes_aptitude(self):
        self.client.login(username='prepuser@example.com', password='password123')
        response = self.client.post(
            reverse('techbrat:company_prep'),
            data=json.dumps({
                'company': 'TCS',
                'role': 'Backend Developer',
                'hours_per_day': 2,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn('Aptitude', payload['data'])
        self.assertIn('TCS-Specific Tips', payload['data'])
