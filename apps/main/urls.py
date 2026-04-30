from django.urls import path
from .views import logout_view, register_view, show_main, login_view, dashboard

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('dashboard/', dashboard, name='dashboard'),
]