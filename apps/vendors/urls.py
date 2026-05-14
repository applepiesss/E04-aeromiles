from django.urls import path

from apps.vendors.views import daftar_hadiah, save_hadiah, delete_hadiah, manage_mitra_view, save_mitra, delete_mitra

app_name = 'vendors'

urlpatterns = [
    path('katalog_hadiah/', daftar_hadiah, name='daftar_hadiah'),
    path('katalog-hadiah/save/', save_hadiah, name='save_hadiah'),
    path('katalog-hadiah/delete/', delete_hadiah, name='delete_hadiah'),
    path('manajemen-mitra/', manage_mitra_view, name='manage_mitra'),
    path('manajemen-mitra/save/', save_mitra, name='save_mitra'),
    path('manajemen-mitra/delete/', delete_mitra, name='delete_mitra'),
]