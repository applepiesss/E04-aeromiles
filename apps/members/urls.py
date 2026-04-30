from django.urls import path
from .views import kelola_member, tambah_member, edit_member, hapus_member

app_name = 'members'

urlpatterns = [
    path('kelola/', kelola_member, name='kelola_member'),
    path('kelola/tambah/', tambah_member, name='tambah_member'),
    path('kelola/edit/<str:nomor>/', edit_member, name='edit_member'),
    path('kelola/hapus/<str:nomor>/', hapus_member, name='hapus_member'),
]
