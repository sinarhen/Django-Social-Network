from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse
from users.models import Post
from django.http import HttpResponseNotAllowed


class LoginRequiredMixin(LoginRequiredMixin):
    """Checks if request user is authenticated and if not redirects to SignUp page"""
    login_url = settings.LOGIN_REDIRECT_URL


class ProfileRequiredMixin(AccessMixin):
    """
    A view mixin that only allows users that are active on the site.
    """
    permission_denied_message = ""
    not_created_message = ""
    not_created_redirect = ""

    def get_not_сreated_message(self):
        if not self.not_created_message:
            return "Profile is not created"
        return self.not_created_message

    def get_not_created_redirect(self):
        """ Get the url name to redirect to if the user has no profile"""
        if not self.not_created_redirect:
            self.not_created_redirect = reverse('users:profile_create')
        return self.not_created_redirect

    def handle_not_created(self):
        """ Deal with users that are logged in but not created a profile yet. """
        message = self.get_not_сreated_message()
        if self.raise_exception:
            raise PermissionDenied(message)
        return redirect(self.get_not_created_redirect())

    def dispatch(self, request, *args, **kwargs):
        """Dispatcher"""
        if not request.user.profile:
            return self.handle_not_created()
        return super().dispatch(request, *args, **kwargs)


class PostOwnerRequiredMixin(AccessMixin):
    not_owner_of_post_message = ""
    not_owner_of_post_redirect = ""

    def get_not_owner_message(self):
        return self.not_owner_of_post_message

    def get_not_owner_redirect(self):
        if not self.not_owner_of_post_redirect:
            return HttpResponseNotAllowed({'user': self.request.user, 'allowed': False})
        return self.not_owner_of_post_redirect

    def check_if_is_owner(self, request):
        """Checks if request user is owner of the post, while trying to update/delete data"""
        post = self.get_object()
        return request.user.is_owner_of_post(post)

    def handle_not_owner(self):
        message = self.not_owner_of_post_message
        if self.raise_exception:
            raise PermissionDenied(message)
        return redirect(self.get_not_owner_redirect())

    def dispatch(self, request, *args, **kwargs):
        """Dispatcher"""
        if not self.check_if_is_owner(request):
            return self.handle_not_owner()
        return super().dispatch(request, *args, **kwargs)
