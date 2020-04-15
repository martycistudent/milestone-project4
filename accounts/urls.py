from django.urls import path, include
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout, name='logout'),
    path('login/', views.login, name='login'),
    path('password-reset/', include('.urls_reset')),
]
