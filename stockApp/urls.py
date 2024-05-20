from django.urls import path
from . import views

urlpatterns = [
    path('api/signIn', views.signIn, name='signIn'),
    path('api/signUp', views.signUp, name='signUp'),
    path('api/addCompany', views.createCompany, name='addCompany'),
    path('api/companies', views.companies, name='companies'),
    path('api/addBuyOffer', views.addBuyOffer, name='addBuyOffer'),
]