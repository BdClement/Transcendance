import logging
import os
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
# , viewsets, permissions
from authentication.models import User
from authentication.serializers import LoginSerializer, UserSerializer, SignupSerializer, UserUpdateSerializer, PublicUserSerializer

# Create your views here.

logger = logging.getLogger(__name__)

from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.http import require_GET

@require_GET
def get_csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})

#APIView pour des actions specifiques
#ModelViewset pour les operations CRUD directement liee a un model
class UserInfoAPI(APIView):
	def get(self, request):
		if request.user.is_authenticated:
			return Response({
				'alias': request.user.alias,
				'username': request.user.username,
				'email': request.user.email,
				'photoProfile': request.user.photoProfile.url if request.user.photoProfile else None
			})
		else:
			return Response({'message': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

class LoginAPI(APIView):
	def post(self, request):
		serializer = LoginSerializer(data=request.data)
		if serializer.is_valid():
			user = serializer.validated_data['user']  # Cela devrait renvoyer l'utilisateur authentifié
			login(request, user)
			# Utiliser UserSerializer pour renvoyer les infos de l'utilisateur après connexion
			user_data = UserSerializer(user).data

			return Response({
				"message": "Connexion réussie",
				"user": user_data
			}, status=status.HTTP_200_OK)

		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# /!\ ajouter verification (par exemple verifier si on m'envoie bien un username)
class SignupAPI(APIView):
	def post(self, request):
		logger.debug(f"Received data: {request.data}")
		logger.debug(f"Received files: {request.FILES}")
		serializer = SignupSerializer(data=request.data)
		if serializer.is_valid():
			user = get_user_model()(
				username=serializer.validated_data['username'],
				email=serializer.validated_data['email'],
				alias=serializer.validated_data['alias'],
			)
			user.set_password(serializer.validated_data['password'])

			# Handle profile photo upload
			if 'photoProfile' in request.FILES:
				photo = request.FILES['photoProfile']
				filename = f'{user.username}.jpg'
				filepath = os.path.join(settings.BASE_DIR, 'static', 'images', filename)

				with open(filepath, 'wb+') as destination:
					for chunk in photo.chunks():
						destination.write(chunk)

				user.photoProfile = f'images/{filename}'

			user.save()
			login(request, user)
			user_data = UserSerializer(user).data
			return Response({
				"message": "Inscription réussie",
				"user": user_data
			}, status=status.HTTP_201_CREATED)
		else:
				logger.error(f"Validation errors: {serializer.errors}")
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		pass

class Logout(APIView):
	def get(self, request):
		logout(request)
		return Response({"message": "Déconnexion réussie"}, status.HTTP_200_OK)

class UserDetailView(APIView):
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        serializer = PublicUserSerializer(user)
        data = serializer.data
        data['id'] = user.id  # Assurez-vous que l'ID est inclus dans la réponse
        return Response(data)

class UserProfileView(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request, user_id=None):
		if user_id:
			user = get_object_or_404(User, id=user_id)
		else:
			user = request.user
		if user == request.user:
			serializer = UserSerializer(user)
		else:
			serializer = PublicUserSerializer(user)
		return Response(serializer.data)

class UserProfileUpdateView(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request):
		user = request.user
		serializer = UserUpdateSerializer(user)
		return Response(serializer.data)

	def put(self, request):
		user = request.user
		serializer = UserUpdateSerializer(user, data=request.data, partial=True)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDeleteView(APIView):
	permission_classes = [IsAuthenticated]
	def delete(self, request):
		user = request.user
		user.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

class AddFriendView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, user_id):
        user_to_follow = get_object_or_404(User, id=user_id)
        if request.user == user_to_follow:
            return Response({"detail": "Vous ne pouvez pas vous suivre vous-même."}, status=status.HTTP_400_BAD_REQUEST)
        if request.user.following.filter(id=user_to_follow.id).exists():
            return Response({"detail": "Vous suivez déjà cet utilisateur."}, status=status.HTTP_400_BAD_REQUEST)
        request.user.following.add(user_to_follow)
        return Response({"detail": f"Vous suivez maintenant {user_to_follow.username}."}, status=status.HTTP_200_OK)

class SuppFriendView(APIView):
	permission_classes = [IsAuthenticated]
	def delete(self, request, user_id):
		user_to_unfollow = get_object_or_404(User, id=user_id)
		if request.user not in request.user.following.all():
			return Response({"detail": "Vous ne suivez pas cet utilisateur."}, status=status.HTTP_400_BAD_REQUEST)
		request.user.following.remove(user_to_unfollow)
		return Response({"detail": f"Vous ne suivez plus {user_to_unfollow.username}."}, status=status.HTTP_200_OK)

class FollowingListView(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request):
		following_users = request.user.following.all()
		following_data = [{"id": user.id, "username": user.username} for user in following_users]
		return Response(following_data, status=status.HTTP_200_OK)

class FollowersListView(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request):
		followers_users = request.user.followers.all()
		followers_data = [{"id": user.id, "username": user.username} for user in followers_users]
		return Response(followers_data, status=status.HTTP_200_OK)
