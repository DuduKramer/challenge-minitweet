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
from .models import Tweet
from .serielizers import TweetSerializer

ALLOWED_HOSTS = settings.ALLOWED_HOSTS

# Página inicial
def home_view(request, *args, **kwargs):
    return render(request, "pages/home.html", context={}, status=200)

@api_view(['GET'])
def tweet_detail_view(request,tweet_id, *args, **kwargs):
    qs = Tweet.objects.filter(id=tweet_id)
    if not qs.exists():
        return Response({"message": "Tweet not found"}, status=404)
    obj = qs.first()
    serializer = TweetSerializer(obj)
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def tweet_delete_view(request, tweet_id, *args, **kwargs):
    try:
        tweet = Tweet.objects.get(id=tweet_id)
    except Tweet.DoesNotExist:
        return Response({"message": "Tweet not found"}, status=404)

    if tweet.user != request.user:
        return Response({"message": "You do not have permission to delete this tweet"}, status=403)

    tweet.delete()
    return Response({"message": "Tweet deleted"}, status=200)


@api_view(['GET'])
def tweet_list_view(request, *args, **kwargs):
    qs = Tweet.objects.all()
    serializer = TweetSerializer(qs, many=True)
    return Response(serializer.data)

# Lista de tweets
def tweet_list_view_pure_django(request, *args, **kwargs):
    qs = Tweet.objects.all()
    tweets_list = [
        {"id": tweet.id, "content": tweet.content, "likes": random.randint(0, 200)}
        for tweet in qs
    ]
    return JsonResponse({"isUser": False, "response": tweets_list}, status=200)

@api_view(['POST'])
#@authentication_classes([SessionAuthentication, MyCustomAuth]) 
@permission_classes([IsAuthenticated])
def tweet_create_view(request, *args, **kwargs):
    serializer = TweetSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)
# Criação de um novo tweet
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

        form = TweetForm()  # limpa o formulário

    if form.errors and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse(form.errors, status=400)

    return render(request, "components/form.html", context={"form": form})


# Detalhes de um tweet específico
def tweet_detail_view_pure_django(request, tweet_id, *args, **kwargs):
    obj = get_object_or_404(Tweet, id=tweet_id)
    data = {
        "id": obj.id,
        "content": obj.content,
    }
    return JsonResponse(data, status=200)
