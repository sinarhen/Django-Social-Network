from django.urls import path
from .views import NewsPageView

app_name = 'news'

urlpatterns = [
    path('all-news/', NewsPageView.as_view(), name='home')
]
