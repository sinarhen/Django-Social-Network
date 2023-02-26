# users/views.py
from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse
from django.views.generic import View, CreateView, UpdateView, DetailView, DeleteView, ListView
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.decorators import login_required
from users.mixins import LoginRequiredMixin, ProfileRequiredMixin, PostOwnerRequiredMixin
from django.db.models import Q, QuerySet

from users.forms import (
    SignupUserForm,
    AuthenticationUserForm,
    ProfileCreateForm,
    ProfileUpdateForm,
    PostCreateForm,
    PostUpdateForm,
)

from users.models import Profile, Post, PostPhoto, Like, Comment
from users.decorators import profile_required


@login_required # checks if request user is authenticated
@profile_required # checks if request user has a profile
def follow_handler(request, profile_id) -> HttpResponse:
    """Handles the follow/unfollow functionality"""
    if request.method == 'POST':
        profile = get_object_or_404(Profile, id=profile_id)
        user_obj = request.user
        if profile.user in user_obj.follows.all():
            user_obj.follows.remove(profile.user)
        else:
            user_obj.follows.add(profile.user)
        user_obj.save()
    return redirect(reverse('users:profile_detail', kwargs={'username': profile.username}))


@login_required # checks if request user is authenticated
@profile_required # checks if request user has a profile
def like_handler(request, post_id, next) -> HttpResponse:
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(author=request.user, post=post)
        if not created:
            like.delete()
    return redirect(next)


@login_required # checks if request user is authenticated
@profile_required # checks if request user has a profile
def comment_handler(request, post_id) -> HttpResponse:
    """Handles comment action"""
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        user = request.user
        text = request.POST.get('comment_text')
        try:
            Comment.objects.create(post=post, author=user, text=text)
        except Exception as ex:
            print(ex)
        return redirect(reverse('users:post_detail', kwargs={'post_id': post_id}))


class ProfileCreateView(LoginRequiredMixin, CreateView):
    """
        Profile create view with form, which is avalaible only for users, that didn't create one before
    """
    model = Profile
    template_name: str = 'users/profile/profile_create.html'
    form_class = ProfileCreateForm

    def get_success_url(self) -> str:  # get_success_url provides url we will redirect to if form filled properly
        return reverse('users:profile_detail', kwargs={'username': self.request.user.profile.username})

    def get(self, request, *args: str, **kwargs) -> HttpResponse:  # GET request handler
        profile = Profile.objects.filter(user=request.user)
        if profile.count() != 0:
            return redirect(self.get_success_url())
        return super().get(request, *args, **kwargs)

    def form_valid(self, form) -> HttpResponse:  # if form.is_valid() is true
        f = form.save(commit=False)
        f.user = self.request.user
        f.save()
        return redirect(self.get_success_url())

class ProfileUpdateView(LoginRequiredMixin, ProfileRequiredMixin, UpdateView):
    """
        ProfileUpdateView provies profile editing
    """
    model = Profile
    template_name: str = 'users/profile/profile_update.html'
    form_class = ProfileUpdateForm

    not_created_message: str = 'Profile is not created'

    def get_object(self, queryset=None):  # get object of profile
        return get_object_or_404(Profile, username=self.request.user.profile)


class SearchResultsView(LoginRequiredMixin, ProfileRequiredMixin, ListView):
    """
        Search users results view
    """
    model = Profile
    template_name: str = 'users/profile/profile_search.html'
    context_object_name: str = 'profiles'

    def get_queryset(self) -> QuerySet: 
        search_query = self.request.GET.get('q')
        profile = Profile.objects.filter(Q(username__icontains=search_query)|Q(first_name__icontains=search_query)|Q(last_name__icontains=search_query)) # searching if user's search query has match with all of the Profile objects
        return profile


class ProfileDetailView(DetailView):
    """
        ProfileDetailView provides profile page with all public data
    """
    model = Profile
    template_name: str = 'users/profile/profile_detail.html'

    def get_object(self, queryset=None):  # get profile object
        return get_object_or_404(Profile, username=self.kwargs.get('username'))

class PostCreateView(LoginRequiredMixin, ProfileRequiredMixin, CreateView):
    """
        View for creating Posts
    """
    model = Post
    template_name: str = 'users/post/post_create.html'
    not_owner_of_post_message: str = "You aren't owner of this post"
    form_class = PostCreateForm

    def get_success_url(self, object_id) -> str: # get_success_url provides url we will redirect to if form filled properly
        return reverse('users:post_detail', kwargs={'post_id': object_id})

    def post(self, request, *args, **kwargs) -> HttpResponse: # if request.method == 'POST'
        form = self.form_class(request.POST)
        images = request.FILES.getlist('images')
        if form.is_valid():
            f = form.save(commit=False)
            f.author = request.user
            f.save()
            for i in images:
                PostPhoto.objects.create(post=f, photo_original=i, photo_resized=i) # Saving multiple PostPhoto objects and bounding them to Post object
            return redirect(self.get_success_url(f.id))
        return HttpResponse(f'error: {form.errors}')



class PostUpdateView(LoginRequiredMixin, ProfileRequiredMixin, PostOwnerRequiredMixin, UpdateView):
    """
        View for updating the post data
    """
    model = Post
    template_name: str = "users/post/post_update.html"
    not_owner_of_post_message: str = "You aren't owner of this post"
    form_class = PostUpdateForm

    def post(self, request, *args: str, **kwargs) -> HttpResponse:
        form = self.form_class(request.POST)
        images = request.FILES.getlist('images') 
        if form.is_valid():
            post = self.get_object()
            cd = form.cleaned_data
            desc = cd['description']
            post.description = desc
            post.save()
            if cd['clear_photos']:
                PostPhoto.objects.filter(post=post).delete()
            else:
                for i in images:
                    PostPhoto.objects.create(post=post, photo_original=i, photo_resized=i) # Saving multiple PostPhoto objects and bounding them to Post object
            return redirect(self.get_success_url())
        return HttpResponse(f'error: {form.errors}')

    def get_success_url(self) -> str: 
        return reverse('users:post_detail', kwargs={'post_id': self.get_object().id})

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, id=self.kwargs.get('post_id'))


class PostDetailView(DetailView):
    """
        Post Detail View
    """
    model = Post
    template_name: str = 'users/post/post_detail.html'
    context_object_name: str = 'post'

    def get_object(self, queryset=None) -> Post:
        kw = self.kwargs.get('post_id', None)
        post = get_object_or_404(Post, id=kw)
        return post


class PostDeleteView(LoginRequiredMixin, ProfileRequiredMixin, PostOwnerRequiredMixin, DeleteView):
    """
        View for deleting Posts
    """
    model = Post
    pk_url_kwarg: str = 'post_id'

    def get_success_url(self) -> str: # get_success_url provides url we will redirect to if form filled properly
        return reverse_lazy('users:profile_detail', kwargs={'username': self.request.user.profile.username})


class LoginPageView(View):
    """
        View for login users
    """
    form = AuthenticationUserForm
    template_name = 'users/login.html'

    def get(self, request) -> HttpResponse: # if request.method == 'GET'
        return render(request, self.template_name, {'form': self.form})

    def post(self, request) -> HttpResponse: # if request.method == 'POST'
        form = self.form(request.POST)
        if form.is_valid():
            user = authenticate( # Authenticating the user with form data 
                request=request,
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
            )
            remember_me = form.cleaned_data['remember_me']
            if user is not None:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(
                        0)  # <-- Here if the remember me is False, that is why expiry is set to 0 seconds. So it will automatically close the session after the browser is closed.

                    # else browser session will be as long as the session  cookie time "SESSION_COOKIE_AGE"
                return redirect(settings.LOGIN_REDIRECT_URL)
        message = 'Login failed'
        return render(request, self.template_name, context={'form': form, 'message': message})


class SignupPageView(CreateView):
    """
        View for Signup
    """
    template_name: str = 'users/signup.html'
    form_class = SignupUserForm
    model = get_user_model()
    success_url: str = reverse_lazy('users:login')


def logout_view(request) -> HttpResponse:
    """
        View which provides logout
    """
    logout(request)
    return redirect(reverse_lazy('users:login'))
