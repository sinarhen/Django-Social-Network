from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from users.models import Post, Profile
from django.db.models import QuerySet
from itertools import chain
from users.mixins import ProfileRequiredMixin, LoginRequiredMixin
from django.db.models import Count
from django.contrib.auth import get_user_model

class NewsPageView(LoginRequiredMixin, ProfileRequiredMixin, ListView):
    template_name = 'news/news.html'
    model = Post
    context_object_name = 'posts'

    def get_recommended_users(self):
        popularity = get_user_model().objects.annotate(popularity=Count('follows_me')).order_by('-popularity').exclude(self.request.user)
        return popularity
    
    def get_queryset(self):
        queryset = Post.objects.filter(author__in=self.request.user.follows.all()).order_by('-updated_at')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.context_object_name] = self.get_queryset()
        context['recommended_users'] =  self.get_recommended_users()
        return context
    