from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('applications/', views.ApplicationListView.as_view(), name='my-applications'),
    path('application/<int:pk>', views.ApplicationDetailView.as_view(), name='application-detail'),
    path('application/create/', views.create_application, name='application-create'),
    path('application/<int:pk>/delete/', views.ApplicationDeleteView.as_view(), name='application-delete'),
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
]