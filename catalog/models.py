from django.db import models
from django.urls import reverse
import uuid
from datetime import date
from django.conf import settings
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.core.exceptions import ValidationError

class Genre(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Введите жанр книги (например, Научная фантастика, Французская поэзия и т.д.)"
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('genre-detail', args=[str(self.id)])

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower('name'),
                name='genre_name_case_insensitive_unique',
                violation_error_message = "Жанр уже существует (без учета регистра)"
            ),
        ]
        verbose_name="Жанр"
        verbose_name_plural="Жанры"

class Language(models.Model):
    name = models.CharField(max_length=200,
                            unique=True,
                            help_text="Введите естественный язык книги (например, Английский, Французский, Японский и т.д.)")

    def get_absolute_url(self):
        return reverse('language-detail', args=[str(self.id)])

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower('name'),
                name='language_name_case_insensitive_unique',
                violation_error_message = "Язык уже существует (без учета регистра)"
            ),
        ]
        verbose_name = "Язык"
        verbose_name_plural = "Языки"

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.RESTRICT, null=True, verbose_name="Автор")
    summary = models.TextField(
        max_length=1000, help_text="Введите краткое описание книги", verbose_name="Описание")
    isbn = models.CharField('ISBN', max_length=13,
                            unique=True,
                            help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn'
                                      '">ISBN number</a>')
    genre = models.ManyToManyField(
        Genre, help_text="Выберите жанр для этой книги", verbose_name="Жанр")
    language = models.ForeignKey(
        'Language', on_delete=models.SET_NULL, null=True, verbose_name="Язык")

    class Meta:
        ordering = ['title', 'author']
        verbose_name = "Книга"
        verbose_name_plural = "Книги"

    def display_genre(self):
        return ', '.join([genre.name for genre in self.genre.all()[:3]])

    display_genre.short_description = 'Жанр'

    def get_absolute_url(self):
        return reverse('book-detail', args=[str(self.id)])

    def __str__(self):
        return self.title


class BookInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Уникальный ID для этой книги во всей библиотеке")
    book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True, verbose_name="Книга")
    imprint = models.CharField(max_length=200, verbose_name="Издательство")
    due_back = models.DateField(null=True, blank=True, verbose_name="Дата возврата")
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Заемщик")

    LOAN_STATUS = (
        ('d', 'Обслуживается'),
        ('o', 'Выдано'),
        ('a', 'Доступно'),
        ('r', 'Зарезервировано'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='d',
        help_text='Доступность книги',
        verbose_name="Статус")

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Отметить книгу как возвращенную"),)
        verbose_name = "Экземпляр книги"
        verbose_name_plural = "Экземпляры книг"

    def clean(self):
        if self.status == 'o' and not self.due_back:
            raise ValidationError({
                'due_back': 'Дата возврата обязательна для статуса "Выдано"'
            })

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        return bool(self.due_back and date.today() > self.due_back)

    def get_absolute_url(self):
        return reverse('bookinstance-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.id} ({self.book.title})'

class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"

    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

