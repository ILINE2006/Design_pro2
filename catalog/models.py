from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Category(models.Model):
    """Модель представляющая категорию заявки."""
    name = models.CharField(max_length=100, help_text="Введите название категории")

    image = models.ImageField(
        upload_to='categories/',
        verbose_name='Изображение категории',
        help_text='Загрузите изображение для категории (необязательно)',
        blank=True,
        null=True
    )

    def __str__(self):
        """Строка для представления объекта Model."""
        return self.name

    def get_absolute_url(self):
        """Возвращает URL для доступа к конкретному экземпляру категории."""
        return reverse('category-detail', args=[str(self.id)])

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

    # Поле для изображения помещения
    image = models.ImageField(
        upload_to='applications/',
        null=True,
        blank=True,
        help_text="Загрузите фото помещения (JPG, JPEG, PNG, BMP, макс. 2MB)"
    )

    #  изображение дизайна (для статуса "Выполнено")
    design_image = models.ImageField(
        upload_to='designs/',
        null=True,
        blank=True,
        verbose_name='Изображение дизайна',
        help_text="Загрузите изображение готового дизайна"
    )

    #  комментарий администратора (для статуса "Принято в работу")
    admin_comment = models.TextField(
        max_length=1000,
        blank=True,
        verbose_name='Комментарий администратора',
        help_text="Комментарий при принятии заявки в работу"
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

    def can_change_status(self):
        """Можно менять статус только у заявок со статусом 'Новая'"""
        return self.status == 'new'


class UserProfile(models.Model):
    """Модель для расширения пользователя (администратор/сотрудник)."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_employee = models.BooleanField(default=False, verbose_name="Сотрудник")

    def __str__(self):
        return f"{self.user.username} - {'Сотрудник' if self.is_employee else 'Клиент'}"


# Автоматическое создание профиля при создании пользователя
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
    else:
        UserProfile.objects.create(user=instance)