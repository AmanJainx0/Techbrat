from django.urls import path
from . import views

app_name = "techbrat"

urlpatterns = [
    # Pages
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),
    path('issue/', views.issue, name='issue'),
    path('issue-snapshots/<int:pk>/', views.issue_snapshot_detail, name='issue_snapshot_detail'),
    path('company-prep/', views.generate_company_prep, name='company_prep'),
    path('que/', views.que, name='que'),
    path('roadmap/', views.roadmap, name='roadmap'),
    path('roadmaps/<int:pk>/', views.roadmap_snapshot_detail, name='roadmap_snapshot_detail'),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('welcome/', views.welcome, name='welcome'),
    path('signout/', views.signout, name='signout'),
    path('profile/', views.profile, name='profile'),
    path('progress/', views.progress_dashboard, name='progress_dashboard'),
    path('job-readiness/', views.job_readiness_page, name='job_readiness'),
    path('skill-gap/', views.skill_gap_page, name='skill_gap'),
    path('action-plan/', views.action_plan_page, name='action_plan'),
    path('portfolio-guidance/', views.portfolio_guidance_page, name='portfolio_guidance'),
    path('application-readiness/', views.application_readiness_page, name='application_readiness'),
    path('opportunity-hub/', views.opportunity_hub_page, name='opportunity_hub'),
    path('saved/', views.saved_items, name='saved_items'),
    path('courses/', views.courses, name='courses'),
    path('courses/<int:pk>/', views.course_detail, name='course_detail'),
    path('books/', views.books, name='books'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('career-paths/<int:pk>/', views.career_path_detail, name='career_path_detail'),
    path('company-prep/<int:pk>/', views.company_prep_detail, name='company_prep_detail'),
    path('tools/', views.tools, name='tools'),
    path('tools/<int:pk>/', views.tool_detail, name='tool_detail'),
    path('motivation/', views.motivation, name='motivation'),
    path('tips/<int:pk>/', views.tip_detail, name='tip_detail'),
    path('save/toggle/', views.toggle_save, name='toggle_save'),
    path('save/career-path/', views.save_career_path, name='save_career_path'),
    path('save/company-prep/', views.save_company_prep_snapshot, name='save_company_prep_snapshot'),
    path('save/issue-assistance/', views.save_issue_snapshot, name='save_issue_snapshot'),
    path('save/roadmap/', views.save_roadmap_snapshot, name='save_roadmap_snapshot'),


    # APIs
    path('api/roadmap/', views.get_roadmap, name='get_roadmap'),
    path('api/generate-roadmap/', views.generate_roadmap, name='generate_roadmap'),
    path('api/issue-assistance/', views.issue_assistance, name='issue_assistance'),
    path('api/career-guidance/', views.career_guidance, name='career_guidance'),
    path('api/filter-courses/', views.filter_courses, name='filter_courses'),
    path('api/roadmap-progress/toggle/', views.toggle_roadmap_step_progress, name='toggle_roadmap_step_progress'),
    path('api/weekly-goal/', views.update_weekly_goal, name='update_weekly_goal'),
    path('api/book-recommendations/', views.book_recommendations, name='book_recommendations'),
    path('api/filter-books/', views.filter_books, name='filter_books'),
    path('api/opportunities/live/', views.live_opportunities, name='live_opportunities'),
    path('api/filter-tools/', views.filter_tools, name='filter_tools'),
    path('api/tools-recommendations/', views.tools_recommendations, name='tools_recommendations'),
    path('api/filter-tips/', views.filter_tips, name='filter_tips'),
    path('api/tips-recommendations/', views.tips_recommendations, name='tips_recommendations'),
]

