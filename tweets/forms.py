from django import forms

from .models import Tweet

class TweetForm(forms.ModelForm):
    class Meta:
        model = Tweet
        fields = ['content']
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content) > 280:
            raise forms.ValidationError("Content exceeds 280 characters limit.")
        return content
