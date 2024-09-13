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
from django.urls import path, re_path
from rest_framework import routers
from game import views
from game.views import PlayCreateAPIView, PlayDetailAPIView

# router = routers.SimpleRouter()#A checker plus !

# router.register('play/create', )
urlpatterns = [
    path('admin/', admin.site.urls),
	path('api/play/create', views.PlayCreateAPIView.as_view(), name='play_create'),
	path('api/play/detail/<play_id>', views.PlayDetailAPIView.as_view(), name='play_detail'),
	# path('api/play/start/<int:id>', views.PlayStartAPIView.as_view()),
	# path('api-auth/', include('rest_framework.urls')), #activation de l'authentification DRF
	re_path(r'^.*$', views.index, name='index'),
]

