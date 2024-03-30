from django import forms
from accounts.models import ReviewRating

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['title', 'review', 'rating']
