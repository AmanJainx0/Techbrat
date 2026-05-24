from django.contrib import admin
from django.urls import path, include

from techbrat import views as techbrat_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'accounts/3rdparty/login/error/',
        techbrat_views.social_login_error_redirect,
        name='socialaccount_login_error',
    ),
    path(
        'accounts/3rdparty/login/cancelled/',
        techbrat_views.social_login_cancelled_redirect,
        name='socialaccount_login_cancelled',
    ),
    path('accounts/', include('allauth.urls')),
    path('', include('techbrat.urls')),
]
