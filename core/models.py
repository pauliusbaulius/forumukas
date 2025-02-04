import datetime
import logging
import uuid

import markdown2
import nh3
import pydantic
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

from core.utils import url_to_instance

_logger = logging.getLogger("forumukas")


class CustomUserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    def _create_user(self, email, password=None, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def __str__(self):
        return self.username or self.email

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email  # Default username to email.
        super().save(*args, **kwargs)



@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    pass


class BaseDbModel(models.Model):
    """Base model for all models in the project."""

    public_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        help_text="Public facing ID, please do not leak id field to the public.",
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ("-created_at",)

    def save(self, *args, **kwargs):
        # All models inheriting BaseModel will have their updated_by automatically set.
        self.modified_at = datetime.datetime.now(tz=datetime.timezone.utc)
        super().save(*args, **kwargs)


class BaseDbModelWithUser(BaseDbModel):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)s_created_by",
        db_index=True,
    )

    class Meta:
        abstract = True


class Tag(BaseDbModel):
    name = models.CharField(max_length=25, unique=True)

    def __str__(self) -> str:
        return self.name


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)


class ThreadSchema(pydantic.BaseModel):
    pub_id: str
    title: str
    content: str
    created_by: str
    created_at: datetime.datetime
    modified_at: datetime.datetime
    replies_count: int


class Thread(BaseDbModelWithUser):
    title = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return str(self.id)

    class Meta:
        verbose_name = "Thread"
        verbose_name_plural = "Threads"

    def get_content(self) -> str:
        # First reply is the "content" of the thread.
        return self.replies.first().get_content_as_html()

    def count_replies(self) -> int:
        amount_replies = self.replies.count()
        return amount_replies - 1  if amount_replies > 0 else 0

    def as_schema(self) -> ThreadSchema:
        return ThreadSchema(
            pub_id=str(self.public_id),
            title=self.get_clean_title(),
            content=self.get_content(),
            created_by=self.created_by.username,
            created_at=self.created_at,
            modified_at=self.modified_at,
            replies_count=self.replies.count() - 1,  # Exclude self.
        )

    def as_dict(self) -> dict:
        return self.as_schema().model_dump()

    def get_clean_title(self) -> str:
        return nh3.clean(self.title)


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        url_to_instance("created_by"),
        "created_at",
        "modified_at",
    )


class ThreadTag(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="tags")
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("thread", "tag")
        verbose_name = "Thread Tag"
        verbose_name_plural = "Thread Tags"


@admin.register(ThreadTag)
class ThreadTagAdmin(admin.ModelAdmin):
    list_display = (
        url_to_instance("thread"),
        url_to_instance("tag"),
    )


class ReplySchema(pydantic.BaseModel):
    pub_id: str
    content: str
    created_by: str
    created_by_id: int
    created_at: datetime.datetime
    modified_at: datetime.datetime


class Reply(BaseDbModelWithUser):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="replies")
    content = models.TextField()

    def get_content_as_html(self) -> str:
        return markdown2.markdown(self.content)

    def __str__(self) -> str:
        return str(self.id)

    class Meta:
        verbose_name = "Reply"
        verbose_name_plural = "Replies"

    def as_schema(self) -> ReplySchema:
        return ReplySchema(
            pub_id=str(self.public_id),
            content=self.get_content_as_html(),
            created_by=self.created_by.username,
            created_by_id=self.created_by.pk,
            created_at=self.created_at,
            modified_at=self.modified_at,
        )

    def as_dict(self) -> dict:
        return self.as_schema().model_dump()


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        url_to_instance("thread"),
        url_to_instance("created_by"),
        "created_at",
        "modified_at",
    )

