from django.urls import path
from members.views import tier_info
app_name = 'members'

urlpatterns = [
    path('tier-info/', tier_info, name='tier_info'),
]
