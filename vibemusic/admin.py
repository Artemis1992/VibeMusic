
# vibemusic/admin.py
# vibemusic/admin.py
from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import Genre, Artist, Post, Track, PostImage, Comment, SiteSettings


#  Универсальный миксин для предпросмотра изображений (миниатюры)
class ImagePreviewMixin:
    def preview(self, obj, field_name: str, size: int = 100):
        """
        Возвращает HTML превью изображения.
        """
        image = getattr(obj, field_name, None)
        if image:
            return format_html(
                '<img src="{}" style="max-height:{}px; border-radius:6px;"/>',
                image.url,
                size
            )
        return format_html('<span style="color:#888;">Нет изображения</span>')


# -------------------------------
# GENRE ADMIN
# -------------------------------
class GenreAdminForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ['name', 'slug', 'icon', 'background_image', 'description']


@admin.register(Genre)
class GenreAdmin(ImagePreviewMixin, admin.ModelAdmin):
    form = GenreAdminForm
    list_display = ('name', 'slug', 'icon_prev', 'background_prev')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('icon_prev', 'background_prev')

    def icon_prev(self, obj):
        return self.preview(obj, 'icon')
    icon_prev.short_description = "Иконка"

    def background_prev(self, obj):
        return self.preview(obj, 'background_image', size=120)
    background_prev.short_description = "Фон жанра"


# -------------------------------
# ARTIST ADMIN
# -------------------------------
class ArtistAdminForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = ['name', 'bio', 'photo', 'genres']

    def clean_genres(self):
        genres = self.cleaned_data.get('genres')
        if not genres:
            raise forms.ValidationError("Пожалуйста, выберите хотя бы один жанр.")
        return genres


@admin.register(Artist)
class ArtistAdmin(ImagePreviewMixin, admin.ModelAdmin):
    form = ArtistAdminForm
    list_display = ('name', 'photo_prev', 'display_genres', 'created_at')
    search_fields = ('name',)
    list_filter = ('genres',)
    readonly_fields = ('photo_prev',)
    filter_horizontal = ('genres',)

    def photo_prev(self, obj):
        return self.preview(obj, 'photo', size=120)
    photo_prev.short_description = "Фото"

    def display_genres(self, obj):
        return ", ".join(g.name for g in obj.genres.all())
    display_genres.short_description = "Жанры"


# -------------------------------
# POST IMAGE ADMIN
# -------------------------------
@admin.register(PostImage)
class PostImageAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('id', 'image_prev', 'caption', 'created_at')
    readonly_fields = ('image_prev',)

    def image_prev(self, obj):
        return self.preview(obj, 'image', size=140)
    image_prev.short_description = "Фото"


# -------------------------------
# TRACK ADMIN
# -------------------------------
@admin.register(Track)
class TrackAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('title', 'artist', 'album_prev', 'created_at')
    search_fields = ('title', 'artist__name')
    list_filter = ('artist', 'created_at')
    readonly_fields = ('album_prev',)

    def album_prev(self, obj):
        return self.preview(obj, 'album_image', size=120)
    album_prev.short_description = "Обложка"


# -------------------------------
# POST ADMIN + INLINE IMAGES/TRACKS
# -------------------------------
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


@admin.register(Post)
class PostAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('title', 'artist', 'genre', 'created_at', 'cover_prev')
    list_filter = ('created_at', 'artist', 'genre')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('cover_prev',)
    inlines = [PostImageInline, TrackInline]

    def cover_prev(self, obj):
        first_img = obj.images.first()
        if first_img:
            return self.preview(first_img, 'image', size=120)
        return format_html('<span style="color:#777;">Нет фото</span>')
    cover_prev.short_description = "Обложка поста"


# -------------------------------
# COMMENT ADMIN
# -------------------------------
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('content', 'user__username', 'post__title')


# -------------------------------
# SITE SETTINGS ADMIN
# -------------------------------
@admin.register(SiteSettings)
class SiteSettingsAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('updated_at', 'header_prev')
    fields = ('header_image', 'header_prev')
    readonly_fields = ('header_prev',)

    def header_prev(self, obj):
        return self.preview(obj, 'header_image', size=150)
    header_prev.short_description = "Шапка сайта"


# -------------------------------
# CUSTOMIZATION OF ADMIN PANEL UI
# -------------------------------
admin.site.site_header = "Vibe Music Admin"
admin.site.site_title = "Vibe Music Admin Panel"
admin.site.index_title = "Добро пожаловать в админку Vibe Music"
