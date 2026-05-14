from django.urls import path
from apps.miles.views import claim_approve, claim_create, claim_delete, claim_edit, claim_member_list, claim_reject, claim_staff_list, transfer_create, transfer_list
from .views import buy_miles_package, process_buy_package

app_name = 'miles'

urlpatterns = [
    path('claim/', claim_member_list, name='claim_member_list'),
    path('claim/create/', claim_create, name='claim_create'),
    path('claim/<int:claim_id>/edit/', claim_edit, name='claim_edit'),
    path('claim/<int:claim_id>/delete/', claim_delete, name='claim_delete'),

    path('staff/claim/', claim_staff_list, name='claim_staff_list'),
    path('staff/claim/<int:claim_id>/approve/', claim_approve, name='claim_approve'),
    path('staff/claim/<int:claim_id>/reject/', claim_reject, name='claim_reject'),

    path('transfer/', transfer_list, name='transfer_list'),
    path('transfer/create/', transfer_create, name='transfer_create'),
    path('buy-miles-package/', buy_miles_package, name='buy_miles_package'),
    path('process-buy-package/', process_buy_package, name='process_buy_package'),
]