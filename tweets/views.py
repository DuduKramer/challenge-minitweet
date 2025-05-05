import random
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.http import url_has_allowed_host_and_scheme

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .forms import TweetForm
from .models import Tweet, Profile
from .serielizers import TweetSerializer, TweetLikeSerializer
from django.contrib.auth.models import User
from rest_framework import status

ALLOWED_HOSTS = settings.ALLOWED_HOSTS

# Página inicial
def home_view(request, *args, **kwargs):
    return render(request, "pages/home.html", context={}, status=200)

# Página de registro
def register_page_view(request, *args, **kwargs):
    return render(request, "pages/register.html", context={}, status=200)

# Página de login
def login_page_view(request, *args, **kwargs):
    return render(request, "pages/login.html", context={}, status=200)

# Registro de usuários
@api_view(['POST'])
def register_user_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    if not username or not password or not email:
        return Response({"error": "All fields (username, password, email) are required."}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password, email=email)
    return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])  # Exige autenticação
def tweet_edit_view(request, tweet_id, *args, **kwargs):
    try:
        tweet = Tweet.objects.get(id=tweet_id)
    except Tweet.DoesNotExist:
        return Response({"message": "Tweet not found"}, status=404)

    # Verifica se o usuário autenticado é o autor do tweet
    if tweet.user != request.user:
        return Response({"message": "You do not have permission to edit this tweet"}, status=403)

    # Atualiza o conteúdo do tweet
    serializer = TweetSerializer(tweet, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=200)
    return Response(serializer.errors, status=400)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_toggle_view(request, username, *args, **kwargs):
    try:
        target_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"message": "User not found"}, status=404)

    profile = request.user.profile
    if profile.following.filter(id=target_user.profile.id).exists():
        profile.following.remove(target_user.profile)
        return Response({"message": f"You unfollowed {username}"}, status=200)
    else:
        profile.following.add(target_user.profile)
        return Response({"message": f"You followed {username}"}, status=200)

# Detalhes de um tweet
@api_view(['GET'])
def tweet_detail_view(request, tweet_id, *args, **kwargs):
    qs = Tweet.objects.filter(id=tweet_id)
    if not qs.exists():
        return Response({"message": "Tweet not found"}, status=404)
    obj = qs.first()
    serializer = TweetSerializer(obj)
    return Response(serializer.data)

# Exclusão de um tweet
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])  # Exige autenticação
def tweet_delete_view(request, tweet_id, *args, **kwargs):
    try:
        # Busca o tweet pelo ID
        tweet = Tweet.objects.get(id=tweet_id)
    except Tweet.DoesNotExist:
        return Response({"message": "Tweet not found"}, status=404)

    # Verifica se o usuário autenticado é o autor do tweet
    if tweet.user != request.user:
        return Response({"message": "You do not have permission to delete this tweet"}, status=403)

    # Deleta o tweet
    tweet.delete()
    return Response({"message": "Tweet deleted successfully"}, status=200)
# Curtir ou descurtir um tweet
@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Exige autenticação
def tweet_like_toggle_view(request, tweet_id, *args, **kwargs):
    tweet = Tweet.objects.filter(id=tweet_id).first()
    if not tweet:
        return Response({"message": "Tweet not found"}, status=404)

    action = request.data.get('action')
    if action not in ["like", "unlike"]:
        return Response({"message": "Invalid action"}, status=400)

    user = request.user
    if action == "like":
        tweet.likes.add(user)
        liked = True
    elif action == "unlike":
        tweet.likes.remove(user)
        liked = False

    return Response({
        "liked": liked,
        "likes_count": tweet.likes.count()
    }, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_list_view(request, *args, **kwargs):
    user = request.user
    # Exclui o próprio usuário da lista
    qs = User.objects.exclude(id=user.id)
    users = [
        {
            "username": u.username,
            "is_following": user.profile.following.filter(user=u).exists()
        }
        for u in qs
    ]
    return Response(users, status=200)
# Listagem de tweets
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tweet_list_view(request, *args, **kwargs):
    user = request.user
    try:
        # Obtém os perfis que o usuário segue
        following_profiles = user.profile.following.all()
        # Obtém os usuários correspondentes
        following_users = [profile.user for profile in following_profiles]
        # Inclui o próprio usuário na lista
        following_users.append(user)
        # Busca os tweets desses usuários
        qs = Tweet.objects.filter(user__in=following_users).order_by('-timestamp')
        serializer = TweetSerializer(qs, many=True)
        return Response(serializer.data)
    except Profile.DoesNotExist:
        return Response({"message": "User profile not found"}, status=404)

# Criação de tweets
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tweet_create_view(request, *args, **kwargs):
    serializer = TweetSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

# Criação de tweets com Django puro
def tweet_create_view_pure_django(request, *args, **kwargs):
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"error": "You must login!"}, status=401)
        return redirect(settings.LOGIN_URL)

    form = TweetForm(request.POST or None)
    next_url = request.POST.get('next') or None

    if form.is_valid():
        obj = form.save(commit=False)
        obj.user = request.user
        obj.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                "id": obj.id,
                "content": obj.content,
            }, status=201)

        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts=settings.ALLOWED_HOSTS):
            return redirect(next_url)

        form = TweetForm()

    if form.errors and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(form.errors, status=400)

    return render(request, "components/form.html", context={"form": form})

# Lista de tweets com Django puro
def tweet_list_view_pure_django(request, *args, **kwargs):
    qs = Tweet.objects.all()
    tweets_list = [
        {"id": tweet.id, "content": tweet.content, "likes": random.randint(0, 200)}
        for tweet in qs
    ]
    return JsonResponse({"isUser": False, "response": tweets_list}, status=200)

# Detalhes de um tweet específico com Django puro
def tweet_detail_view_pure_django(request, tweet_id, *args, **kwargs):
    obj = get_object_or_404(Tweet, id=tweet_id)
    data = {
        "id": obj.id,
        "content": obj.content,
    }
    return JsonResponse(data, status=200)