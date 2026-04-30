from django.shortcuts import redirect, render

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