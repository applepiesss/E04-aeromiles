from django.urls import path
from main.views import show_main, profile_settings, change_password
from .views import show_main, login_view, dashboard

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('profile-settings/', profile_settings, name='profile_settings'),
    path('change-password/', change_password, name='change_password'),
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('vendors/', include('apps.vendors.urls')),
]