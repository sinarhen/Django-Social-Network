# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils import timezone
import uuid
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django_resized import ResizedImageField
from django.conf.urls.static import static


def _upload_avatar_to_profile_username_folder(instance, filename):
    return '/'.join(['profiles', instance.user.email, filename])


def _upload_post_photos_to_profile_username_folder_post(instance, filename):
    return '/'.join([str(instance.post.author.profile.username), str(instance.post.id), filename])


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        """
        Create and save a User with the given email and password.
        """

        if not email:
            raise ValueError('Users must have an email address')
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            created_at=now,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        user = self._create_user(email, password, False, False, **extra_fields)
        group = Group.objects.get(name='User')
        user.groups.add(group)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """

        user = self._create_user(email, password, True, True, **extra_fields)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    CustomUser which provides custom uuid instead default id 
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, db_index=True) 
    email = models.EmailField(max_length=254, unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    follows = models.ManyToManyField('User', verbose_name='Follows', related_name='follows_me')

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []  # Required Fields while registrating a user

    objects = UserManager()
    def __str__(self) -> str:
        return self.email

    def is_owner_of_post(self, post):
        """Method which checks if User instance is owner of the Post object"""
        return post in self.posts.all()


class Profile(models.Model):
    """
    Profile model is the model which we will display on our website
    """
    id = models.UUIDField(verbose_name='ID', primary_key=True, default=uuid.uuid4, db_index=True)
    username = models.CharField(max_length=254, unique=True, validators=[
        RegexValidator(regex='[a-z]+', message='Can only contain latin and lowercase letters')])
    bio = models.TextField(verbose_name='Bio', blank=True, unique=False, null=True)
    first_name = models.CharField(verbose_name='First name', editable=True, blank=True, max_length=254, unique=False)
    last_name = models.CharField(verbose_name='Last name', editable=True, blank=True, max_length=254, unique=False)
    date_of_birth = models.DateField(verbose_name='Date of birth', null=True, blank=True)
    slug = models.SlugField(verbose_name='URL', max_length=100, blank=True)
    avatar = ResizedImageField(verbose_name='Avatar', upload_to=_upload_avatar_to_profile_username_folder, null=True,
                               blank=True, size=[140, 170])
    user = models.OneToOneField(User, verbose_name='User', null=True, on_delete=models.CASCADE, related_name='profile')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.username}'

    def get_absolute_url(self):  # get_absolute_url which allows to automatically generate URL for the instance of model
        return reverse("users:profile_detail", kwargs={self.username})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.username)
        super().save(*args, **kwargs)



class Post(models.Model):
    """
    Post model is the model which we will display as the post of concrete users profiles
    """
    id = models.UUIDField(verbose_name='ID', primary_key=True, default=uuid.uuid4, db_index=True)
    author = models.ForeignKey(User, verbose_name='Author', related_name='posts', on_delete=models.CASCADE)
    description = models.TextField(verbose_name='Description', max_length=1000, editable=True, blank=True)
    created_at = models.DateTimeField(verbose_name='Created at', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Updated at', auto_now=True)

    def __str__(self) -> str:
        return f'{self.author} s Post'

    def get_absolute_url(self): # get_absolute_url which allows to automatically generate URL for the instance of model
        return reverse("users:post_detail", kwargs={"post_id": str(self.id)})


class PostPhoto(models.Model):
    """
    PostPhoto is a model which provides photos(one or more) to concrete post
    """
    post = models.ForeignKey(Post, verbose_name='Post', related_name='post_photos', on_delete=models.CASCADE)
    photo_original = models.ImageField(verbose_name='Post Photo',
                                       upload_to=_upload_post_photos_to_profile_username_folder_post)
    photo_resized = ResizedImageField(verbose_name='Post Photo Resized',
                                      upload_to=_upload_post_photos_to_profile_username_folder_post,
                                      quality=100,
                                      size=[640, 480])


class Comment(models.Model):
    """
    Comment model provides comment, that can write every user to concrete post
    """
    id = models.UUIDField(verbose_name='ID', primary_key=True, default=uuid.uuid4, db_index=True)
    author = models.ForeignKey(User, verbose_name='Author of comment', on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField(verbose_name='Comment', max_length=300, null=False, blank=False)
    post = models.ForeignKey(Post, verbose_name='Post write comment to', on_delete=models.CASCADE,
                             related_name='comments')
    created_at = models.DateTimeField(verbose_name='Created at', auto_now_add=True)


class ReplyComment(models.Model):
    """
    Reply comment is a 'child' comment (reply) to comments on concrete post
    """
    id = models.UUIDField(verbose_name='ID', primary_key=True, default=uuid.uuid4, db_index=True)
    parent_comment = models.ForeignKey(Comment, verbose_name='Parent comment which we will reply to',
                                       related_name='child_comments', null=False, on_delete=models.CASCADE)
    author = models.ForeignKey(User, verbose_name='Author of comment', on_delete=models.CASCADE)
    text = models.TextField(verbose_name='description', max_length=9999, editable=False, blank=False)
    created_at = models.DateTimeField(verbose_name='Created at', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Updated at', auto_now=True)


class Like(models.Model):
    """
    Like model allows concrete user leave a like to the post
    """
    author = models.ForeignKey(User, verbose_name='Like author', on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, verbose_name='Post-to-like', on_delete=models.CASCADE, related_name='likes')
