## 1. Установи django-extensions

*Введи в терминале (в активном venv):*
```
pip install django-extensions
```

*Дождись, пока установка завершится.*
## 2. Добавь django_extensions в `INSTALLED_APPS`

*Открой файл:*
```
coolsite/settings.py
```

*и найди раздел:*
```
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # твои приложения ...
]
```

*Теперь добавь туда:*
```
'django_extensions',
```

*например:*
```
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'people',
    'django_extensions',
]
```

## 3. Проверь, что всё работает

**Перезапусти `shell`:**
```
python manage.py shell_plus
```

*Теперь должно появиться:*
```
# Shell Plus Model Imports
from people.models import Profile
from django.contrib.auth.models import User
...
```

*И ты сразу сможешь писать:*
```
User.objects.all()
Profile.objects.all()
```

***без ручного импорта — всё уже подгружено***