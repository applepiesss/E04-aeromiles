from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from datetime import datetime


# Hardcoded data for Award Miles Package
AWARD_MILES_PACKAGE = [
    {
        'id': 'AMP-001',
        'harga_paket': 150000.00,
        'jumlah_award_miles': 1000,
    },
    {
        'id': 'AMP-002',
        'harga_paket': 650000.00,
        'jumlah_award_miles': 5000,
    },
    {
        'id': 'AMP-003',
        'harga_paket': 1250000.00,
        'jumlah_award_miles': 10000,
    },
    {
        'id': 'AMP-004',
        'harga_paket': 2800000.00,
        'jumlah_award_miles': 25000,
    },
    {
        'id': 'AMP-005',
        'harga_paket': 5200000.00,
        'jumlah_award_miles': 50000,
    },
]

# Member's current award miles balance
MEMBER_AWARD_MILES = {
    'MEM0001234': 0,  # john.doe@aeromiles.com
}

# Transaction history for buying award miles packages
MEMBER_AWARD_MILES_PACKAGE = [
    {
        'id': 1,
        'id_award_miles_package': 'AMP-001',
        'email_member': 'john.doe@aeromiles.com',
        'harga_paket': 150000.00,
        'jumlah_award_miles': 1000,
        'waktu': '2024-01-15 10:30:00',
    },
    {
        'id': 2,
        'id_award_miles_package': 'AMP-002',
        'email_member': 'john.doe@aeromiles.com',
        'harga_paket': 650000.00,
        'jumlah_award_miles': 5000,
        'waktu': '2024-02-20 14:15:00',
    },
    {
        'id': 3,
        'id_award_miles_package': 'AMP-001',
        'email_member': 'john.doe@aeromiles.com',
        'harga_paket': 150000.00,
        'jumlah_award_miles': 1000,
        'waktu': '2024-03-10 09:45:00',
    },
]

# Member data for reference
MEMBER_DATA = {
    'type': 'member',
    'salutation': 'Mr.',
    'first_mid_name': 'John Michael',
    'last_name': 'Doe',
    'email': 'john.doe@aeromiles.com',
    'country_code': '+1',
    'phone_number': '555-0123',
    'nationality': 'American',
    'date_of_birth': '1990-05-15',
    'member_number': 'MEM0001234',
    'join_date': '2020-01-15',
}


@require_http_methods(["GET"])
def buy_miles_package(request):
    """Display award miles packages for purchase"""
    # For mockup, use hardcoded member
    member_id = 'MEM0001234'
    current_award_miles = MEMBER_AWARD_MILES.get(member_id, 0)
    
    # Calculate total award miles from all transactions
    for transaction in MEMBER_AWARD_MILES_PACKAGE:
        if transaction['email_member'] == MEMBER_DATA['email']:
            current_award_miles += transaction['jumlah_award_miles']
    
    # Update in MEMBER_AWARD_MILES
    MEMBER_AWARD_MILES[member_id] = current_award_miles
    
    # Get all available packages
    packages = AWARD_MILES_PACKAGE.copy()
    
    # Get transaction history
    history = [t for t in MEMBER_AWARD_MILES_PACKAGE if t['email_member'] == MEMBER_DATA['email']]
    
    context = {
        'member_id': member_id,
        'current_award_miles': current_award_miles,
        'packages': packages,
        'transaction_history': history,
        'member_name': MEMBER_DATA['first_mid_name'] + ' ' + MEMBER_DATA['last_name'],
        'member_email': MEMBER_DATA['email'],
    }
    
    return render(request, 'buy_miles_package.html', context)


@require_http_methods(["POST"])
def process_buy_package(request):
    """Process award miles package purchase"""
    member_id = 'MEM0001234'
    paket_id = request.POST.get('paket_id', '')
    
    # Find package
    package_found = None
    for pkg in AWARD_MILES_PACKAGE:
        if pkg['id'] == paket_id:
            package_found = pkg
            break
    
    if not package_found:
        messages.error(request, 'Paket tidak ditemukan.')
        return redirect('miles:buy_miles_package')
    
    # Add to member's award miles
    current_miles = MEMBER_AWARD_MILES.get(member_id, 0)
    new_miles = current_miles + package_found['jumlah_award_miles']
    MEMBER_AWARD_MILES[member_id] = new_miles
    
    # Record transaction (mockup)
    new_transaction = {
        'id': len(MEMBER_AWARD_MILES_PACKAGE) + 1,
        'id_award_miles_package': package_found['id'],
        'email_member': MEMBER_DATA['email'],
        'harga_paket': package_found['harga_paket'],
        'jumlah_award_miles': package_found['jumlah_award_miles'],
        'waktu': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    MEMBER_AWARD_MILES_PACKAGE.insert(0, new_transaction)  # Add to beginning
    
    messages.success(request, f'Paket {package_found["id"]} berhasil dibeli! {package_found["jumlah_award_miles"]} award miles telah ditambahkan ke akun Anda.')
    return redirect('miles:buy_miles_package')
