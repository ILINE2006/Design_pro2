from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from .models import Application



class RegisterForm(forms.Form):
    first_name = forms.CharField(label='ФИО', max_length=100)
    username = forms.CharField(label='Логин', max_length=100)
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password_confirm = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput)
    agree_to_terms = forms.BooleanField(label='Согласие на обработку персональных данных')

    def clean_first_name(self):
        data = self.cleaned_data['first_name']
        if not re.match(r'^[а-яА-ЯёЁ\s\-]+$', data):
            raise ValidationError('Только кириллица, пробелы и дефис')
        return data

    def clean_username(self):
        data = self.cleaned_data['username']
        if not re.match(r'^[a-zA-Z\-]+$', data):
            raise ValidationError('Только латиница и дефис')
        if User.objects.filter(username=data).exists():
            raise ValidationError('Логин уже занят')
        return data

    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise ValidationError('Email уже используется')
        return data

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise ValidationError('Пароли не совпадают')

        return cleaned_data


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['title', 'description', 'category', 'image']
        labels = {
            'title': 'Название заявки',
            'description': 'Описание',
            'category': 'Категория',
            'image': 'Фото помещения',
        }
        help_texts = {
            'title': 'Введите краткое название заявки',
            'description': 'Подробно опишите, что нужно сделать',
            'category': 'Выберите подходящую категорию',
            'image': 'Загрузите фото или план помещения',
        }

    def clean_image(self):
        image = self.cleaned_data.get('image', False)
        if image:
            if image.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Размер изображения не должен превышать 2MB")
            return image
        else:
            raise forms.ValidationError("Не удалось прочитать загруженное изображение")