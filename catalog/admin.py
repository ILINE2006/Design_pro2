from django.contrib import admin
from django.utils.html import mark_safe
from .models import Category, Application


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_preview')

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" style="object-fit: cover;" />')
        return "Нет фото"

    image_preview.short_description = 'Фото'


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'display_status', 'created_at')
    list_filter = ('status', 'category', 'created_at')

    def display_status(self, obj):
        return obj.get_status_display()

    display_status.short_description = 'Status'


admin.site.register(Category, CategoryAdmin)
admin.site.register(Application, ApplicationAdmin)