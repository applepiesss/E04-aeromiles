from django.urls import path
from main.views import show_main, profile_settings, change_password

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('profile-settings/', profile_settings, name='profile_settings'),
    path('change-password/', change_password, name='change_password'),
]