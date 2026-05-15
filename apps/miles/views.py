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
from django.db import connection, DatabaseError


def dictfetchall(cursor):
    """Convert database rows to list of dicts"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def dictfetchone(cursor):
    """Convert single database row to dict"""
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    return dict(zip(columns, row)) if row else None


@require_http_methods(["GET"])
def buy_miles_package(request):
    """Display award miles packages for purchase"""
    email = request.session.get('email')
    
    if not email or request.session.get('role') != 'member':
        return redirect('main:login')
    
    try:
        # Fetch member's current award miles
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT award_miles, total_miles
                FROM MEMBER
                WHERE email = %s
            """, [email])
            member_data = dictfetchone(cursor)
        
        current_award_miles = member_data['award_miles'] if member_data else 0
        
        # Fetch all available packages
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, harga_paket, jumlah_award_miles
                FROM AWARD_MILES_PACKAGE
                ORDER BY jumlah_award_miles ASC
            """)
            packages = dictfetchall(cursor)
        
        # Fetch transaction history for this member
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    m.id_award_miles_package,
                    m.email_member,
                    m.timestamp,
                    p.harga_paket,
                    p.jumlah_award_miles
                FROM MEMBER_AWARD_MILES_PACKAGE m
                JOIN AWARD_MILES_PACKAGE p ON m.id_award_miles_package = p.id
                WHERE m.email_member = %s
                ORDER BY m.timestamp DESC
            """, [email])
            transaction_history = dictfetchall(cursor)
        
        # Format timestamps for display
        for transaction in transaction_history:
            if transaction['timestamp']:
                transaction['waktu'] = transaction['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        
        # Fetch member name for display
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT salutation, first_mid_name, last_name
                FROM PENGGUNA
                WHERE email = %s
            """, [email])
            user_data = dictfetchone(cursor)
        
        member_name = f"{user_data['salutation']} {user_data['first_mid_name']} {user_data['last_name']}" if user_data else ""
        
        context = {
            'current_award_miles': current_award_miles,
            'packages': packages,
            'transaction_history': transaction_history,
            'member_name': member_name,
            'member_email': email,
        }
        
        return render(request, 'buy_miles_package.html', context)
    
    except DatabaseError as e:
        messages.error(request, f'Terjadi kesalahan database: {str(e)}')
        return render(request, 'buy_miles_package.html', {
            'current_award_miles': 0,
            'packages': [],
            'transaction_history': [],
        })


@require_http_methods(["POST"])
def process_buy_package(request):
    """Process award miles package purchase"""
    email = request.session.get('email')
    
    if not email or request.session.get('role') != 'member':
        return redirect('main:login')
    
    paket_id = request.POST.get('paket_id', '').strip()
    
    if not paket_id:
        messages.error(request, 'Paket tidak valid.')
        return redirect('miles:buy_miles_package')
    
    try:
        # Call function to handle validation, insert, and return pesan
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT fn_buy_award_miles_package(%s, %s) as pesan
            """, [paket_id, email])
            result = dictfetchone(cursor)
            pesan = result['pesan'] if result else 'Terjadi kesalahan.'
        
        # Check if error atau success berdasarkan prefix pesan
        if pesan.startswith('ERROR:'):
            messages.error(request, pesan.replace('ERROR: ', ''))
        else:
            messages.success(request, pesan.replace('SUKSES: ', ''))
        
    except DatabaseError as e:
        messages.error(request, f'Terjadi kesalahan database: {str(e)}')
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
    
    return redirect('miles:buy_miles_package')
