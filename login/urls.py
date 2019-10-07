from django.urls import path 
from django.contrib.auth import views as auth_views
from .views import LoginView, WelcomeUser, LogoutView, RegistrationView
from django.conf.urls import url
import pdb
from . import views

urlpatterns = [
    url('login/', LoginView.as_view(), name='login'),
    url('logout/', LogoutView.as_view(), name='logout'),
    url('register/', RegistrationView.as_view(), name='register'),
    url('welcome/', WelcomeUser.as_view(), name='welcome'),
]