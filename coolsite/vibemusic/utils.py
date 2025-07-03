# util.py
from django.db.models import *
from django.utils.text import slugify
from .models import *
import logging
from django.conf import settings

from django.core.paginator import Paginator

logger = logging.getLogger(__name__)

menu = [
    {"title": "Главная", "url_name": "home"},
    {"title": "О сайте", "url_name": "about"},
    {"title": "Обратная связь", "url_name": "contact"},
]

class DataMixin:

    def get_context_menu(self, **kwargs):
        context = kwargs.copy()
        context['menu'] = menu
        context['genres'] = Genre.objects.all()
        return context

    def get_paginated_comments(self, comments, request):
        """Возвращает объект пагинатора для комментариев"""
        logger.debug(f"Paginating comments with {settings.COMMENTS_PER_PAGE} per page")             # Записываем в лог информацию о количестве комментариев на одну страницу
        paginator = Paginator(comments, settings.COMMENTS_PER_PAGE)                                 # Создаём объект пагинатора: разбивает список comments по N на страницу
        page_number = request.GET.get('page')                                                       # Получаем номер текущей страницы из параметра запроса (например, ?page=2)
        page_obj = paginator.get_page(page_number)                                                  # Получаем объект страницы с комментариями для данного номера
        logger.debug(f"Comments page number: {page_number}, Total pages: {paginator.num_pages}")    # Логируем текущую страницу и общее количество страниц
        return page_obj                                                                             # Возвращаем объект страницы — его можно использовать в шаблоне как page_obj
    

    # Метод для постраничного вывода постов (аналогично предыдущему, только для постов)
    def get_paginated_posts(self, posts, request):
        """Возвращаем обьект пагинатора для постов"""
        logger.debug(f"Paginating posts with {settings.POSTS_PER_PAGE} per page")                   # Логируем информацию о постах: сколько постов на одной странице
        paginator = Paginator(posts, settings.POSTS_PER_PAGE)                                       # Создаём пагинатор для постов (разбиваем их по N на страницу)
        page_number = request.GET.get('page')                                                       # Получаем номер нужной страницы из запроса
        page_obj = paginator.get_page(page_number)                                                  # Получаем номер нужной страницы из запроса
        logger.debug(f"Posts page number: {page_number}, Total pages: {paginator.num_pages}")       # Логируем номер текущей страницы и общее количество
        return page_obj                                                                             # Возвращаем объект страницы с постами
