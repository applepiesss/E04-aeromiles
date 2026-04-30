from django.urls import path
from .views import (
    kelola_member, tambah_member, edit_member, hapus_member,
    identitas, tambah_identitas, edit_identitas, hapus_identitas,
)

app_name = 'members'

urlpatterns = [
    path('kelola/', kelola_member, name='kelola_member'),
    path('kelola/tambah/', tambah_member, name='tambah_member'),
    path('kelola/edit/<str:nomor>/', edit_member, name='edit_member'),
    path('kelola/hapus/<str:nomor>/', hapus_member, name='hapus_member'),

    path('identitas/', identitas, name='identitas'),
    path('identitas/tambah/', tambah_identitas, name='tambah_identitas'),
    path('identitas/edit/<str:nomor>/', edit_identitas, name='edit_identitas'),
    path('identitas/hapus/<str:nomor>/', hapus_identitas, name='hapus_identitas'),
]
