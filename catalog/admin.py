from django.contrib import admin
from django.utils.html import mark_safe
from django import forms
from .models import Category, Application


class ApplicationAdminForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        design_image = cleaned_data.get('design_image')
        admin_comment = cleaned_data.get('admin_comment')

        # Проверка для статуса "Выполнено"
        if status == 'completed' and not design_image:
            raise forms.ValidationError("Для статуса 'Выполнено' обязательно нужно загрузить изображение дизайна.")

        # Проверка для статуса "Принято в работу"
        if status == 'in_progress' and not admin_comment:
            raise forms.ValidationError("Для статуса 'Принято в работу' обязательно нужно указать комментарий.")

        return cleaned_data


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_preview')

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" style="object-fit: cover;" />')
        return "Нет фото"

    image_preview.short_description = 'Фото'


class ApplicationAdmin(admin.ModelAdmin):
    form = ApplicationAdminForm
    list_display = ('title', 'user', 'category', 'display_status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'category', 'user')
        }),
        ('Изображения', {
            'fields': ('image', 'design_image')
        }),
        ('Статус и комментарии', {
            'fields': ('status', 'admin_comment', 'created_at', 'updated_at')
        }),
    )

    def display_status(self, obj):
        return obj.get_status_display()

    display_status.short_description = 'Status'


admin.site.register(Category, CategoryAdmin)
admin.site.register(Application, ApplicationAdmin)