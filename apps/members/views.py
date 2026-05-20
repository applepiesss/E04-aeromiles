from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import connection, DatabaseError
import datetime

app_name = 'members'

# Tier benefits
TIER_BENEFITS = {
    'TIR-BLU': [
        {'icon': '🎫', 'text': 'Akumulasi miles dari setiap penerbangan'},
        {'icon': '📱', 'text': 'Akses aplikasi mobile AeroMiles'},
        {'icon': '📧', 'text': 'Notifikasi promosi dan penawaran khusus'},
    ],
    'TIR-SLV': [
        {'icon': '🎫', 'text': '+10% bonus miles setiap penerbangan'},
        {'icon': '🛫', 'text': 'Prioritas boarding dan check-in'},
        {'icon': '🏨', 'text': 'Diskon 10% hotel partner AeroMiles'},
        {'icon': '💳', 'text': 'Status elite di maskapai partner'},
    ],
    'TIR-GLD': [
        {'icon': '🎫', 'text': '+25% bonus miles setiap penerbangan'},
        {'icon': '🛫', 'text': 'Prioritas boarding dan seat selection'},
        {'icon': '🎁', 'text': 'Upgrade gratis ke business class'},
        {'icon': '🏨', 'text': 'Diskon 20% hotel dan restoran partner'},
        {'icon': '🎫', 'text': '2 free miles voucher per tahun'},
    ],
    'TIR-PLT': [
        {'icon': '🎫', 'text': '+50% bonus miles setiap penerbangan'},
        {'icon': '🛫', 'text': 'Priority boarding & premium lounge access'},
        {'icon': '🎁', 'text': 'Unlimited upgrade ke business class'},
        {'icon': '🏨', 'text': 'Diskon 30% hotel dan restoran partner'},
        {'icon': '🎫', 'text': '5 free miles voucher per tahun'},
        {'icon': '👥', 'text': 'Dedicated concierge service'},
    ],
}

BULAN_ID = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Ags', 'Sep', 'Okt', 'Nov', 'Des']


def _fmt_tanggal(iso_str):
    try:
        if isinstance(iso_str, datetime.date):
            d = iso_str
        else:
            d = datetime.date.fromisoformat(iso_str)
        return f"{d.day:02d} {BULAN_ID[d.month]} {d.year}"
    except Exception:
        return iso_str


def dictfetchall(cursor):
    """Convert database rows to list of dicts"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def dictfetchone(cursor):
    """Convert single database row to dict"""
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    return dict(zip(columns, row)) if row else None


def get_tier_info_from_db():
    """Fetch all tiers from database"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id_tier, nama, minimal_frekuensi_terbang, minimal_tier_miles
                FROM TIER
                ORDER BY minimal_tier_miles ASC
            """)
            tiers = dictfetchall(cursor)
            
            # Add benefits from hardcoded dictionary
            for tier in tiers:
                tier['benefits'] = TIER_BENEFITS.get(tier['id_tier'], [])
                tier['id'] = tier['id_tier']  # Add 'id' alias for compatibility
            
            return tiers
    except Exception:
        return []


def get_tier_info_for_member(email):
    """Calculate tier information for a specific member including next tier and miles needed"""
    try:
        # Fetch member data
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT nomor_member, id_tier, award_miles, total_miles
                FROM MEMBER
                WHERE email = %s
            """, [email])
            member_data = dictfetchone(cursor)
        
        if not member_data:
            return None, None
        
        current_tier_id = member_data['id_tier']
        current_miles = member_data['total_miles']
        current_flights = member_data['award_miles']
        
        # Fetch member name
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT salutation, first_mid_name, last_name
                FROM PENGGUNA
                WHERE email = %s
            """, [email])
            user_data = dictfetchone(cursor)
        
        name = f"{user_data['salutation']} {user_data['first_mid_name']} {user_data['last_name']}" if user_data else "Member"
        
        # Get all tiers
        tiers = get_tier_info_from_db()
        
        # Add calculated fields
        enriched_tiers = []
        for i, tier in enumerate(tiers):
            tier_info = tier.copy()
            tier_info['is_current'] = (tier['id_tier'] == current_tier_id)
            
            # Calculate miles needed to reach next tier
            if i < len(tiers) - 1:
                next_tier = tiers[i + 1]
                miles_needed_for_next = next_tier['minimal_tier_miles'] - current_miles
                tier_info['miles_to_next'] = max(0, miles_needed_for_next)
                tier_info['next_tier_name'] = next_tier['nama']
                
                # Calculate progress percentage for current tier
                if tier_info['is_current']:
                    current_tier_min_miles = tier['minimal_tier_miles']
                    next_tier_min_miles = next_tier['minimal_tier_miles']
                    miles_in_range = next_tier_min_miles - current_tier_min_miles
                    miles_since_current = current_miles - current_tier_min_miles
                    progress_percentage = int((miles_since_current / miles_in_range) * 100) if miles_in_range > 0 else 0
                    tier_info['progress_percentage'] = min(progress_percentage, 100)
                else:
                    tier_info['progress_percentage'] = 0
            else:
                tier_info['miles_to_next'] = None
                tier_info['next_tier_name'] = None
                tier_info['progress_percentage'] = 0 if not tier_info['is_current'] else 100
            
            enriched_tiers.append(tier_info)
        
        member = {
            'name': name,
            'current_miles': current_miles,
            'current_flights': current_flights,
        }
        
        return enriched_tiers, member
    except Exception:
        return None, None


@require_http_methods(["GET"])
def tier_info(request):
    """Display tier information and current member tier"""
    email = request.session.get('email')
    
    if not email:
        context = {'tiers': [], 'member': None}
        return render(request, 'tier_info.html', context)
    
    tiers, member = get_tier_info_for_member(email)
    
    if tiers is None:
        # Fallback to showing all tiers without member-specific data
        tiers = get_tier_info_from_db()
        member = None
    
    context = {
        'tiers': tiers or [],
        'member': member or {},
    }
    
    return render(request, 'tier_info.html', context)


def kelola_member(request):
    if request.session.get('role') != 'staff':
        return redirect('main:dashboard')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                m.nomor_member, m.email, m.id_tier,
                m.award_miles, m.total_miles, m.tanggal_bergabung,
                p.salutation, p.first_mid_name, p.last_name,
                p.country_code, p.mobile_number,
                p.tanggal_lahir, p.kewarganegaraan,
                t.nama AS nama_tier
            FROM MEMBER m
            JOIN PENGGUNA p ON m.email = p.email
            JOIN TIER t ON m.id_tier = t.id_tier
            ORDER BY m.nomor_member
        """)
        rows = dictfetchall(cursor)

    members = []
    for r in rows:
        members.append({
            **r,
            'nama_lengkap': f"{r['salutation']} {r['first_mid_name']} {r['last_name']}",
            'tier': r['nama_tier'],
            'tanggal_bergabung': _fmt_tanggal(r['tanggal_bergabung']),
            'tanggal_lahir_iso': str(r['tanggal_lahir'])[:10] if r['tanggal_lahir'] else '',
        })

    return render(request, 'kelola_member.html', {'members': members})


@require_http_methods(["POST"])
def tambah_member(request):
    if request.session.get('role') != 'staff':
        return redirect('main:dashboard')

    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '').strip()
    salutation = request.POST.get('salutation', '').strip()
    first_mid_name = request.POST.get('first_mid_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    country_code = request.POST.get('country_code', '').strip()
    mobile_number = request.POST.get('mobile_number', '').strip()
    tanggal_lahir = request.POST.get('tanggal_lahir', '').strip()
    kewarganegaraan = request.POST.get('kewarganegaraan', '').strip()

    try:
        with connection.cursor() as cursor:
            # INSERT PENGGUNA
            cursor.execute("""
                INSERT INTO PENGGUNA (email, password, salutation, first_mid_name, last_name, country_code, mobile_number, tanggal_lahir, kewarganegaraan)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, [email, password, salutation, first_mid_name, last_name, country_code, mobile_number, tanggal_lahir, kewarganegaraan])

            # INSERT MEMBER
            cursor.execute("""
                INSERT INTO MEMBER (email, tanggal_bergabung, id_tier)
                VALUES (%s, CURRENT_DATE, 'TIR-BLU')
            """, [email])

        messages.success(request, f'Member baru ({email}) berhasil didaftarkan.')

    except DatabaseError as e:
        err = str(e)
        if 'ERROR:' in err:
            pesan = err.split('ERROR:')[1].split('\n')[0].strip()
            messages.error(request, pesan)
        else:
            messages.error(request, 'Terjadi gangguan pada sistem. Silakan coba beberapa saat lagi.')
    except Exception:
        messages.error(request, 'Terjadi gangguan pada sistem. Silakan coba beberapa saat lagi.')

    return redirect('members:kelola_member')


@require_http_methods(["POST"])
def edit_member(request, nomor):
    if request.session.get('role') != 'staff':
        return redirect('main:dashboard')

    salutation = request.POST.get('salutation', '').strip()
    first_mid_name = request.POST.get('first_mid_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    country_code = request.POST.get('country_code', '').strip()
    mobile_number = request.POST.get('mobile_number', '').strip()
    tanggal_lahir = request.POST.get('tanggal_lahir', '').strip()
    kewarganegaraan = request.POST.get('kewarganegaraan', '').strip()
    id_tier = request.POST.get('id_tier', '').strip()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT email FROM MEMBER WHERE nomor_member = %s", [nomor]
            )
            row = cursor.fetchone()
            if not row:
                messages.error(request, 'Member tidak ditemukan.')
                return redirect('members:kelola_member')
            email = row[0]

            # UPDATE PENGGUNA
            cursor.execute("""
                UPDATE PENGGUNA
                SET salutation = %s, first_mid_name = %s, last_name = %s, country_code = %s, mobile_number = %s, tanggal_lahir = %s, kewarganegaraan = %s
                WHERE email = %s
            """, [salutation, first_mid_name, last_name, country_code, mobile_number, tanggal_lahir, kewarganegaraan, email])

            # UPDATE MEMBER tier
            cursor.execute(
                "UPDATE MEMBER SET id_tier = %s WHERE email = %s",
                [id_tier, email]
            )

        messages.success(request, f'Data member {nomor} berhasil diperbarui.')

    except DatabaseError as e:
        err = str(e)
        if 'ERROR:' in err:
            pesan = err.split('ERROR:')[1].split('\n')[0].strip()
            messages.error(request, pesan)
        else:
            messages.error(request, 'Terjadi gangguan pada sistem. Silakan coba beberapa saat lagi.')
    except Exception:
        messages.error(request, 'Terjadi gangguan pada sistem. Silakan coba beberapa saat lagi.')

    return redirect('members:kelola_member')


@require_http_methods(["POST"])
def hapus_member(request, nomor):
    if request.session.get('role') != 'staff':
        return redirect('main:dashboard')

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT email FROM MEMBER WHERE nomor_member = %s", [nomor]
            )
            row = cursor.fetchone()
            if not row:
                messages.error(request, 'Member tidak ditemukan.')
                return redirect('members:kelola_member')
            email = row[0]

            cursor.execute("DELETE FROM MEMBER WHERE email = %s", [email])

            cursor.execute("DELETE FROM PENGGUNA WHERE email = %s", [email])

        messages.success(request, f'Member {nomor} beserta seluruh data terkait berhasil dihapus.')

    except DatabaseError as e:
        err = str(e)
        if 'ERROR:' in err:
            pesan = err.split('ERROR:')[1].split('\n')[0].strip()
            messages.error(request, pesan)
        else:
            messages.error(request, 'Terjadi gangguan pada sistem. Silakan coba beberapa saat lagi.')
    except Exception:
        messages.error(request, 'Terjadi gangguan pada sistem. Silakan coba beberapa saat lagi.')

    return redirect('members:kelola_member')


def _build_identitas(raw_list):
    today = datetime.date.today()
    result = []
    for item in raw_list:
        habis_iso = item['tanggal_habis']
        habis_date = datetime.date.fromisoformat(habis_iso)
        never_expires = habis_date >= datetime.date(9999, 12, 31)

        if never_expires:
            status = 'Aktif'
            status_class = 'badge-aktif'
            tanggal_habis_display = 'Berlaku Seumur Hidup'
        elif habis_date >= today:
            status = 'Aktif'
            status_class = 'badge-aktif'
            tanggal_habis_display = _fmt_tanggal(habis_iso)
        else:
            status = 'Kedaluwarsa'
            status_class = 'badge-kedaluwarsa'
            tanggal_habis_display = _fmt_tanggal(habis_iso)

        result.append({
            **item,
            'tanggal_terbit_display': _fmt_tanggal(item['tanggal_terbit']),
            'tanggal_habis_display': tanggal_habis_display,
            'status': status,
            'status_class': status_class,
        })
    return result


def identitas(request):
    if request.session.get('role') != 'member':
        return redirect('main:dashboard')
    
    email = request.session.get('email', '')

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT nomor, jenis, negara_penerbit, tanggal_terbit, tanggal_habis
                FROM IDENTITAS
                WHERE email_member = %s
                ORDER BY tanggal_terbit DESC
            """, [email])
            rows = dictfetchall(cursor)
    except Exception:
        rows = []

    for r in rows:
        r['tanggal_terbit_iso'] = str(r['tanggal_terbit'])[:10] if r['tanggal_terbit'] else ''
        r['tanggal_habis_iso']  = str(r['tanggal_habis'])[:10] if r['tanggal_habis'] else ''
        r['tanggal_terbit'] = r['tanggal_terbit_iso']
        r['tanggal_habis']  = r['tanggal_habis_iso']

    return render(request, 'identitas.html', {'identitas_list': _build_identitas(rows)})


@require_http_methods(["POST"])
def tambah_identitas(request):
    if request.session.get('role') != 'member':
        return redirect('main:dashboard')

    email = request.session.get('email', '')
    nomor = request.POST.get('nomor', '').strip()
    jenis = request.POST.get('jenis', '').strip()
    negara_penerbit = request.POST.get('negara_penerbit', '').strip()
    tanggal_terbit = request.POST.get('tanggal_terbit', '').strip()
    tanggal_habis = request.POST.get('tanggal_habis', '').strip()

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO IDENTITAS
                (nomor, email_member, tanggal_habis, tanggal_terbit, negara_penerbit, jenis)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [nomor, email, tanggal_habis, tanggal_terbit, negara_penerbit, jenis])

        messages.success(request, f'Identitas {nomor} berhasil ditambahkan.')

    except DatabaseError as e:
        err = str(e)
        if 'duplicate key' in err.lower() or 'unique' in err.lower():
            messages.error(request, f'Nomor dokumen "{nomor}" sudah terdaftar di sistem.')
        elif 'check constraint' in err.lower() or 'identitas_jenis_check' in err.lower():
            messages.error(request, 'Jenis dokumen tidak valid (gunakan Paspor, KTP, atau SIM).')
        elif 'ERROR:' in err:
            pesan = err.split('ERROR:')[1].split('\n')[0].strip()
            messages.error(request, pesan)
        else:
            messages.error(request, 'Terjadi gangguan pada sistem. Silakan coba beberapa saat lagi.')
    except Exception:
        messages.error(request, 'Terjadi gangguan pada sistem. Silakan coba beberapa saat lagi.')

    return redirect('members:identitas')


@require_http_methods(["POST"])
def edit_identitas(request, nomor):
    if request.session.get('role') != 'member':
        return redirect('main:dashboard')

    email = request.session.get('email', '')
    tanggal_terbit = request.POST.get('tanggal_terbit', '').strip()
    tanggal_habis  = request.POST.get('tanggal_habis', '').strip()

    try:
        with connection.cursor() as cursor:
            # Pastikan identitas milik member yang sedang login
            cursor.execute("""
                SELECT 1 FROM IDENTITAS
                WHERE nomor = %s AND email_member = %s
            """, [nomor, email])
            if not cursor.fetchone():
                messages.error(request, 'Identitas tidak ditemukan atau bukan milik Anda.')
                return redirect('members:identitas')

            cursor.execute("""
                UPDATE IDENTITAS
                SET tanggal_terbit = %s, tanggal_habis = %s
                WHERE nomor = %s AND email_member = %s
            """, [tanggal_terbit, tanggal_habis, nomor, email])

        messages.success(request, f'Identitas {nomor} berhasil diperbarui.')

    except DatabaseError as e:
        err = str(e)
        if 'ERROR:' in err:
            pesan = err.split('ERROR:')[1].split('\n')[0].strip()
            messages.error(request, pesan)
        else:
            messages.error(request, 'Terjadi gangguan pada sistem. Silakan coba beberapa saat lagi.')
    except Exception:
        messages.error(request, 'Terjadi gangguan pada sistem. Silakan coba beberapa saat lagi.')

    return redirect('members:identitas')


@require_http_methods(["POST"])
def hapus_identitas(request, nomor):
    if request.session.get('role') != 'member':
        return redirect('main:dashboard')

    email = request.session.get('email', '')

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM IDENTITAS
                WHERE nomor = %s AND email_member = %s
            """, [nomor, email])

            if cursor.rowcount == 0:
                messages.error(request, 'Identitas tidak ditemukan atau bukan milik Anda.')
            else:
                messages.success(request, f'Identitas {nomor} berhasil dihapus.')

    except DatabaseError as e:
        err = str(e)
        if 'ERROR:' in err:
            pesan = err.split('ERROR:')[1].split('\n')[0].strip()
            messages.error(request, pesan)
        else:
            messages.error(request, 'Terjadi gangguan pada sistem. Silakan coba beberapa saat lagi.')
    except Exception:
        messages.error(request, 'Terjadi gangguan pada sistem. Silakan coba beberapa saat lagi.')

    return redirect('members:identitas')
