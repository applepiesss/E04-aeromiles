from django.shortcuts import render, redirect
from django.db import connection
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from datetime import datetime, timedelta

_BULAN = ['','Jan','Feb','Mar','Apr','Mei','Jun','Jul','Ags','Sep','Okt','Nov','Des']

def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def dictfetchone(cursor):
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))

def _fmt_date(d):
    # Handles datetime.date, datetime.datetime, or ISO string from DB
    if isinstance(d, str):
        d = datetime.date.fromisoformat(d[:10])
    elif isinstance(d, datetime.datetime):
        d = d.date()
    return f"{d.day:02d} {_BULAN[d.month]} {d.year}"

def show_main(request):
    return render(request, "main.html")


# Hardcoded sample data for mockup
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

STAFF_DATA = {
    'type': 'staff',
    'salutation': 'Ms.',
    'first_mid_name': 'Jane Marie',
    'last_name': 'Smith',
    'email': 'jane.smith@aeromiles.com',
    'country_code': '+62',
    'phone_number': '08123456789',
    'nationality': 'Indonesian',
    'date_of_birth': '1992-03-20',
    'staff_id': 'STF0000567',
    'airline_code': 'GA',
}

SALUTATION_CHOICES = ['Mr.', 'Mrs.', 'Ms.', 'Dr.']


@require_http_methods(["GET", "POST"])
def profile_settings(request):
    """Display and handle profile settings mockup"""
    user_type = request.GET.get('type', 'staff')  # 'member' or 'staff'
    
    if user_type == 'staff':
        profile = STAFF_DATA.copy()
        is_staff = True
    else:
        profile = MEMBER_DATA.copy()
        is_staff = False

    if request.method == 'POST':
        # Update hardcoded data (mockup)
        for key in request.POST:
            if key in profile:
                profile[key] = request.POST[key]
        
        messages.success(request, 'Profil Anda berhasil diperbarui.')
        return redirect('main:profile_settings' + ('?type=staff' if is_staff else ''))

    context = {
        'profile': profile,
        'is_staff': is_staff,
        'user_type': user_type,
        'salutation_choices': SALUTATION_CHOICES,
    }

    return render(request, 'profile_settings.html', context)


@require_http_methods(["POST"])
def change_password(request):
    """Handle password change mockup"""
    user_type = request.GET.get('type', 'member')
    
    # Validate password change (mockup - simple validation)
    old_password = request.POST.get('old_password', '')
    new_password = request.POST.get('new_password', '')
    confirm_password = request.POST.get('confirm_password', '')
    
    errors = {}
    
    # Simple mockup validation
    if not old_password:
        errors['old_password'] = 'Password lama harus diisi'
    
    if len(new_password) < 8:
        errors['new_password'] = 'Password baru harus minimal 8 karakter'
    
    if new_password != confirm_password:
        errors['confirm_password'] = 'Password baru dan konfirmasi tidak cocok'
    
    if errors:
        messages.error(request, 'Ada kesalahan dalam form')
        context = {
            'user_type': user_type,
            'password_errors': errors,
        }
        return render(request, 'profile_settings.html', context)
    
    messages.success(request, 'Password Anda berhasil diubah.')
    return redirect('main:profile_settings' + ('?type=staff' if user_type == 'staff' else ''))
import datetime
from django.shortcuts import redirect, render
from django.contrib import messages

_BULAN = ['','Jan','Feb','Mar','Apr','Mei','Jun','Jul','Ags','Sep','Okt','Nov','Des']

def _fmt_date(iso):
    d = datetime.date.fromisoformat(iso[:10])
    return f"{d.day:02d} {_BULAN[d.month]} {d.year}"

def _nama(p):
    return f"{p['salutation']} {p['first_mid_name']} {p['last_name']}"

DUMMY_PENGGUNA = {
    'judy.hopps@yahoo.com': {
        'password': 'password123',
        'salutation': 'Ms.',
        'first_mid_name': 'Judy',
        'last_name': 'Hopps',
        'country_code': '+1',
        'mobile_number': '5554941103',
        'tanggal_lahir': '1994-11-03',
        'kewarganegaraan': 'American',
        'role': 'member',
    },
    'nick.wilde@yahoo.com': {
        'password': 'password456',
        'salutation': 'Mr.',
        'first_mid_name': 'Nick',
        'last_name': 'Wilde',
        'country_code': '+1',
        'mobile_number': '5558560622',
        'tanggal_lahir': '1985-06-22',
        'kewarganegaraan': 'American',
        'role': 'staff',
    },
}

DUMMY_TIER = {
    'TIR-BLU': {'nama': 'Blue'},
    'TIR-SLV': {'nama': 'Silver'},
    'TIR-GLD': {'nama': 'Gold'},
    'TIR-PLT': {'nama': 'Platinum'},
}

DUMMY_MASKAPAI = {
    'GA': {'nama_maskapai': 'Garuda Indonesia'},
    'QG': {'nama_maskapai': 'Citilink'},
    'JT': {'nama_maskapai': 'Lion Air'},
    'SJ': {'nama_maskapai': 'Sriwijaya Air'},
    'ID': {'nama_maskapai': 'Batik Air'},
}

DUMMY_MEMBER = {
    'judy.hopps@yahoo.com': {
        'nomor_member': 'M0008',
        'tanggal_bergabung': '2023-08-19',
        'id_tier': 'TIR-BLU',
        'award_miles': 2600,
        'total_miles': 5500,
    },
}

DUMMY_STAF = {
    'nick.wilde@yahoo.com': {
        'id_staf': 'S0011',
        'kode_maskapai': 'QG',
    },
}

DUMMY_HADIAH = {
    'RWD-001': {'nama': 'Voucher Kopi Rp50.000', 'miles': 500},
    'RWD-002': {'nama': 'Tiket Nonton Bioskop Premiere', 'miles': 1200},
    'RWD-003': {'nama': 'Merchandise Kaos Eksklusif', 'miles': 2500},
    'RWD-004': {'nama': 'Diskon 20% Belanja Supermarket', 'miles': 800},
    'RWD-005': {'nama': 'Voucher Menginap Hotel Bintang 4', 'miles': 15000},
    'RWD-006': {'nama': 'E-Money Saldo Rp100.000', 'miles': 1000},
    'RWD-007': {'nama': 'Paket Liburan Bali 3H2M', 'miles': 50000},
    'RWD-008': {'nama': 'Voucher Makan Malam Romantis', 'miles': 3500},
    'RWD-009': {'nama': 'Gratis Bagasi Pesawat 10kg', 'miles': 2000},
    'RWD-010': {'nama': 'Akses Airport Premium Lounge', 'miles': 3000},
    'RWD-011': {'nama': 'Diskon Sewa Mobil 30%', 'miles': 1500},
    'RWD-012': {'nama': 'Voucher Spa & Pijat 90 Menit', 'miles': 2200},
}

DUMMY_MASKAPAI = {
    'GA': {
        'nama_maskapai': 'Garuda Indonesia',
        'id_penyedia': 1
    },
    'QG': {
        'nama_maskapai': 'Citilink',
        'id_penyedia': 2
    },
    'JT': {
        'nama_maskapai': 'Lion Air',
        'id_penyedia': 3
    },
    'SJ': {
        'nama_maskapai': 'Sriwijaya Air',
        'id_penyedia': 4
    },
    'ID': {
        'nama_maskapai': 'Batik Air',
        'id_penyedia': 5
    }
}
DUMMY_REDEEM = [
    {
        'email_member': 'judy.hopps@yahoo.com',
        'kode_hadiah': 'RWD-001',
        'timestamp': '2025-03-15 08:30:00',
    },
    {
        'email_member': 'judy.hopps@yahoo.com',
        'kode_hadiah': 'RWD-010',
        'timestamp': '2025-02-10 10:15:00',
    },
    {
        'email_member': 'judy.hopps@yahoo.com',
        'kode_hadiah': 'RWD-004',
        'timestamp': '2025-01-20 16:45:00',
    },
]

DUMMY_TRANSFER = [
    {
        'email_member_1': 'judy.hopps@yahoo.com',
        'email_member_2': 'nick.wilde@yahoo.com',
        'timestamp': '2025-05-12 13:20:00',
        'jumlah': 75,
        'catatan': 'Patungan beli Jumbo-pop untuk Pawpsicles',
    },
    {
        'email_member_1': 'nick.wilde@yahoo.com', 
        'email_member_2': 'judy.hopps@yahoo.com',
        'timestamp': '2025-04-05 09:00:00',
        'jumlah': 250,
        'catatan': 'Refund dana operasional taksi',
    },
]

DUMMY_CLAIM_MISSING_MILES = [
    {
        'email_member': 'blueberry.muffin@gmail.com', 'email_staf': None,
        'maskapai': 'QG', 'bandara_asal': 'SUB', 'bandara_tujuan': 'CGK',
        'tanggal_penerbangan': '2024-01-10', 'flight_number': 'QG712',
        'nomor_tiket': '1260000002', 'kelas_kabin': 'Economy',
        'pnr': 'QWERTY', 'status_penerimaan': 'Menunggu',
        'waktu_penerbangan': '2024-01-10 14:30:00',
    },
    {
        'email_member': 'steve.rogers@gmail.com', 'email_staf': None,
        'maskapai': 'GA', 'bandara_asal': 'LHR', 'bandara_tujuan': 'CDG',
        'tanggal_penerbangan': '2024-06-01', 'flight_number': 'GA910',
        'nomor_tiket': '1260000007', 'kelas_kabin': 'Business',
        'pnr': 'ASDFGH', 'status_penerimaan': 'Menunggu',
        'waktu_penerbangan': '2024-06-01 11:20:00',
    },
    {
        'email_member': 'peter.parker@gmail.com', 'email_staf': None,
        'maskapai': 'GA', 'bandara_asal': 'JFK', 'bandara_tujuan': 'SYD',
        'tanggal_penerbangan': '2024-08-15', 'flight_number': 'GA101',
        'nomor_tiket': '1260000012', 'kelas_kabin': 'Economy',
        'pnr': 'RDXESZ', 'status_penerimaan': 'Menunggu',
        'waktu_penerbangan': '2024-08-15 06:45:00',
    },
    {
        'email_member': 'judy.hopps@yahoo.com', 'email_staf': 'nick.wilde@yahoo.com',
        'maskapai': 'QG', 'bandara_asal': 'CGK', 'bandara_tujuan': 'DPS',
        'tanggal_penerbangan': '2023-10-05', 'flight_number': 'QG401',
        'nomor_tiket': '1260000021', 'kelas_kabin': 'Economy',
        'pnr': 'HOPPS1', 'status_penerimaan': 'Disetujui',
        'waktu_penerbangan': '2023-10-05 07:00:00',
    },
    {
        'email_member': 'fru.fru@yahoo.com', 'email_staf': 'nick.wilde@yahoo.com',
        'maskapai': 'QG', 'bandara_asal': 'DPS', 'bandara_tujuan': 'CGK',
        'tanggal_penerbangan': '2023-11-20', 'flight_number': 'QG512',
        'nomor_tiket': '1260000022', 'kelas_kabin': 'Economy',
        'pnr': 'FRUFRU', 'status_penerimaan': 'Disetujui',
        'waktu_penerbangan': '2023-11-20 09:00:00',
    },
    {
        'email_member': 'pawbert.linxley@yahoo.com', 'email_staf': 'nick.wilde@yahoo.com',
        'maskapai': 'QG', 'bandara_asal': 'CGK', 'bandara_tujuan': 'SUB',
        'tanggal_penerbangan': '2023-12-12', 'flight_number': 'QG601',
        'nomor_tiket': '1260000023', 'kelas_kabin': 'Economy',
        'pnr': 'PAWBRT', 'status_penerimaan': 'Disetujui',
        'waktu_penerbangan': '2023-12-12 11:00:00',
    },
    {
        'email_member': 'choso.kamo@gmail.com', 'email_staf': 'nick.wilde@yahoo.com',
        'maskapai': 'QG', 'bandara_asal': 'SUB', 'bandara_tujuan': 'DPS',
        'tanggal_penerbangan': '2024-01-08', 'flight_number': 'QG711',
        'nomor_tiket': '1260000024', 'kelas_kabin': 'Economy',
        'pnr': 'CHSKMO', 'status_penerimaan': 'Disetujui',
        'waktu_penerbangan': '2024-01-08 08:00:00',
    },
    {
        'email_member': 'hiromi.hiruguma@gmail.com', 'email_staf': 'nick.wilde@yahoo.com',
        'maskapai': 'QG', 'bandara_asal': 'CGK', 'bandara_tujuan': 'KNO',
        'tanggal_penerbangan': '2024-02-14', 'flight_number': 'QG321',
        'nomor_tiket': '1260000025', 'kelas_kabin': 'Economy',
        'pnr': 'HIROMI', 'status_penerimaan': 'Disetujui',
        'waktu_penerbangan': '2024-02-14 10:00:00',
    },
    {
        'email_member': 'orange.blossom@gmail.com', 'email_staf': 'nick.wilde@yahoo.com',
        'maskapai': 'QG', 'bandara_asal': 'DPS', 'bandara_tujuan': 'SUB',
        'tanggal_penerbangan': '2023-09-15', 'flight_number': 'QG220',
        'nomor_tiket': '1260000026', 'kelas_kabin': 'Economy',
        'pnr': 'WILDE1', 'status_penerimaan': 'Ditolak',
        'waktu_penerbangan': '2023-09-15 14:00:00',
    },
]

def show_main(request):
    return render(request, "login.html")

def login_view(request):
    if request.session.get('email'):
        return redirect('main:dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        error = None

        user = DUMMY_PENGGUNA.get(email)
        if not user or user['password'] != password:
            error = 'Email atau password salah.'
        else:
            request.session['email'] = email
            request.session['role'] = user['role']
            request.session['nama'] = _nama(user)
            return redirect('main:dashboard')

        return render(request, 'login.html', {'error': error, 'email': email})

    return render(request, 'login.html')

def logout_view(request):
    request.session.flush()
    return redirect('main:login')

def register_view(request):
    if request.session.get('email'):
        return redirect('main:dashboard')

    maskapai_items = DUMMY_MASKAPAI.items()

    if request.method == 'POST':
        role = request.POST.get('role', 'member')
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        salutation = request.POST.get('salutation', '').strip()
        first_mid_name = request.POST.get('first_mid_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        country_code = request.POST.get('country_code', '').strip()
        mobile_number = request.POST.get('mobile_number', '').strip()
        tanggal_lahir = request.POST.get('tanggal_lahir', '').strip()
        kewarganegaraan = request.POST.get('kewarganegaraan', '').strip()
        kode_maskapai = request.POST.get('kode_maskapai', '').strip()

        errors = []

        required = [email, password, confirm_password, salutation,
                    first_mid_name, last_name, country_code,
                    mobile_number, tanggal_lahir, kewarganegaraan]
        
        if any(not f for f in required):
            errors.append('Semua field wajib diisi.')

        if password != confirm_password:
            errors.append('Password dan konfirmasi password tidak sama.')

        if role == 'staff' and not kode_maskapai:
            errors.append('Kode maskapai wajib dipilih untuk Staf.')
        
        if role == 'staff' and kode_maskapai and kode_maskapai not in DUMMY_MASKAPAI:
            errors.append('Maskapai tidak valid.')

        if salutation not in ('Mr.', 'Mrs.', 'Ms.', 'Dr.'):
            errors.append('Salutation tidak valid.')

        if country_code and not re.match(r'^\+\d+$', country_code):
            errors.append('Kode negara harus diawali "+" diikuti angka (contoh: +62).')

        if mobile_number and not mobile_number.isdigit():
            errors.append('Nomor HP hanya boleh berisi angka.')

        if mobile_number and not (9 <= len(mobile_number) <= 13):
            errors.append('Nomor HP harus berjumlah 9 hingga 13 digit.')

        if not errors:
            messages.success(request, 'Registrasi berhasil! Silakan login.')
            return redirect('main:login')

        return render(request, 'register.html', {
            'errors': errors,
            'maskapai_list': maskapai_items, 
            'role': role,
            'form': request.POST,
        })

    return render(request, 'register.html', {
        'maskapai_list': maskapai_items, 
        'role': 'member',
        'form': {},
    })

def dashboard(request):
    email = request.session.get('email')
    role = request.session.get('role')
    if not email or not role:
        return redirect('main:login')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT salutation, first_mid_name, last_name, country_code, mobile_number, tanggal_lahir, kewarganegaraan
            FROM PENGGUNA
            WHERE email = %s
        """, [email])
        p = dictfetchone(cursor)

    if not p:
        request.session.flush()
        return redirect('main:login')

    base = {
        'role': role,
        'nama_lengkap': f"{p['salutation']} {p['first_mid_name']} {p['last_name']}",
        'email': email,
        'telepon': f"{p['country_code']} {p['mobile_number']}",
        'tanggal_lahir': _fmt_date(p['tanggal_lahir']),
        'kewarganegaraan': p['kewarganegaraan'],
    }

    if role == 'member':
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT m.nomor_member, m.tanggal_bergabung, m.id_tier, m.award_miles, m.total_miles, t.nama AS nama_tier
                FROM MEMBER m
                JOIN TIER t ON m.id_tier = t.id_tier
                WHERE m.email = %s
            """, [email])
            m = dictfetchone(cursor)

        if not m:
            return redirect('main:login')

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT timestamp, jenis, keterangan, jumlah
                FROM (
                    SELECT r.timestamp,
                           'Redeem' AS jenis,
                           h.nama || ' (' || r.kode_hadiah || ')' AS keterangan,
                           -h.miles AS jumlah
                    FROM REDEEM r
                    JOIN HADIAH h ON r.kode_hadiah = h.kode_hadiah
                    WHERE r.email_member = %s

                    UNION ALL

                    SELECT t.timestamp,
                           'Transfer' AS jenis,
                           'Ke ' || p.salutation || ' ' || p.first_mid_name || ' ' || p.last_name
                               || CASE WHEN t.catatan IS NOT NULL THEN ' – ' || t.catatan ELSE '' END,
                           -t.jumlah
                    FROM TRANSFER t
                    JOIN PENGGUNA p ON t.email_member_2 = p.email
                    WHERE t.email_member_1 = %s

                    UNION ALL

                    SELECT t.timestamp,
                           'Transfer' AS jenis,
                           'Dari ' || p.salutation || ' ' || p.first_mid_name || ' ' || p.last_name
                               || CASE WHEN t.catatan IS NOT NULL THEN ' – ' || t.catatan ELSE '' END,
                           t.jumlah
                    FROM TRANSFER t
                    JOIN PENGGUNA p ON t.email_member_1 = p.email
                    WHERE t.email_member_2 = %s
                ) tx
                ORDER BY timestamp DESC
                LIMIT 5
            """, [email, email, email])
            transactions = dictfetchall(cursor)

        for tx in transactions:
            tx['tanggal'] = _fmt_date(tx['timestamp'])

        context = {
            **base,
            'nomor_member': m['nomor_member'],
            'tier': m['nama_tier'],
            'id_tier': m['id_tier'],
            'award_miles': m['award_miles'],
            'total_miles': m['total_miles'],
            'tanggal_bergabung': _fmt_date(m['tanggal_bergabung']),
            'transactions': transactions,
        }

    else:  # staff
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT s.id_staf, s.kode_maskapai, mk.nama_maskapai
                FROM STAF s
                JOIN MASKAPAI mk ON s.kode_maskapai = mk.kode_maskapai
                WHERE s.email = %s
            """, [email])
            s = dictfetchone(cursor)

        if not s:
            return redirect('main:login')

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM CLAIM_MISSING_MILES
                WHERE status_penerimaan = 'Menunggu'
            """)
            klaim_menunggu = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM CLAIM_MISSING_MILES
                WHERE email_staf = %s AND status_penerimaan = 'Disetujui'
            """, [email])
            klaim_disetujui = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM CLAIM_MISSING_MILES
                WHERE email_staf = %s AND status_penerimaan = 'Ditolak'
            """, [email])
            klaim_ditolak = cursor.fetchone()[0]

        context = {
            **base,
            'id_staf': s['id_staf'],
            'maskapai': s['nama_maskapai'],
            'kode_maskapai': s['kode_maskapai'],
            'klaim_menunggu': klaim_menunggu,
            'klaim_disetujui': klaim_disetujui,
            'klaim_ditolak': klaim_ditolak,
        }

    return render(request, 'dashboard.html', context)
