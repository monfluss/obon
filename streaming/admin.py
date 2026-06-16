from django.contrib import admin
from django.db.models import Count
from .models import Track, Playlist, Genre


# --- Настройка заголовков админки ---
admin.site.site_header = "Панель управления OBON"
admin.site.site_title  = "OBON Admin"
admin.site.index_title = "Добро пожаловать в административную часть OBON"


# ══════════════════════════════════════════════════════════════
# ПРОКСИ-МОДЕЛЬ ДЛЯ РАЗДЕЛА «ИСПОЛНИТЕЛИ»
# Отдельной таблицы нет — используем ту же таблицу Track,
# но Django показывает её как самостоятельный раздел в меню.
# ══════════════════════════════════════════════════════════════

class ArtistProxy(Track):
    """
    Прокси-модель для отображения исполнителей в отдельном разделе.
    Не создаёт новую таблицу в БД — работает поверх Track.
    """
    class Meta:
        proxy               = True
        verbose_name        = "Исполнитель"
        verbose_name_plural = "Исполнители"
        ordering            = ['artist']


@admin.register(ArtistProxy)
class ArtistAdmin(admin.ModelAdmin):
    # Показываем только уникальных артистов — группировка через queryset
    list_display   = ('artist', 'track_count', 'genres_list')
    search_fields  = ('artist',)
    list_filter    = ('genre',)
    # Запрет на добавление/удаление — раздел только для просмотра и редактирования
    # (треки добавляются через раздел «Треки»)

    @admin.display(description='Треков')
    def track_count(self, obj):
        """Считаем сколько треков у этого артиста."""
        return Track.objects.filter(artist=obj.artist).count()

    @admin.display(description='Жанры')
    def genres_list(self, obj):
        """Все жанры треков данного артиста через запятую."""
        genres = (
            Track.objects
            .filter(artist=obj.artist, genre__isnull=False)
            .values_list('genre__name', flat=True)
            .distinct()
        )
        return ', '.join(genres) if genres else '—'

    def get_queryset(self, request):
        """
        Возвращаем только по одному треку на артиста (DISTINCT по полю artist).
        Так список не дублирует одного артиста N раз.
        """
        qs = super().get_queryset(request)
        # Берём первый трек каждого уникального артиста
        artist_ids = (
            qs.order_by('artist', 'id')
            .values('artist')
            .annotate(first_id=Count('id'))
            .values_list(
                qs.order_by('artist', 'id')
                  .values('artist')
                  .annotate(first_id=Count('id'))
                  .query,
                flat=False
            )
        )
        # Упрощённый вариант: distinct по artist через subquery
        from django.db.models import Min
        first_ids = (
            Track.objects
            .values('artist')
            .annotate(first_id=Min('id'))
            .values_list('first_id', flat=True)
        )
        return qs.filter(id__in=first_ids)

    def get_fields(self, request, obj=None):
        """В форме редактирования показываем только artist и cover."""
        return ('artist', 'cover')

    def save_model(self, request, obj, form, change):
        """
        При сохранении из раздела Исполнители — обновляем поле artist
        у ВСЕХ треков данного артиста (если имя было изменено).
        """
        if change:
            old_artist = Track.objects.get(pk=obj.pk).artist
            if old_artist != obj.artist:
                Track.objects.filter(artist=old_artist).update(artist=obj.artist)
        super().save_model(request, obj, form, change)


# ══════════════════════════════════════════════════════════════
# ЖАНРЫ
# ══════════════════════════════════════════════════════════════

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display        = ('name', 'slug', 'color', 'track_count')
    list_editable       = ('color',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields       = ('name',)

    @admin.display(description='Треков')
    def track_count(self, obj):
        return obj.tracks.count()


# ══════════════════════════════════════════════════════════════
# ТРЕКИ
# ══════════════════════════════════════════════════════════════

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display  = ('title', 'artist', 'genre', 'play_count', 'audio_file')
    search_fields = ('title', 'artist')
    list_filter   = ('genre',)
    list_editable = ('genre',)
    readonly_fields = ('play_count',)


# ══════════════════════════════════════════════════════════════
# ПЛЕЙЛИСТЫ
# ══════════════════════════════════════════════════════════════

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display      = ('name', 'user')
    search_fields     = ('name', 'user__username')
    filter_horizontal = ('tracks',)


# ══════════════════════════════════════════════════════════════
# ЗАЯВКИ НА ПУБЛИКАЦИЮ
# ══════════════════════════════════════════════════════════════

from django.utils import timezone
from .models import TrackSubmission


@admin.register(TrackSubmission)
class TrackSubmissionAdmin(admin.ModelAdmin):
    list_display  = (
        'track_title', 'artist_name', 'genre',
        'status', 'submitted_at', 'reviewed_at',
    )
    list_filter   = ('status', 'genre')
    search_fields = ('artist_name', 'track_title', 'contact')
    readonly_fields = (
        'submitted_at', 'reviewed_at',
        'published_track', 'audio_player',
    )
    fieldsets = (
        ('От исполнителя', {
            'fields': (
                'artist_name', 'track_title', 'genre',
                'audio_file', 'audio_player', 'cover',
                'comment', 'contact',
            )
        }),
        ('Модерация', {
            'fields': (
                'status', 'admin_note',
                'submitted_at', 'reviewed_at', 'published_track',
            )
        }),
    )
    actions = ('approve_submissions', 'reject_submissions')

    @admin.display(description='Прослушать')
    def audio_player(self, obj):
        """Встроенный плеер прямо в форме заявки."""
        from django.utils.html import format_html
        if obj.audio_file:
            return format_html(
                '<audio controls style="width:100%;margin-top:6px">'
                '<source src="{}">'
                '</audio>',
                obj.audio_file.url,
            )
        return '—'

    @admin.action(description='✅ Одобрить и опубликовать выбранные заявки')
    def approve_submissions(self, request, queryset):
        published = 0
        for sub in queryset.filter(status=TrackSubmission.STATUS_PENDING):
            # Создаём настоящий трек из заявки
            track = Track.objects.create(
                title      = sub.track_title,
                artist     = sub.artist_name,
                audio_file = sub.audio_file,
                cover      = sub.cover,
                genre      = sub.genre,
                play_count = 0,
            )
            sub.status          = TrackSubmission.STATUS_APPROVED
            sub.reviewed_at     = timezone.now()
            sub.published_track = track
            sub.save()
            published += 1
        self.message_user(
            request,
            f'Опубликовано треков: {published}',
        )

    @admin.action(description='❌ Отклонить выбранные заявки')
    def reject_submissions(self, request, queryset):
        updated = queryset.filter(
            status=TrackSubmission.STATUS_PENDING
        ).update(
            status      = TrackSubmission.STATUS_REJECTED,
            reviewed_at = timezone.now(),
        )
        self.message_user(request, f'Отклонено заявок: {updated}')