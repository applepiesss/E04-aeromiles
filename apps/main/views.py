import re
from django.shortcuts import redirect, render
from django.contrib import messages

DUMMY_PENGGUNA = {
    'judy.hopps@yahoo.com': {
        'nama': 'Ms. Judy Hopps',
        'password': 'password123',
        'salutation': 'Ms.',
        'first_mid_name': 'Judy',
        'last_name': 'Hopps',
        'country_code': '+1',
        'mobile_number': '5554941103',
        'tanggal_lahir': '03 November 1994',
        'kewarganegaraan': 'American',
        'role': 'member',
    },
    'nick.wilde@yahoo.com': {
        'nama': 'Mr. Nick Wilde',
        'password': 'password456',
        'salutation': 'Mr.',
        'first_mid_name': 'Nick',
        'last_name': 'Wilde',
        'country_code': '+1',
        'mobile_number': '5558560622',
        'tanggal_lahir': '22 Juni 1985',
        'kewarganegaraan': 'American',
        'role': 'staff',
    },
}

DUMMY_MEMBER = {
    'judy.hopps@yahoo.com': {
        'nomor_member': 'M0008',
        'tanggal_bergabung': '19 Agustus 2023',
        'tier': 'Blue',
        'id_tier': 'TIR-BLU',
        'award_miles': 2600,
        'total_miles': 5500,
    },
}

DUMMY_STAF = {
    'nick.wilde@yahoo.com': {
        'id_staf': 'S0011',
        'maskapai': 'Citilink',
        'kode_maskapai': 'QG',
        'klaim_menunggu': 3,
        'klaim_disetujui': 5,
        'klaim_ditolak': 1,
    },
}

DUMMY_TRANSACTIONS = {
    'judy.hopps@yahoo.com': [
        {
            'tanggal': '12 Mei 2025',
            'jenis': 'Transfer Keluar',
            'keterangan': 'Ke Mr. Nick Wilde – Patungan beli Jumbo-pop untuk Pawpsicles',
            'miles': -75,
        },
        {
            'tanggal': '15 Mar 2025',
            'jenis': 'Redeem',
            'keterangan': 'Voucher Kopi Rp50.000 (RWD-001)',
            'miles': -500,
        },
    ],
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

def show_main(request):
    return render(request, "main.html")


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
            request.session['nama'] = user['nama']
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

    pengguna = DUMMY_PENGGUNA.get(email, {})

    if role == 'member':
        member = DUMMY_MEMBER.get(email, {})
        transactions = DUMMY_TRANSACTIONS.get(email, [])
        context = {
            'role': 'member',
            'pengguna': pengguna,
            'member': member,
            'transactions': transactions,
        }
    else:
        staf = DUMMY_STAF.get(email, {})
        context = {
            'role': 'staff',
            'pengguna': pengguna,
            'staf': staf,
        }

    return render(request, 'dashboard.html', context)