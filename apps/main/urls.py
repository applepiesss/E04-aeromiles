from django.urls import path
from main.views import show_main, login_view

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('login/', login_view, name='login'),
]