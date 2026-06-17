from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Track, Playlist, Genre
from django.contrib.auth.models import User
from django.http import HttpResponse

def create_admin(request):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@test.com', 'ТвойПароль123')
        return HttpResponse("Админ создан!")
    return HttpResponse("Админ уже существует.")

# ─────────────────────────────────────────────────────────────
# ГЛАВНАЯ — витрина треков + поиск
# ─────────────────────────────────────────────────────────────

def index(request):
    query = request.GET.get('query', '').strip()

    if query:
        tracks = Track.objects.filter(
            Q(title__icontains=query) | Q(artist__icontains=query)
        ).order_by('-id')
    else:
        tracks = Track.objects.all().order_by('-id')

    context = {
        'tracks': tracks,
        'query':  query,
    }
    return render(request, 'streaming/index.html', context)


# ─────────────────────────────────────────────────────────────
# ПОПУЛЯРНОЕ
# ─────────────────────────────────────────────────────────────

def popular(request):
    query = request.GET.get('query', '').strip()

    tracks = Track.objects.all()
    if query:
        tracks = tracks.filter(
            Q(title__icontains=query) | Q(artist__icontains=query)
        )
    tracks = tracks.order_by('-play_count', '-id')

    context = {
        'tracks': tracks,
        'query':  query,
    }
    return render(request, 'streaming/popular.html', context)


# ─────────────────────────────────────────────────────────────
# ПЛЕЙЛИСТЫ
# ─────────────────────────────────────────────────────────────

@login_required(login_url='login')
def playlists(request):
    user_playlists = Playlist.objects.filter(
        user=request.user
    ).prefetch_related('tracks').order_by('-id')

    context = {
        'playlists': user_playlists,
    }
    return render(request, 'streaming/playlists.html', context)


# ─────────────────────────────────────────────────────────────
# СОЗДАНИЕ ПЛЕЙЛИСТА
# ─────────────────────────────────────────────────────────────

@login_required(login_url='login')
def playlist_create(request):
    if request.method == 'POST':
        name        = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        track_pks   = request.POST.getlist('tracks')

        if not name:
            all_tracks = Track.objects.all().order_by('artist', 'title')
            return render(request, 'streaming/create_playlist.html', {
                'all_tracks':    all_tracks,
                'form_error':    'Название плейлиста обязательно.',
                'posted_name':   request.POST.get('name', ''),
                'posted_desc':   description,
                'posted_tracks': track_pks,
            })

        playlist = Playlist.objects.create(
            user=request.user,
            name=name,
            description=description,
        )

        if track_pks:
            valid_tracks = Track.objects.filter(pk__in=track_pks)
            ordered_tracks = sorted(
                valid_tracks,
                key=lambda t: track_pks.index(str(t.pk))
            )
            playlist.tracks.set(ordered_tracks)

        messages.success(request, f'Плейлист «{name}» создан!')
        return redirect('playlists')

    all_tracks = Track.objects.all().order_by('artist', 'title')
    context = {
        'all_tracks':    all_tracks,
        'form_error':    None,
        'posted_name':   '',
        'posted_desc':   '',
        'posted_tracks': [],
    }
    return render(request, 'streaming/create_playlist.html', context)


# ─────────────────────────────────────────────────────────────
# ИСПОЛНИТЕЛИ
# ─────────────────────────────────────────────────────────────

def artists(request):
    query = request.GET.get('query', '').strip()

    qs = Track.objects.values('artist').distinct().order_by('artist')
    if query:
        qs = qs.filter(artist__icontains=query)

    artist_list = []
    for row in qs:
        artist_name   = row['artist']
        artist_tracks = Track.objects.filter(
            artist=artist_name
        ).order_by('-play_count', '-id')
        sample_track = artist_tracks.first()
        artist_list.append({
            'name':        artist_name,
            'track_count': artist_tracks.count(),
            'cover':       sample_track.cover if sample_track and sample_track.cover else None,
            'tracks_qs':   artist_tracks,
        })

    context = {
        'artists': artist_list,
        'query':   query,
    }
    return render(request, 'streaming/artists.html', context)


# ─────────────────────────────────────────────────────────────
# АВТОРИЗАЦИЯ — Войти
# ─────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    error = None

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            error = 'Введите имя пользователя и пароль.'
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next') or request.POST.get('next') or 'index'
                return redirect(next_url)
            else:
                error = 'Неверное имя пользователя или пароль.'

    return render(request, 'streaming/login.html', {
        'error': error,
        'next':  request.GET.get('next', ''),
    })


# ─────────────────────────────────────────────────────────────
# РЕГИСТРАЦИЯ
# ─────────────────────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    error = None

    if request.method == 'POST':
        username  = request.POST.get('username', '').strip()
        email     = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not username or not password1:
            error = 'Заполните все обязательные поля.'
        elif password1 != password2:
            error = 'Пароли не совпадают.'
        elif len(password1) < 8:
            error = 'Пароль должен содержать не менее 8 символов.'
        elif User.objects.filter(username=username).exists():
            error = f'Имя пользователя «{username}» уже занято.'
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
            )
            login(request, user)
            messages.success(request, f'Добро пожаловать, {username}!')
            return redirect('index')

    return render(request, 'streaming/register.html', {'error': error})


# ─────────────────────────────────────────────────────────────
# ВЫХОД
# ─────────────────────────────────────────────────────────────

def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('index')


# ─────────────────────────────────────────────────────────────
# ЖАНРЫ — список всех жанров
# ─────────────────────────────────────────────────────────────

def genres(request):
    """
    Страница со всеми жанрами.
    Для каждого жанра считаем кол-во треков прямо в QuerySet
    через annotate — один SQL-запрос вместо N+1.
    """
    from django.db.models import Count

    genres_qs = (
        Genre.objects
        .annotate(track_count=Count('tracks'))
        .order_by('name')
    )

    context = {
        'genres': genres_qs,
    }
    return render(request, 'streaming/genres.html', context)


# ─────────────────────────────────────────────────────────────
# ЖАНР — детальная страница с треками
# ─────────────────────────────────────────────────────────────

def genre_detail(request, slug):
    """
    Страница конкретного жанра: заголовок + все его треки.
    slug берётся из URL: /genres/hip-hop/
    """
    from django.shortcuts import get_object_or_404

    genre  = get_object_or_404(Genre, slug=slug)
    query  = request.GET.get('query', '').strip()

    tracks = genre.tracks.all()
    if query:
        tracks = tracks.filter(
            Q(title__icontains=query) | Q(artist__icontains=query)
        )
    tracks = tracks.order_by('-id')

    context = {
        'genre':  genre,
        'tracks': tracks,
        'query':  query,
    }
    return render(request, 'streaming/genre_detail.html', context)


# ─────────────────────────────────────────────────────────────
# API — счётчик прослушиваний
# ─────────────────────────────────────────────────────────────

from django.http import JsonResponse
from django.views.decorators.http import require_POST

@require_POST
def increment_play_count(request, track_id):
    """
    POST /api/track/<id>/play/
    Увеличивает play_count трека на 1.
    Вызывается из JS-плеера (base.html) при каждом старте воспроизведения.
    require_POST защищает от случайных GET-запросов (например от браузерного prefetch).
    F()-выражение делает UPDATE атомарно на уровне БД — без race condition.
    """
    from django.db.models import F

    updated = Track.objects.filter(pk=track_id).update(
        play_count=F('play_count') + 1
    )

    if updated:
        track = Track.objects.get(pk=track_id)
        return JsonResponse({'ok': True, 'play_count': track.play_count})

    return JsonResponse({'ok': False, 'error': 'Track not found'}, status=404)


# ─────────────────────────────────────────────────────────────
# ДЛЯ АВТОРОВ — форма отправки трека на модерацию
# ─────────────────────────────────────────────────────────────

from .models import TrackSubmission

@login_required(login_url='login')
def submit_track(request):
    """
    GET  — показать форму загрузки трека.
    POST — сохранить заявку со статусом 'pending'.
    Доступно только авторизованным пользователям.
    """
    genres_qs = Genre.objects.order_by('name')
    error     = None
    success   = False

    if request.method == 'POST':
        artist_name = request.POST.get('artist_name', '').strip()
        track_title = request.POST.get('track_title', '').strip()
        contact     = request.POST.get('contact', '').strip()
        comment     = request.POST.get('comment', '').strip()
        genre_id    = request.POST.get('genre', '').strip()
        audio_file  = request.FILES.get('audio_file')
        cover       = request.FILES.get('cover')

        # Валидация
        if not artist_name:
            error = 'Укажите имя исполнителя.'
        elif not track_title:
            error = 'Укажите название трека.'
        elif not audio_file:
            error = 'Прикрепите аудиофайл.'
        else:
            genre = None
            if genre_id:
                try:
                    genre = Genre.objects.get(pk=genre_id)
                except Genre.DoesNotExist:
                    pass

            TrackSubmission.objects.create(
                artist_name = artist_name,
                track_title = track_title,
                audio_file  = audio_file,
                cover       = cover,
                genre       = genre,
                contact     = contact,
                comment     = comment,
                status      = TrackSubmission.STATUS_PENDING,
            )
            success = True

    context = {
        'genres':  genres_qs,
        'error':   error,
        'success': success,
    }
    return render(request, 'streaming/submit.html', context)