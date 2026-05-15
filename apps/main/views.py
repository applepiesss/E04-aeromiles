from django.db import DatabaseError
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import connection
from datetime import datetime, timedelta
import re

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
    if isinstance(d, str):
        d = datetime.strptime(d[:10], '%Y-%m-%d')
    return f"{d.day:02d} {_BULAN[d.month]} {d.year}"

def show_main(request):
    return render(request, "login.html")

def login_view(request):
    # Jika email sudah ada di session langsung redirect ke dashboard
    if request.session.get('email'):
        return redirect('main:dashboard')

    error = None

    # Ambil data dari form
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        try:
            with connection.cursor() as cursor:
                # Panggil fn login pengguna
                cursor.execute("SELECT fn_login_pengguna(%s, %s)", [email, password])
                hasil_login = cursor.fetchone()[0]

                # Jika sukses 
                if hasil_login.startswith('SUKSES'):
                    # Ambil email, salutation, first_mid_name, dan last_name
                    cursor.execute("""
                        SELECT email, salutation, first_mid_name, last_name 
                        FROM PENGGUNA 
                        WHERE lower(email) = lower(%s)
                    """, [email])
                    user = cursor.fetchone()

                    # Set sessionnya 
                    request.session['email'] = user[0]
                    request.session['nama'] = f"{user[1]} {user[2]} {user[3]}"
                    request.session['role'] = get_user_role(email)

                    return redirect('main:dashboard')

                # Jika gagal ambil message dari db
                else:
                    error = hasil_login

        except Exception as e:
            error = "Terjadi gangguan pada sistem. Silakan coba beberapa saat lagi."

    # Render dan tampilkan error message jika ada
    return render(request, 'login.html', {'error': error})

def logout_view(request):
    request.session.flush()
    return redirect('main:login')

def register_view(request):
    # Jika email sudah ada di session langsung redirect ke dashboard
    if request.session.get('email'):
        return redirect('main:dashboard')

    # Ambil data maskapai untuk dropdown
    maskapai_items = []
    errors = []

    try:
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT kode_maskapai, nama_maskapai 
                FROM MASKAPAI
            ''')
            maskapai_items = cursor.fetchall()
    except Exception:
        maskapai_items = []

    if request.method == 'POST':
        # Ambil data dari form
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
        role = request.POST.get('role', 'member') 
        kode_maskapai = request.POST.get('kode_maskapai', '').strip()
        
        # Define required fields
        required_fields = [
            email, password, confirm_password, salutation, first_mid_name, 
            last_name, country_code, mobile_number, tanggal_lahir, kewarganegaraan
        ]
        if any(not f for f in required_fields):
            errors.append('Semua field wajib diisi.')

        # Cek password match
        if password != confirm_password:
            errors.append('Password dan konfirmasi password tidak sama.')

        # Cek validasi maskapai untuk STAF
        if role == 'staff':
            if not kode_maskapai:
                errors.append('Kode maskapai wajib dipilih untuk akun Staf.')
            else:
                valid_kodes = [item[0] for item in maskapai_items]
                if kode_maskapai not in valid_kodes:
                    errors.append('Maskapai tidak valid.')

        # Cek validasi salutation
        if salutation not in ('Mr.', 'Mrs.', 'Ms.', 'Dr.'):
            errors.append('Salutation tidak valid (Gunakan Mr., Mrs., Ms., atau Dr.).')

        # Cek validasi format kode negara
        if country_code and not re.match(r'^\+\d+$', country_code):
            errors.append('Kode negara harus diawali "+" diikuti angka (contoh: +62).')
        
        # Cek validasi format nomor hp
        if mobile_number:
            if not mobile_number.isdigit():
                errors.append('Nomor HP hanya boleh berisi angka.')
            elif not (9 <= len(mobile_number) <= 13):
                errors.append('Nomor HP harus berjumlah 9 hingga 13 digit.')

        # INSERT ke db jika sudah tdk ada error
        if not errors:
            try:
                with connection.cursor() as cursor:
                    # INSERT ke PENGGUNA
                    cursor.execute('''
                        INSERT INTO PENGGUNA 
                        (email, password, salutation, first_mid_name, last_name, country_code, mobile_number, tanggal_lahir, kewarganegaraan)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', [email, password, salutation, first_mid_name, last_name, country_code, mobile_number, tanggal_lahir, kewarganegaraan])
                    
                    # INSERT ke MEMBER
                    if role == 'member':                        
                        cursor.execute('''
                            INSERT INTO MEMBER (email, tanggal_bergabung, id_tier)
                            VALUES (%s, CURRENT_DATE, 'TIR-BLU')
                        ''', [email])
                
                    # INSERT KE STAF
                    else:
                        cursor.execute('''
                            INSERT INTO STAF (email, kode_maskapai)
                            VALUES (%s, %s)
                        ''', [email, kode_maskapai])
                        
                messages.success(request, 'Registrasi berhasil! Silakan login.')
                return redirect('main:login')

            # Exception handling
            except DatabaseError as e:
                error_msg = str(e)

                if 'ERROR:' in error_msg:
                    parts = error_msg.split('ERROR:')
                    actual_error_message = parts[1].split('\n')[0].strip()

                    errors.append(actual_error_message)
                else:
                    errors.append("Terjadi gangguan pada sistem. Silakan coba beberapa saat lagi.")
            except Exception:
                errors.append("Terjadi gangguan pada sistem. Silakan coba beberapa saat lagi.")

    # Render halaman jika ada error atau request GET
    return render(request, 'register.html', {
        'errors': errors,
        'maskapai_list': maskapai_items, 
        'role': role if request.method == 'POST' else 'member',
        'form': request.POST if request.method == 'POST' else {},
    })

# Helper untuk cek role user
def get_user_role(email):
    with connection.cursor() as cursor:
        # Cek role member
        cursor.execute('''
            SELECT email 
            FROM MEMBER 
            WHERE lower(email) = lower(%s)
        ''', [email])
        if cursor.fetchone():
            return 'member'

        # Cek role staf
        cursor.execute('''
            SELECT email 
            FROM STAF 
            WHERE lower(email) = lower(%s)
        ''', [email])
        if cursor.fetchone():
            return 'staff'

    # Bukan keduanya
    return 'unknown'

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

@require_http_methods(["GET", "POST"])
def profile_settings(request):
    """Display and handle profile settings mockup"""
    user_type = request.GET.get('type', 'staff')  
    
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