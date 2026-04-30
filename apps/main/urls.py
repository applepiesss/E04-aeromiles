from django.urls import path
from .views import show_main, login_view, dashboard

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
]