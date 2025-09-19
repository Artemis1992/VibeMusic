# spotify_utils.py
import spotipy                                                                              # Импортирует библиотеку Spotipy для работы с Spotify API
from spotipy.oauth2 import SpotifyClientCredentials                                         # Импортирует класс для аутентификации клиента Spotify
import requests                                                                             # Импортирует библиотеку requests для выполнения HTTP-запросов
from django.conf import settings                                                            # Импортирует настройки Django для доступа к конфигурации (например, SPOTIFY_CLIENT_ID)
import os                                                                                   # Импортирует модуль os для работы с файловой системой

def get_spotify_client():                                                                   # Определяет функцию для создания клиента Spotify
    """Инициализация клиента Spotify с использованием учетных данных."""                    
    return spotipy.Spotify(auth_manager=SpotifyClientCredentials(                           # Создаёт и возвращает объект клиента Spotify
        client_id=settings.SPOTIFY_CLIENT_ID,                                               # Использует ID клиента из настроек Django
        client_secret=settings.SPOTIFY_CLIENT_SECRET                                        # Использует секретный ключ клиента из настроек Django
    ))                                                                                      

def search_track(track_name, artist_name):                                                  # Определяет функцию для поиска трека по названию и исполнителю
    """Поиск трека в Spotify по названию и исполнителю."""                                  
    sp = get_spotify_client()                                                               # Получает клиент Spotify через функцию get_spotify_client
    query = f"track:{track_name} artist:{artist_name}"                                      # Формирует строку запроса для поиска (например, "track:Shape of You artist:Ed Sheeran")
    results = sp.search(q=query, type='track', limit=1)                                     # Выполняет поиск трека с лимитом 1 результат
    tracks = results['tracks']['items']                                                     # Извлекает список треков из результатов поиска
    if tracks:                                                                              # Проверяет, найдены ли треки
        track = tracks[0]                                                                   # Берёт первый трек из списка
        album = track['album']                                                              # Извлекает данные альбома из трека
        return {                                                                            # Возвращает словарь с метаданными трека
            'track_id': track['id'],                                                        # ID трека в Spotify
            'track_name': track['name'],                                                    # Название трека
            'artist_name': track['artists'][0]['name'],                                     # Имя первого исполнителя трека
            'album_name': album['name'],                                                    # Название альбома
            'album_image_url': album['images'][0]['url'] if album['images'] else None       # URL обложки альбома или None, если изображение отсутствует
        }                                                                                   # Завершает формирование словаря
    return None                                                                             # Возвращает None, если трек не найден

def download_image(url, filename):                                                          # Определяет функцию для скачивания изображения по URL
    """Скачивание изображения по URL и сохранение в media."""  
    if not url:                                                                             # Проверяет, не пустой ли URL
        return None                                                                         # Возвращает None, если URL пустой
    response = requests.get(url)                                                            # Выполняет HTTP GET-запрос для загрузки изображения
    if response.status_code == 200:                                                         # Проверяет, успешен ли запрос (код 200)
        media_path = os.path.join(settings.MEDIA_ROOT, 'images', filename)                  # Формирует путь для сохранения файла (media/images/filename)
        os.makedirs(os.path.dirname(media_path), exist_ok=True)                             # Создаёт директорию images, если она не существует
        with open(media_path, 'wb') as f:                                                   # Открывает файл в режиме записи бинарных данных
            f.write(response.content)                                                       # Записывает содержимое ответа (изображение) в файл
        return os.path.join('images', filename)                                             # Возвращает относительный путь к файлу (images/filename)
    return None                                                                             # Возвращает None, если загрузка не удалась