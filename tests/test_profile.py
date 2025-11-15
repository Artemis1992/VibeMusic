# test_profile.py
from vibemusic.models import Profile

def test_profile_created(profile):
    """Проверяем, что профиль связан с пользователем и создался."""
    assert profile.user.username == "artemtester"
    assert Profile.objects.count() == 1