from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Genre(models.Model):
    name        = models.CharField(max_length=100, unique=True, verbose_name="Название")
    slug        = models.SlugField(max_length=120, unique=True, blank=True, verbose_name="URL-slug")
    description = models.TextField(blank=True, verbose_name="Описание")
    color       = models.CharField(
        max_length=7,
        default='#282828',
        verbose_name="Цвет карточки (hex)",
        help_text="Например: #1e3a5f",
    )
    cover       = models.ImageField(
        upload_to='genres/',
        null=True,
        blank=True,
        verbose_name="Обложка жанра",
    )

    class Meta:
        verbose_name        = "Жанр"
        verbose_name_plural = "Жанры"
        ordering            = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Автогенерация slug из названия если не задан вручную
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=False)
            # Если кириллица — делаем транслит вручную
            if not self.slug:
                self.slug = slugify(self._translit(self.name))
        super().save(*args, **kwargs)

    @staticmethod
    def _translit(text):
        """Простой транслит кириллицы → латиница для slug."""
        ru = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
        en = 'abvgdeyozhziyklmnoprstufxtschshhuyeluaABVGDEYOZHZIYKLMNOPRSTUFXTSCHSHHUYELUA'
        table = str.maketrans(ru, en)
        return text.translate(table)


# ─── Track — добавлено только поле genre, всё остальное без изменений ───

class Track(models.Model):
    title      = models.CharField(max_length=100, verbose_name="Название")
    artist     = models.CharField(max_length=100, verbose_name="Артист")
    audio_file = models.FileField(upload_to='music/', verbose_name="Файл трека")
    cover      = models.ImageField(upload_to='covers/', null=True, blank=True, verbose_name="Обложка")
    play_count = models.IntegerField(default=0, verbose_name="Прослушивания")

    # ← НОВОЕ: связь с жанром (SET_NULL — трек не удалится если жанр удалят)
    genre      = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tracks',
        verbose_name="Жанр",
    )

    def __str__(self):
        return f"{self.artist} - {self.title}"


# ─── Playlist — без изменений ────────────────────────────────────────────

class Playlist(models.Model):
    user   = models.ForeignKey(User, on_delete=models.CASCADE)
    name   = models.CharField(max_length=100, verbose_name="Название плейлиста")
    tracks = models.ManyToManyField(Track, related_name="playlists")

    def __str__(self):
        return self.name


class TrackSubmission(models.Model):
    """
    Заявка исполнителя на добавление трека.
    После одобрения администратором создаётся настоящий Track.
    """

    STATUS_PENDING  = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING,  '⏳ На модерации'),
        (STATUS_APPROVED, '✅ Одобрено'),
        (STATUS_REJECTED, '❌ Отклонено'),
    ]

    # ── Данные от исполнителя ────────────────────────────────
    artist_name  = models.CharField(max_length=100, verbose_name="Имя исполнителя")
    track_title  = models.CharField(max_length=200, verbose_name="Название трека")
    audio_file   = models.FileField(upload_to='submissions/audio/', verbose_name="Аудиофайл")
    cover        = models.ImageField(
        upload_to='submissions/covers/',
        null=True, blank=True,
        verbose_name="Обложка",
    )
    genre        = models.ForeignKey(
        'Genre',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Жанр",
    )
    comment      = models.TextField(
        blank=True,
        verbose_name="Комментарий исполнителя",
        help_text="Краткое описание трека, ссылки на соцсети и т.д.",
    )
    contact      = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Контакт (email / Telegram)",
    )

    # ── Модерация ────────────────────────────────────────────
    status       = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name="Статус",
    )
    admin_note   = models.TextField(
        blank=True,
        verbose_name="Заметка администратора",
        help_text="Причина отклонения или комментарий — видит только администратор",
    )
    reviewed_at  = models.DateTimeField(null=True, blank=True, verbose_name="Дата решения")
    published_track = models.OneToOneField(
        'Track',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='submission',
        verbose_name="Опубликованный трек",
    )

    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата заявки")

    class Meta:
        verbose_name        = "Заявка на публикацию"
        verbose_name_plural = "Заявки на публикацию"
        ordering            = ['-submitted_at']

    def __str__(self):
        return f"{self.artist_name} — {self.track_title} [{self.get_status_display()}]"