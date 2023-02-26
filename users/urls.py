from django.urls import path
from .views import(
    LoginPageView, 
    SignupPageView, 
    ProfileDetailView, 
    ProfileCreateView,
    PostCreateView, 
    ProfileUpdateView,
    PostDetailView,
    PostDeleteView,
    PostUpdateView,
    SearchResultsView,
    logout_view, 
    like_handler,
    follow_handler,
    comment_handler,
    )

app_name = 'users'
urlpatterns = [
    path('login/', LoginPageView.as_view(), name='login'),
    path('signup/', SignupPageView.as_view(), name='signup'),
    path('logout/', logout_view, name='logout'),
    path('profile/create/', ProfileCreateView.as_view(), name='profile_create'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_update'),
    path('profile/search/', SearchResultsView.as_view(), name='profile_search'),
    path('profile/<slug:username>/', ProfileDetailView.as_view(), name='profile_detail'),
    path('post/create', PostCreateView.as_view(), name='post_create'),
    path('post/<uuid:post_id>/', PostDetailView.as_view(), name='post_detail'),
    path('post/<uuid:post_id>/edit/', PostUpdateView.as_view(), name='post_update'),
    path('post/<uuid:post_id>/delete', PostDeleteView.as_view(), name='post_delete'),
    path('post/<uuid:post_id>/comment', comment_handler, name='comment'),
    path('relationships/like/<uuid:post_id>/<path:next>', like_handler, name='like'),
    path('relationships/follow/<uuid:profile_id>', follow_handler, name='follow'),
]
