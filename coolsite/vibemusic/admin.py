from django.contrib import admin
from .models import *
from django import forms

from django.contrib import admin
from .models import *


class PostImageInline(admin.TabularInline):
    model = Post.images.through
    extra = 1
    verbose_name = "Фотография"
    verbose_name_plural = "Фотографии"

class TrackInline(admin.TabularInline):
    model = Post.tracks.through
    extra = 1
    verbose_name = "Трек"
    verbose_name_plural = "Треки"


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'created_at')  # Показывать в списке
    list_filter = ('created_at', 'artist')                            # Фильтры сбоку
    search_fields = ('title',)
    list_filter = ('created_at',)
    prepopulated_fields = {'slug': ('title',)}


class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'background_image')
    search_fields = ('name',)





admin.site.register(Genre, GenreAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Artist)
admin.site.register(Track)
admin.site.register(PostImage)
admin.site.register(Comment)



# Register your models here.
