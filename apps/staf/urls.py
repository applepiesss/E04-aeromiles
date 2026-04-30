from django.urls import path
from . import views

app_name = 'staf'

urlpatterns = [
    path('laporan-transaksi/', views.laporan_transaksi, name='laporan_transaksi'),
    path('delete-transaction/', views.delete_transaction, name='delete_transaction'),
]
