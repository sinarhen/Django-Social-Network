# main/urls.py
from django.urls import path
from .views import HomePageView, AboutPageView


app_name = 'main'

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('about', AboutPageView.as_view(), name='about')
]