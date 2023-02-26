from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Post


class SignupUserForm(UserCreationForm):
    """Form for user registration"""

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('email',)


class AuthenticationUserForm(forms.Form):
    """Form for user authentication"""
    email = forms.fields.CharField(widget=forms.widgets.EmailInput)
    password = forms.fields.CharField(widget=forms.widgets.PasswordInput)
    remember_me = forms.fields.BooleanField(widget=forms.widgets.CheckboxInput, required=False) # increases time when cookies will be expired


class ProfileCreateForm(forms.ModelForm):
    """Form for creating Profile for user (One User = One Profile)"""

    username = forms.CharField(widget=forms.widgets.TextInput(
        attrs={'pattern': '[a-z0-9_]+', 'title': 'Can only contain latin, lowercase letters, underscores and integers'})) # Username can't be like &<?>#$@#!&
    avatar = forms.fields.ImageField(widget=forms.widgets.FileInput, required=False) 
    date_of_birth = forms.fields.DateField(widget=forms.widgets.SelectDateWidget, required=False)

    class Meta:
        exclude = ('id', 'slug', 'user', 'follows')
        model = Profile


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating Profile data"""
    class Meta:
        model = Profile
        fields = ('username', 'bio', 'first_name', 'last_name', 'avatar', 'date_of_birth')


class PostForm(forms.ModelForm):
    """Prototype of form to create posts"""
    class Meta:
        model = Post
        fields = ('description',)


class PostCreateForm(PostForm):
    """Form for creating posts, which provides multiple file sending"""
    images = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        required=False,
    )

    class Meta(PostForm.Meta):
        fields = PostForm.Meta.fields + (
            "images",
        )


class PostUpdateForm(PostCreateForm):
    """Form for updating Post data"""
    clear_photos = forms.fields.BooleanField(required=False, widget=forms.widgets.CheckboxInput)

    class Meta(PostCreateForm.Meta):
        fields = PostCreateForm.Meta.fields + (
            "clear_photos",
        )
