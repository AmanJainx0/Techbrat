from django.urls import path
from . import views

app_name = "techbrat"

urlpatterns = [
    # Pages
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),
    path('issue/', views.issue, name='issue'),
    path('que/', views.que, name='que'),
    path('roadmap/', views.roadmap, name='roadmap'),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('welcome/', views.welcome, name='welcome'),
    path('signout/', views.signout, name='signout'),
    path('profile/', views.profile, name='profile'),

    # APIs
    path('api/roadmap/', views.get_roadmap, name='get_roadmap'),
    path('api/generate-roadmap/', views.generate_roadmap, name='generate_roadmap'),
    path('api/issue-assistance/', views.issue_assistance, name='issue_assistance'),
    path('api/career-guidance/', views.career_guidance, name='career_guidance'),
]
