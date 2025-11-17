from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class Category(models.Model):
    """Модель представляющая категорию заявки."""
    name = models.CharField(max_length=100, help_text="Введите название категории")

    # ДОБАВЬТЕ ЭТО ПОЛЕ ↓
    image = models.ImageField(
        upload_to='categories/',
        verbose_name='Изображение категории',
        help_text='Загрузите изображение для категории',
        blank=True,
        null=True
    )

    def __str__(self):
        """Строка для представления объекта Model."""
        return self.name

    def get_absolute_url(self):
        """Возвращает URL для доступа к конкретному экземпляру категории."""
        return reverse('category-detail', args=[str(self.id)])

    # ДОБАВЬТЕ ЭТОТ МЕТОД ↓
    def image_url(self):
        """Возвращает URL изображения или None если его нет."""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return None


class Application(models.Model):
    """Модель представляющая заявку пользователя."""
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=1000, help_text="Введите описание заявки")

    # Внешний ключ на Category
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        help_text="Выберите категорию для этой заявки"
    )

    # Поле для изображения
    image = models.ImageField(
        upload_to='applications/',
        null=True,
        blank=True,
        help_text="Загрузите фото помещения (JPG, JPEG, PNG, BMP, макс. 2MB)"
    )

    # Статус заявки
    LOAN_STATUS = (
        ('new', 'Новая'),
        ('in_progress', 'Принято в работу'),
        ('completed', 'Выполнено'),
    )

    status = models.CharField(
        max_length=20,
        choices=LOAN_STATUS,
        blank=True,
        default='new',
        help_text='Статус заявки',
    )

    # Даты
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Внешний ключ на пользователя
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        """Строка для представления объекта Model."""
        return self.title

    def get_absolute_url(self):
        """Возвращает URL для доступа к деталям этой заявки."""
        return reverse('application-detail', args=[str(self.id)])

    def display_category(self):
        """Создает строку для категории. Это требуется для отображения в Admin."""
        return self.category.name

    display_category.short_description = 'Category'

    def can_be_deleted(self):
        """Можно удалять только заявки со статусом 'Новая'"""
        return self.status == 'new'