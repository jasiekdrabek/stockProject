from django.urls import path
from . import views

urlpatterns = [
    path('api/signIn', views.signIn, name='signIn'),
    path('api/signUp', views.signUp, name='signUp'),
]