"""
URL configuration for CoreApp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    path("", view=Home, name="homepage"),
    path("register/", view=Register, name="registerpage"),
    path("login/", view=Login, name="loginpage"),
    path('login/forgot-password/', view=ForgotPassword, name='forgotpasswordpage'),
    path('login/forgot-password/reset-password/<str:id1>/<str:id2>/', view=ResetPassword, name='resetpasswordpage'),
    path("logout/", view=Logout, name="logoutpage"),

]
