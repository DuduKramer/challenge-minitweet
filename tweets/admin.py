from django.contrib import admin
from .models import Tweet, TweetLike

class TweetLikeAdmin(admin.TabularInline):
    model = TweetLike

class TweetAdmin(admin.ModelAdmin):
    inlines = [TweetLikeAdmin]  # Adiciona o TweetLikeAdmin como inline no admin do Tweet
    list_display = ['__str__', 'user']
    search_fields = ['content', 'user__username', 'user__email']  # <-- dois underlines para acessar campos do relacionamento

    class Meta:
        model = Tweet

admin.site.register(Tweet, TweetAdmin)
