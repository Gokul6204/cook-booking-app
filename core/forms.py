from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import User, CookProfile, Booking, Review


class UserRegisterForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "role", "password1", "password2")


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class CookProfileForm(forms.ModelForm):
    class Meta:
        model = CookProfile
        fields = [
            "cuisine",
            "dishes",
            "experience_years",
            "hourly_rate",
            "location",
            "bio",
            "photo",
        ]


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["date", "time", "duration_hours"]


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "avatar"]

