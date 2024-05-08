"""ParentDrive_Connect URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from dashboard import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('index.html',views.index,name='index'),
    path('login.html',views.login,name='login'),
    path('signup.html', views.signup_view, name='signup'),
    path('Driver.html', views.Driver, name='Driver'),
    path('parentdashboard.html', views.parentdashboard, name='parentdashboard'),
    path('generate_response',views.generate_response,name='generate_response'),
    path('view_dat',views.view_dat,name='view_dat'),
    path('view_maps',views.view_maps,name='view_maps'),
    path('forgot_password',views.forgot_password,name='forgot_password'),



] 


