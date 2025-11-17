from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm


def index(request):
    return render(request, 'index.html')


@login_required
def profile(request):
    return render(request, 'profile.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            # Создаем пользователя
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name']
            )

            # Автоматический вход
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            login(request, user)

            return redirect('profile')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})