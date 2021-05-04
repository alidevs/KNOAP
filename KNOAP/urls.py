"""KNOAP URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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

from api import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home),
    path('login/', views.login, name="login"),
    path('register/', views.register, name="register"),
    path('logout/', views.logout, name="logout"),
    path('add_patient/', views.add_patient, name="add_patient"),
    path('list_doctors/', views.list_all_doctors, name="list_doctors"),
    # path('test_model/', views.test_model),
    path('add_patient_file/', views.add_patient_file),
    path('patient/<int:id>/', views.to_patient, name='to_patient'),
    path('edit_patient/<int:id>/', views.edit_patient, name='to_patient')

    path('add/', views.addP, name="add_patient"),
    path('list_doctors/', views.list_all_doctors, name="list_doctors"),
    path('patient/<int:id>/', views.to_patient,name='to_patient'),
    path('edit_patient/<int:id>/', views.edit_patient, name='to_patient'),
    path('testLogin/', views.testLogin),
    path('add_patient/', views.add_patient, name="add_patient"),
]
