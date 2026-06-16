from django.urls import path
from . import views

# Все имена URL-маршрутов должны точно совпадать с именами в шаблонах:
#
#   {% url 'index' %}              → главная + поиск
#   {% url 'popular' %}            → популярные треки
#   {% url 'playlists' %}          → плейлисты пользователя (login_required)
#   {% url 'playlist_create' %}    → форма создания плейлиста (login_required)
#   {% url 'artists' %}            → список исполнителей
#   {% url 'genres' %}             → список всех жанров
#   {% url 'genre_detail' slug %}  → треки конкретного жанра
#   {% url 'login' %}              → форма входа
#   {% url 'register' %}           → форма регистрации
#   {% url 'logout' %}             → выход (только POST, CSRF-protected)

urlpatterns = [

    # ── Основные страницы ────────────────────────────────────
    path('',                  views.index,          name='index'),
    path('popular/',          views.popular,         name='popular'),
    path('playlists/',        views.playlists,       name='playlists'),

    # ВАЖНО: playlists/create/ стоит ДО playlists/<pk>/
    path('playlists/create/', views.playlist_create, name='playlist_create'),

    path('artists/',          views.artists,         name='artists'),

    # ── Жанры ────────────────────────────────────────────────
    path('genres/',                views.genres,       name='genres'),
    path('genres/<slug:slug>/',    views.genre_detail, name='genre_detail'),

    # ── Авторизация ──────────────────────────────────────────
    path('login/',    views.login_view,    name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/',   views.logout_view,   name='logout'),

    # ── API ──────────────────────────────────────────────
    path('api/track/<int:track_id>/play/', views.increment_play_count, name='increment_play_count'),

    # ── Для авторов ───────────────────────────────────────
    path('submit/', views.submit_track, name='submit_track'),
]