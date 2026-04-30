from django.urls import path

from apps.vendors.views import daftar_hadiah, manage_mitra_view

app_name = 'vendors'

urlpatterns = [
    path('katalog_hadiah/', daftar_hadiah, name='daftar_hadiah'),
    path('manajemen-mitra/', manage_mitra_view, name='manage_mitra'),
]