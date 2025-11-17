from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from django.views import generic
from .models import Application, Category
from .forms import ApplicationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy


def index(request):
    """View function for home page of site."""

    # Генерируем counts некоторых главных объектов
    num_applications_in_progress = Application.objects.filter(status='in_progress').count()

    # Получаем 4 последние ВЫПОЛНЕННЫЕ заявки
    num_completed_applications = Application.objects.filter(status='completed').order_by('-created_at')[:4]

    context = {
        'num_applications_in_progress': num_applications_in_progress,
        'completed_applications': num_completed_applications,
    }

    # Рендерим HTML-шаблон index.html с данными внутри переменной context
    return render(request, 'index.html', context=context)


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


@login_required
def create_application(request):
    """View function for creating an application."""

    # Если это POST запрос, обрабатываем данные формы
    if request.method == 'POST':

        # Создаем экземпляр формы и заполняем данными из запроса:
        form = ApplicationForm(request.POST, request.FILES)

        # Проверяем валидность формы:
        if form.is_valid():
            # Обрабатываем данные в form.cleaned_data
            application = form.save(commit=False)
            application.user = request.user
            application.status = 'n'  # Статус "Новая"
            application.save()

            # Перенаправляем на страницу с заявками:
            return redirect('my-applications')

    # Если это GET (или любой другой) запрос, создаем пустую форму
    else:
        form = ApplicationForm()

    return render(request, 'catalog/application_form.html', {'form': form})


class ApplicationListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing applications of current user."""
    model = Application
    template_name = 'catalog/application_list.html'
    paginate_by = 10

    def get_queryset(self):
        # Получаем базовый queryset - все заявки пользователя
        qs = Application.objects.filter(user=self.request.user)

        # Получаем параметр фильтра из GET-запроса
        status_filter = self.request.GET.get('status', None)

        # Если параметр передан и он не пустой, применяем фильтр
        if status_filter:
            qs = qs.filter(status=status_filter)

        return qs

    def get_context_data(self, **kwargs):
        # Добавляем в контекст текущее значение фильтра
        context = super().get_context_data(**kwargs)
        context['current_status'] = self.request.GET.get('status', '')
        return context


class ApplicationDeleteView(LoginRequiredMixin, DeleteView):
    """Generic class-based view for deleting an application."""
    model = Application
    template_name = 'catalog/application_confirm_delete.html'
    success_url = reverse_lazy('my-applications')

    def get_queryset(self):
        # Пользователь может удалять только свои заявки
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        # Получаем объект для удаления
        self.object = self.get_object()

        # Проверяем, можно ли удалять заявку (статус "Новая")
        if self.object.can_be_deleted():
            return super().delete(request, *args, **kwargs)
        else:
            # Если статус не "Новая", возвращаем ошибку
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("Нельзя удалить заявку, которая уже принята в работу или выполнена.")

class CategoryListView(generic.ListView):
    """Generic class-based view listing categories."""
    model = Category
    template_name = 'catalog/category_list.html'
    context_object_name = 'category_list'