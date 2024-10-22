"""
URL configuration for Transcendance project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework import routers
from game import views
from game.views import PlayCreateAPIView, PlayDetailAPIView, PlaySubscribeAPIView
from game.views import TournamentViewSet
from authentication.views import LoginAPI, SignupAPI, Logout, UserInfoAPI, UserProfileView, UserProfileUpdateView, UserDeleteView
from authentication.views import AddFriendView, SuppFriendView, FollowingListView, FollowersListView, UserDetailView, MatchHistoryView
from authentication.views import get_csrf_token

router = routers.DefaultRouter()#Similaire a SimpleRouter mais offre api-root qui expose les endpoints disponibles
router.register('tournaments', TournamentViewSet, basename='tournament')

# router.register('play/create', )
urlpatterns = [
    path('admin/', admin.site.urls),
	path('api/play/create', views.PlayCreateAPIView.as_view(), name='play_create'),
	path('api/play/detail/<play_id>', views.PlayDetailAPIView.as_view(), name='play_detail'),
	path('api/play/join/<play_id>', views.PlaySubscribeAPIView.as_view(), name="play_join"),
	path('api/', include(router.urls)),
	path('api/user/match-history/', MatchHistoryView.as_view(), name='match-history'),
	# path('users/<int:user_id>/match-history/', MatchHistoryView.as_view(), name='match-history'),#MatchHistory dautre joueurs (amis)??
    path('api/login/', LoginAPI.as_view(), name='login'),
    path('api/signup/', SignupAPI.as_view(), name='signup'),
    path('api/logout/', Logout.as_view(), name='logout'),
    path('api/user/', UserInfoAPI.as_view(), name='user-info'),#TBD ?
    path('api/userprofile/<int:user_id>/', UserProfileView.as_view(), name='userprofile'),
    path('api/userprofileupdate/', UserProfileUpdateView.as_view(), name='userprofileupdate'),
    path('api/userdelete/', UserDeleteView.as_view(), name='userdelete'),
    path('api/addfriend/<int:user_id>/', AddFriendView.as_view()),
    path('api/users/<str:username>/', UserDetailView.as_view(), name='user-detail'),#TBD ?
    path('api/suppfriend/<int:user_id>/', SuppFriendView.as_view()),
    path('api/following/', FollowingListView.as_view()),
    path('api/followers/', FollowersListView.as_view()),
	path('api/get-csrf-token/', get_csrf_token, name='get_csrf_token'),
	re_path(r'^.*$', views.index, name='index'),
]

