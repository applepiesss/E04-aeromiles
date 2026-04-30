from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from datetime import datetime, timedelta


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

def dashboard(request):
    email = request.session.get('email')
    role = request.session.get('role')
    if not email or not role:
        return redirect('main:login')

    p = DUMMY_PENGGUNA.get(email, {})
    base = {
        'role': role,
        'nama_lengkap': _nama(p),
        'email': email,
        'telepon': f"{p['country_code']} {p['mobile_number']}",
        'tanggal_lahir': _fmt_date(p['tanggal_lahir']),
        'kewarganegaraan': p['kewarganegaraan'],
    }

    if role == 'member':
        m = DUMMY_MEMBER.get(email, {})
        tier = DUMMY_TIER.get(m.get('id_tier', ''), {})

        transactions = []

        for r in DUMMY_REDEEM:
            if r['email_member'] == email:
                h = DUMMY_HADIAH.get(r['kode_hadiah'], {})
                transactions.append({
                    'timestamp': r['timestamp'],
                    'jenis': 'Redeem',
                    'keterangan': f"{h.get('nama', r['kode_hadiah'])} ({r['kode_hadiah']})",
                    'jumlah': -h.get('miles', 0),
                })

        for t in DUMMY_TRANSFER:
            if t['email_member_1'] == email:
                penerima = DUMMY_PENGGUNA.get(t['email_member_2'], {})
                transactions.append({
                    'timestamp': t['timestamp'],
                    'jenis': 'Transfer',
                    'keterangan': f"Ke {_nama(penerima)} – {t['catatan']}",
                    'jumlah': -t['jumlah'],
                })
            elif t['email_member_2'] == email:
                pengirim = DUMMY_PENGGUNA.get(t['email_member_1'], {})
                transactions.append({
                    'timestamp': t['timestamp'],
                    'jenis': 'Transfer',
                    'keterangan': f"Dari {_nama(pengirim)} – {t['catatan']}",
                    'jumlah': +t['jumlah'],
                })

        transactions.sort(key=lambda x: x['timestamp'], reverse=True)
        for tx in transactions:
            tx['tanggal'] = _fmt_date(tx['timestamp'])

        context = {
            **base,
            'nomor_member': m.get('nomor_member', '-'),
            'tier': tier.get('nama', '-'),
            'id_tier': m.get('id_tier', ''),
            'award_miles': m.get('award_miles', 0),
            'total_miles': m.get('total_miles', 0),
            'tanggal_bergabung': _fmt_date(m['tanggal_bergabung']),
            'transactions': transactions,
        }

    else:  # staff
        s = DUMMY_STAF.get(email, {})
        maskapai = DUMMY_MASKAPAI.get(s.get('kode_maskapai', ''), {})

        klaim_menunggu = sum(1 for k in DUMMY_CLAIM_MISSING_MILES if k['status_penerimaan'] == 'Menunggu')
        klaim_disetujui = sum(1 for k in DUMMY_CLAIM_MISSING_MILES if k['email_staf'] == email and k['status_penerimaan'] == 'Disetujui')
        klaim_ditolak = sum(1 for k in DUMMY_CLAIM_MISSING_MILES if k['email_staf'] == email and k['status_penerimaan'] == 'Ditolak')

        context = {
            **base,
            'id_staf': s.get('id_staf', '-'),
            'maskapai': maskapai.get('nama_maskapai', '-'),
            'kode_maskapai': s.get('kode_maskapai', '-'),
            'klaim_menunggu': klaim_menunggu,
            'klaim_disetujui': klaim_disetujui,
            'klaim_ditolak': klaim_ditolak,
        }

    return render(request, 'dashboard.html', context)
