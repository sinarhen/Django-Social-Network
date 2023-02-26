# main/views.py
from django.views.generic import FormView, TemplateView
from users.forms import SignupUserForm
from django.shortcuts import redirect


class HomePageView(FormView):
    template_name: str = 'main/home.html'
    form_class = SignupUserForm


class AboutPageView(TemplateView):
    template_name = 'main/about.html'