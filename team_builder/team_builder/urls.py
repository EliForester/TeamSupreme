"""team_builder URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import notifications.urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path, re_path

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('admin/', admin.site.urls),

# Account stuff (sign-up, sign-in, etc)
    path('accounts/signin/', views.SignInView.as_view(), name='signin'),
    path('accounts/signout/', LogoutView.as_view(), name='signout'),
    path('accounts/signup/', views.SignUpView.as_view(), name='signup'),

# Profile URLs
    path('profile/<int:profile_id>/', views.ProfileDetailView.as_view(), name='profile'),
    path('profile/<int:profile_id>/update/',
         views.ProfileUpdateView.as_view(), name='profile_update'),

# Project creation, update, etc
    path('projects/list/', views.ProjectView.as_view(),
         name='projects'),

    re_path(r'^projects/list/(?P<filter_type>own|join|member)/$',
            views.ProjectView.as_view(), name='projects_filter'),

    path('projects/detail/<int:project_id>/', views.ProjectDetailView.as_view(),
         name='project_detail'),

    path('projects/create/',
         views.ProjectCreateView.as_view(),
         name='project_create'),

    path('projects/<int:project_id>/update/',
         views.ProjectUpdateView.as_view(),
         name='project_update'),

# Position creation, update, etc
    path('projects/<int:project_id>/position/add/', views.PositionAddView.as_view(),
         name='position_add'),

    path('position/<int:position_id>/detail/', views.PositionDetailView.as_view(),
         name='position_detail'),

    path('position/<int:position_id>/update/', views.PositionUpdateView.as_view(),
         name='position_update'),

    path('position/<int:position_id>/delete/', views.PositionDeleteView.as_view(),
         name='position_delete'),

    path('search/', views.SearchView.as_view(), name='search'),

# Applying for participation, approving/denying or clearing
    path('participant/<int:position_id>/apply/',
         views.ParticipantCreateView.as_view(), name='participant_create'),

    re_path(r'^participant/(?P<participant_id>\d+)/(?P<action>approve|reject|retire)/$',
            views.participant_update_view, name='participant_update'),

    path('participant/<int:position_id>/delete/',
         views.ParticipantDeleteView.as_view(), name='participant_delete'),

    path('skill/<int:skill_id>/', views.SkillDetailView.as_view(),
                       name='skill_detail'),

    re_path('skill/(?P<referrer>user|position)/(?P<referrer_id>\d+)/add/',
            views.SkillCreateView.as_view(), name='skill_add'),

# Notifications
    path('notifications/', include(notifications.urls, namespace='notifications'))

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
