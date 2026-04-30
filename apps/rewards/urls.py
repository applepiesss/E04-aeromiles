from django.urls import path
from .views import redeem_hadiah, process_redeem

app_name = 'rewards'

urlpatterns = [
    path('redeem-hadiah/', redeem_hadiah, name='redeem_hadiah'),
    path('process-redeem/', process_redeem, name='process_redeem'),
]
