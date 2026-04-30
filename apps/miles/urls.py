from django.urls import path
from .views import buy_miles_package, process_buy_package

app_name = 'miles'

urlpatterns = [
    path('buy-miles-package/', buy_miles_package, name='buy_miles_package'),
    path('process-buy-package/', process_buy_package, name='process_buy_package'),
]
