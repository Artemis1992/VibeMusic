# conftest.ini

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coolsite.coolsite.settings")
import django
django.setup()

import pytest
from django.contrib.auth.models import User
from vibemusic.models import Profile


@pytest.fixture
def user(db):
    """Создаем тестового пользователя."""
    return User.objects.create_user(
        username="artemtester", 
        password="123456789"
    )


@pytest.fixture
def profile(user):
    """Создаем профиль для тестового пользователя"""
    return Profile.objects.get(user=user)

