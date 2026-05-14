from django.shortcuts import render, redirect

app_name = 'miles'

def require_member(request):
    return request.session.get('role') == 'member'

def require_staff(request):
    return request.session.get('role') == 'staff'

DUMMY_MASKAPAI = {
    'GA': {'nama_maskapai': 'Garuda Indonesia', 'id_penyedia': 1},
    'QG': {'nama_maskapai': 'Citilink',         'id_penyedia': 2},
    'JT': {'nama_maskapai': 'Lion Air',         'id_penyedia': 3},
    'SJ': {'nama_maskapai': 'Sriwijaya Air',    'id_penyedia': 4},
    'ID': {'nama_maskapai': 'Batik Air',        'id_penyedia': 5},
}

DUMMY_BANDARA = {
    'CGK': {'nama': 'Soekarno-Hatta International Airport', 'kota': 'Jakarta',       'negara': 'Indonesia'},
    'DPS': {'nama': 'Ngurah Rai International Airport',     'kota': 'Bali',          'negara': 'Indonesia'},
    'SUB': {'nama': 'Juanda International Airport',         'kota': 'Surabaya',      'negara': 'Indonesia'},
    'KNO': {'nama': 'Kualanamu International Airport',      'kota': 'Medan',         'negara': 'Indonesia'},
    'YIA': {'nama': 'Yogyakarta International Airport',     'kota': 'Yogyakarta',    'negara': 'Indonesia'},
    'SIN': {'nama': 'Changi Airport',                       'kota': 'Singapore',     'negara': 'Singapore'},
    'KUL': {'nama': 'Kuala Lumpur International Airport',   'kota': 'Kuala Lumpur',  'negara': 'Malaysia'},
    'BKK': {'nama': 'Suvarnabhumi Airport',                 'kota': 'Bangkok',       'negara': 'Thailand'},
    'HND': {'nama': 'Haneda Airport',                       'kota': 'Tokyo',         'negara': 'Japan'},
    'ICN': {'nama': 'Incheon International Airport',        'kota': 'Seoul',         'negara': 'South Korea'},
    'DXB': {'nama': 'Dubai International Airport',          'kota': 'Dubai',         'negara': 'United Arab Emirates'},
    'LHR': {'nama': 'Heathrow Airport',                     'kota': 'London',        'negara': 'United Kingdom'},
    'CDG': {'nama': 'Charles de Gaulle Airport',            'kota': 'Paris',         'negara': 'France'},
    'JFK': {'nama': 'John F. Kennedy International Airport','kota': 'New York',      'negara': 'United States'},
    'SYD': {'nama': 'Sydney Kingsford Smith Airport',       'kota': 'Sydney',        'negara': 'Australia'},
}

DUMMY_CLAIMS_MEMBER = {
    1: {
        'id': 1, 'maskapai': 'GA', 'bandara_asal': 'CGK', 'bandara_tujuan': 'DPS',
        'tanggal_penerbangan': '2023-12-01', 'flight_number': 'GA404',
        'nomor_tiket': '1260000001', 'kelas_kabin': 'Economy', 'pnr': 'ABCDEF',
        'status_penerimaan': 'Disetujui', 'waktu_penerbangan': '2023-12-01 10:00:00',
        'email_staf': 'harry.potter@ui.ac.id',
    },
    2: {
        'id': 2, 'maskapai': 'QG', 'bandara_asal': 'SUB', 'bandara_tujuan': 'CGK',
        'tanggal_penerbangan': '2024-01-10', 'flight_number': 'QG712',
        'nomor_tiket': '1260000002', 'kelas_kabin': 'Economy', 'pnr': 'QWERTY',
        'status_penerimaan': 'Menunggu', 'waktu_penerbangan': '2024-01-10 14:30:00',
        'email_staf': None,
    },
    3: {
        'id': 3, 'maskapai': 'JT', 'bandara_asal': 'KNO', 'bandara_tujuan': 'SIN',
        'tanggal_penerbangan': '2024-02-15', 'flight_number': 'JT202',
        'nomor_tiket': '1260000003', 'kelas_kabin': 'Business', 'pnr': 'ZXCVBN',
        'status_penerimaan': 'Ditolak', 'waktu_penerbangan': '2024-02-15 09:15:00',
        'email_staf': 'luna.lovegood@ui.ac.id',
    },
}

DUMMY_CLAIMS_STAFF = {
    1:  {
        'id': 1,  'nama_member': 'Ms. Strawberry Shortcake', 'email_member': 'strawberry.shortcake@gmail.com',
        'maskapai': 'GA', 'bandara_asal': 'CGK', 'bandara_tujuan': 'DPS',
        'tanggal_penerbangan': '2023-12-01', 'flight_number': 'GA404', 'kelas_kabin': 'Economy',
        'waktu_penerbangan': '2023-12-01 10:00:00', 'status_penerimaan': 'Disetujui',
    }
}

DUMMY_TRANSFERS = {
    ('tony.stark@gmail.com', 'peter.parker@gmail.com', '2025-01-10 09:15:00'): {
        'timestamp': '2025-01-10 09:15:00',
        'email_member_1': 'tony.stark@gmail.com',
        'email_member_2': 'peter.parker@gmail.com',
        'nama_lawan': 'Mr. Peter Parker',
        'email_lawan': 'peter.parker@gmail.com',
        'jumlah': 5000,
        'catatan': 'Dana tambahan untuk perlengkapan magang Stark Industries',
        'tipe': 'Kirim',
    },
}

def maskapai_as_list():
    return [(k, v['nama_maskapai']) for k, v in DUMMY_MASKAPAI.items()]

def bandara_as_list():
    return [(k, v['nama'], v['kota'], v['negara']) for k, v in DUMMY_BANDARA.items()]

def claim_member_list(request):
    if not require_member(request):
        return redirect('main:login')

    status_filter = request.GET.get('status', '')
    claims = list(DUMMY_CLAIMS_MEMBER.values())

    if status_filter in ('Menunggu', 'Disetujui', 'Ditolak'):
        claims = [c for c in claims if c['status_penerimaan'] == status_filter]

    for c in claims:
        asal  = DUMMY_BANDARA.get(c['bandara_asal'], {})
        tujuan = DUMMY_BANDARA.get(c['bandara_tujuan'], {})
        c['nama_asal']   = f"{c['bandara_asal']} – {asal.get('kota', '')}"
        c['nama_tujuan'] = f"{c['bandara_tujuan']} – {tujuan.get('kota', '')}"
        c['nama_maskapai'] = DUMMY_MASKAPAI.get(c['maskapai'], {}).get('nama_maskapai', c['maskapai'])

    return render(request, 'claim_member.html', {
        'claims': claims,
        'status_filter': status_filter,
        'maskapai_list': maskapai_as_list(),
        'bandara_list': bandara_as_list(),
    })

def claim_create(request):
    if not require_member(request):
        return redirect('main:login')

    if request.method == 'POST':
        errors = []
        fields = ['maskapai', 'bandara_asal', 'bandara_tujuan',
                'tanggal_penerbangan', 'flight_number',
                'nomor_tiket', 'kelas_kabin', 'pnr']
        for f in fields:
            if not request.POST.get(f, '').strip():
                errors.append(f'Field {f} wajib diisi.')
                break

        if errors:
            claims = list(DUMMY_CLAIMS_MEMBER.values())
            for c in claims:
                asal   = DUMMY_BANDARA.get(c['bandara_asal'], {})
                tujuan = DUMMY_BANDARA.get(c['bandara_tujuan'], {})
                c['nama_asal']     = f"{c['bandara_asal']} – {asal.get('kota', '')}"
                c['nama_tujuan']   = f"{c['bandara_tujuan']} – {tujuan.get('kota', '')}"
                c['nama_maskapai'] = DUMMY_MASKAPAI.get(c['maskapai'], {}).get('nama_maskapai', c['maskapai'])

            return render(request, 'claim_member.html', {
                'errors': errors,
                'maskapai_list': maskapai_as_list(),
                'bandara_list': bandara_as_list(),
                'claims': claims,
                'status_filter': '',
                'show_modal': True,
                'form': request.POST,
            })

        return redirect('miles:claim_member_list')

    return redirect('miles:claim_member_list')


def claim_edit(request, claim_id):
    if not require_member(request):
        return redirect('main:login')
    return redirect('miles:claim_member_list')


def claim_delete(request, claim_id):
    if not require_member(request):
        return redirect('main:login')
    return redirect('miles:claim_member_list')

def claim_staff_list(request):
    if not require_staff(request):
        return redirect('main:login')

    status_filter   = request.GET.get('status', '')
    maskapai_filter = request.GET.get('maskapai', '')

    claims = list(DUMMY_CLAIMS_STAFF.values())

    if status_filter in ('Menunggu', 'Disetujui', 'Ditolak'):
        claims = [c for c in claims if c['status_penerimaan'] == status_filter]
    if maskapai_filter:
        claims = [c for c in claims if c['maskapai'] == maskapai_filter]

    for c in claims:
        asal   = DUMMY_BANDARA.get(c['bandara_asal'], {})
        tujuan = DUMMY_BANDARA.get(c['bandara_tujuan'], {})
        c['rute'] = f"{c['bandara_asal']} ({asal.get('kota','')}) → {c['bandara_tujuan']} ({tujuan.get('kota','')})"
        c['nama_maskapai'] = DUMMY_MASKAPAI.get(c['maskapai'], {}).get('nama_maskapai', c['maskapai'])

    return render(request, 'claim_staff.html', {
        'claims': claims,
        'maskapai_list': maskapai_as_list(),
        'status_filter': status_filter,
        'maskapai_filter': maskapai_filter,
    })

def claim_approve(request, claim_id):
    if not require_staff(request):
        return redirect('main:login')
    return redirect('miles:claim_staff_list')


def claim_reject(request, claim_id):
    if not require_staff(request):
        return redirect('main:login')
    return redirect('miles:claim_staff_list')

def transfer_list(request):
    if not require_member(request):
        return redirect('main:login')

    transfers = list(DUMMY_TRANSFERS.values())

    return render(request, 'transfer.html', {
        'transfers': transfers,
        'award_miles': 185000,  
    })

def transfer_create(request):
    if not require_member(request):
        return redirect('main:login')

    if request.method == 'POST':
        errors = []
        email_penerima = request.POST.get('email_penerima', '').strip()
        jumlah_str     = request.POST.get('jumlah', '0').strip()

        try:
            jumlah = int(jumlah_str)
        except ValueError:
            jumlah = 0

        if not email_penerima:
            errors.append('Email penerima wajib diisi.')
        if jumlah <= 0:
            errors.append('Jumlah miles harus lebih dari 0.')

        if errors:
            return render(request, 'transfer.html', {
                'transfers': list(DUMMY_TRANSFERS.values()),
                'award_miles': 185000,
                'errors': errors,
                'show_modal': True,
                'form': request.POST,
            })

        return redirect('miles:transfer_list')

    return redirect('miles:transfer_list')
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
