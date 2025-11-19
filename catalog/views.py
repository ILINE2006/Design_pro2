from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .forms import RegisterForm, ApplicationForm, ApplicationStatusForm
from .models import Application, Category, UserProfile
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import DeleteView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden


def index(request):
    """View function for home page of site."""

    num_applications_in_progress = Application.objects.filter(status='in_progress').count()
    completed_applications = Application.objects.filter(status='completed').order_by('-created_at')[:4]

    context = {
        'num_applications_in_progress': num_applications_in_progress,
        'completed_applications': completed_applications,
    }

    return render(request, 'index.html', context=context)


@login_required
def profile(request):
    return render(request, 'profile.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name']
            )

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

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)

        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.status = 'new'
            application.save()
            return redirect('my-applications')
    else:
        form = ApplicationForm()

    return render(request, 'catalog/application_form.html', {'form': form})


class ApplicationListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing applications of current user."""
    model = Application
    template_name = 'catalog/application_list.html'
    paginate_by = 10

    def get_queryset(self):
        qs = Application.objects.filter(user=self.request.user)
        status_filter = self.request.GET.get('status')

        if status_filter:
            qs = qs.filter(status=status_filter)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_status'] = self.request.GET.get('status', '')
        return context


class ApplicationDetailView(LoginRequiredMixin, generic.DetailView):
    """Generic class-based view detailing an application."""
    model = Application
    template_name = 'catalog/application_detail.html'

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)


class ApplicationDeleteView(LoginRequiredMixin, DeleteView):
    """Generic class-based view for deleting an application."""
    model = Application
    template_name = 'catalog/application_confirm_delete.html'
    success_url = reverse_lazy('my-applications')

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)

    def post(self, request, pk):
        application = get_object_or_404(Application, pk=pk, user=request.user)

        if application.can_be_deleted():
            application.delete()
            return redirect(self.success_url)
        else:
            return HttpResponseForbidden("Нельзя удалить заявку, которая уже принята в работу или выполнена.")


class CategoryListView(generic.ListView):
    """Generic class-based view listing categories."""
    model = Category
    template_name = 'catalog/category_list.html'
    context_object_name = 'category_list'


# Административные функции
@staff_member_required
def all_applications_list(request):
    """Список всех заявок для администратора."""
    applications = Application.objects.all().order_by('-created_at')
    return render(request, 'catalog/all_applications_list.html', {'application_list': applications})


@staff_member_required
def change_application_status(request, pk):
    """Изменение статуса заявки администратором с проверками."""
    application = get_object_or_404(Application, pk=pk)

    # Проверяем, можно ли менять статус
    if not application.can_change_status():
        messages.error(request, "Нельзя изменить статус заявки, которая уже принята в работу или выполнена.")
        return redirect('all-applications-list')

    if request.method == 'POST':
        form = ApplicationStatusForm(request.POST, request.FILES, instance=application)
        if form.is_valid():
            application = form.save()
            messages.success(request,
                             f'Статус заявки "{application.title}" изменен на "{application.get_status_display()}"')
            return redirect('all-applications-list')
    else:
        form = ApplicationStatusForm(instance=application)

    return render(request, 'catalog/change_application_status.html', {
        'application': application,
        'form': form
    })


# Классы для управления категориями
class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    fields = ['name']  # УБРАЛИ 'image' - теперь только название
    template_name = 'catalog/category_form.html'
    success_url = reverse_lazy('category-list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden("У вас нет прав для выполнения этого действия")
        return super().dispatch(request, *args, **kwargs)


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    fields = ['name', 'image']  # Оставили image для редактирования, но не обязательно
    template_name = 'catalog/category_form.html'
    success_url = reverse_lazy('category-list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden("У вас нет прав для выполнения этого действия")
        return super().dispatch(request, *args, **kwargs)

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'catalog/category_confirm_delete.html'
    success_url = reverse_lazy('category-list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden("У вас нет прав для выполнения этого действия")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return redirect(self.success_url)