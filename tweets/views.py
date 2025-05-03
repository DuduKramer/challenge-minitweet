import random
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import TweetForm
from .models import Tweet

ALLOWED_HOSTS = settings.ALLOWED_HOSTS

# Página inicial
def home_view(request, *args, **kwargs):
    print(request.user)
    return render(request, "pages/home.html", context={}, status=200)

# Lista de tweets
def tweet_list_view(request, *args, **kwargs):
    qs = Tweet.objects.all()
    tweets_list = [
        {"id": tweet.id, "content": tweet.content, "likes": random.randint(0, 200)}
        for tweet in qs
    ]
    return JsonResponse({"isUser": False, "response": tweets_list}, status=200)

# Criação de um novo tweet
def tweet_create_view(request, *args, **kwargs):
    
    form = TweetForm(request.POST or None)
    next_url = request.POST.get('next') or None

    if form.is_valid():
        obj = form.save()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                "id": obj.id,
                "content": obj.content,
            }, status=201)
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts=ALLOWED_HOSTS):
            return redirect(next_url)
        form = TweetForm()  # limpa o form se quiser reexibir vazio

    if form.errors:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(form.errors, status=400)

    return render(request, "components/form.html", context={"form": form})

# Detalhes de um tweet específico
def tweet_detail_view(request, tweet_id, *args, **kwargs):
    obj = get_object_or_404(Tweet, id=tweet_id)
    data = {
        "id": obj.id,
        "content": obj.content,
    }
    return JsonResponse(data, status=200)
