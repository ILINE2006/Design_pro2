from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from django.views import generic
from .models import Application, Category
from .forms import ApplicationForm



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


class ApplicationListView(generic.ListView):
    """Generic class-based view listing applications of current user."""
    model = Application
    template_name = 'catalog/application_list.html'
    paginate_by = 10

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)


class ApplicationDetailView(generic.DetailView):
    """Generic class-based view detailing an application."""
    model = Application
    template_name = 'catalog/application_detail.html'

class CategoryListView(generic.ListView):
    """Generic class-based view listing categories."""
    model = Category
    template_name = 'catalog/category_list.html'
    context_object_name = 'category_list'