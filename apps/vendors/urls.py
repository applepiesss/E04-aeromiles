from django.urls import path

from apps.vendors.views import daftar_hadiah

app_name = 'vendors'

urlpatterns = [
    path('katalog_hadiah/', daftar_hadiah, name='daftar_hadiah'),
]