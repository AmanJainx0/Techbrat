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
    path('courses/', views.courses, name='courses'),
    path('books/', views.books, name='books'),
    path('tools/', views.tools, name='tools'),
    path('motivation/', views.motivation, name='motivation'),


    # APIs
    path('api/roadmap/', views.get_roadmap, name='get_roadmap'),
    path('api/generate-roadmap/', views.generate_roadmap, name='generate_roadmap'),
    path('api/issue-assistance/', views.issue_assistance, name='issue_assistance'),
    path('api/career-guidance/', views.career_guidance, name='career_guidance'),
    path('api/filter-courses/', views.filter_courses, name='filter_courses'),
    path('api/book-recommendations/', views.book_recommendations, name='book_recommendations'),
    path('api/filter-books/', views.filter_books, name='filter_books'),
    path('api/filter-tools/', views.filter_tools, name='filter_tools'),
    path('api/tools-recommendations/', views.tools_recommendations, name='tools_recommendations'),
    path('api/filter-tips/', views.filter_tips, name='filter_tips'),
    path('api/tips-recommendations/', views.tips_recommendations, name='tips_recommendations'),
]

