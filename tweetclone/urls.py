from django.contrib import admin
from django.urls import path, re_path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from tweets.views import (
  home_view, 
  tweet_like_toggle_view,
  tweet_detail_view, 
  tweet_delete_view,
  tweet_list_view, 
  tweet_create_view,
  register_user_view,
  register_page_view,
  login_page_view,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('register/', register_page_view, name='register'),
    path('create-tweet', tweet_create_view),
    path('tweets', tweet_list_view),
    path('tweets/<int:tweet_id>', tweet_detail_view),
    path('api/tweets/<int:tweet_id>/delete', tweet_delete_view),
    path('api/tweet/<int:tweet_id>/like-toggle/', tweet_like_toggle_view),
    path('api/register/', register_user_view, name='register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Login
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Refresh do token
     path('login/', login_page_view, name='login')
]