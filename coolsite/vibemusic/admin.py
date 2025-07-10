
# vibemusic/admin.py
from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import Genre, Artist, Post, Track, PostImage, Comment, SiteSettings

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
    list_display = ('title', 'artist', 'genre', 'created_at')
    list_filter = ('created_at', 'artist', 'genre')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PostImageInline, TrackInline]

class GenreAdminForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ['name', 'slug', 'icon', 'background_image', 'description']  # Исключаем related_genres

class GenreAdmin(admin.ModelAdmin):
    form = GenreAdminForm
    list_display = ('name', 'slug', 'icon', 'background_image', 'image_preview')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

    def image_preview(self, obj):
        if obj.background_image:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.background_image.url)
        return "Нет изображения"
    image_preview.short_description = "Превью фона"

    def save_model(self, request, obj, form, change):
        try:
            super().save_model(request, obj, form, change)
            print(f"Saved Genre: {obj.name}, Slug: {obj.slug}, ID: {obj.id}")
        except Exception as e:
            print(f"Error saving Genre: {e}")

class ArtistAdminForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = ['name', 'bio', 'photo', 'genres']

    def clean_genres(self):
        genres = self.cleaned_data.get('genres')
        if not genres:
            raise forms.ValidationError("Пожалуйста, выберите хотя бы один жанр.")
        return genres

class ArtistAdmin(admin.ModelAdmin):
    form = ArtistAdminForm
    list_display = ('name', 'display_genres', 'created_at')
    search_fields = ('name',)
    list_filter = ('genres',)
    filter_horizontal = ('genres',)  # Удобный интерфейс для выбора жанров

    def display_genres(self, obj):
        return ", ".join(genre.name for genre in obj.genres.all())
    display_genres.short_description = "Жанры"


class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('updated_at', 'image_preview')
    fields = ('header_image',)

    def image_preview(self, obj):
        if obj.header_image:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.header_image.url)
        return "Нет изображения"
    image_preview.short_description = "Превью изображение шапки"


# Настройка глобальных параметров админки
admin.site.site_header = "Vibe Music Admin"
admin.site.site_title = "Vibe Music Admin Panel"
admin.site.index_title = "Добро пожаловать в админку Vibe Music"


admin.site.register(SiteSettings, SiteSettingsAdmin)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Track)
admin.site.register(PostImage)
admin.site.register(Comment)