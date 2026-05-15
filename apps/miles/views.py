from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from datetime import datetime
from django.db import connection

app_name = 'miles'

# C - Ajukan Claim Baru - Member
def claim_create(request):
    # Cek apakah sudah login
    if not request.session.get('email'):
        messages.error(request, "Anda harus login terlebih dahulu untuk mengajukan claim.")
        return redirect('main:login')

    # Cek role jika bukan member redirect ke dashboard
    if request.session.get('role') != "member":
        messages.error(request, "Anda tidak memiliki hak akses untuk mengajukan claim.")
        return redirect('main:dashboard')

    if request.method == 'POST':
        errors = []

        # Ambil data dari form
        maskapai          = request.POST.get('maskapai', '').strip()
        bandara_asal      = request.POST.get('bandara_asal', '').strip()
        bandara_tujuan    = request.POST.get('bandara_tujuan', '').strip()
        tanggal_penerbangan = request.POST.get('tanggal_penerbangan', '').strip()
        flight_number     = request.POST.get('flight_number', '').strip()
        nomor_tiket       = request.POST.get('nomor_tiket', '').strip()
        kelas_kabin       = request.POST.get('kelas_kabin', '').strip()
        pnr               = request.POST.get('pnr', '').strip()

        # Validasi field yang required
        required_fields = [
            maskapai, bandara_asal, bandara_tujuan, tanggal_penerbangan, flight_number, nomor_tiket, kelas_kabin, pnr
        ]
        if any(not f for f in required_fields):
            errors.append('Semua field wajib diisi.')

        # INSERT ke db jika sudah tdk ada error
        if not errors:
            email = request.session.get('email')
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO CLAIM_MISSING_MILES
                            (email_member, maskapai, bandara_asal, bandara_tujuan, tanggal_penerbangan, flight_number, nomor_tiket, kelas_kabin, pnr, status_penerimaan, timestamp)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Menunggu', NOW())
                    """, [
                        email, maskapai, bandara_asal, bandara_tujuan, tanggal_penerbangan, flight_number, nomor_tiket, kelas_kabin, pnr,
                    ])
            except Exception as e:
                errors.append(str(e))

        # Jika ada error
        if errors:
            with connection.cursor() as cursor:
                # Ambil data maskapai
                cursor.execute('''
                    SELECT kode_maskapai, nama_maskapai 
                    FROM MASKAPAI 
                    ORDER BY nama_maskapai
                ''')
                maskapai_list = cursor.fetchall()

                # Ambil data bandara
                cursor.execute('''
                    SELECT iata_code, nama, kota, negara 
                    FROM BANDARA 
                    ORDER BY kota
                ''')
                bandara_rows = cursor.fetchall()
                bandara_list = [(r[0], r[1], r[2], r[3]) for r in bandara_rows]

            # Render form lagi
            return render(request, 'claim_member.html', {
                'errors': errors,
                'maskapai_list': maskapai_list,
                'bandara_list': bandara_list,
                'claims': [],
                'status_filter': '',
                'show_modal': True,
                'form': request.POST,
            })

        return redirect('miles:claim_member_list')
    return redirect('miles:claim_member_list')

# R - Riwayat Miles - Member
def claim_member_list(request):
    # Cek apakah sudah login
    if not request.session.get('email'):
        messages.error(request, "Anda harus login terlebih dahulu.")
        return redirect('main:login')

    # Cek role jika bukan member redirect ke dashboard
    if request.session.get('role') != "member":
        messages.error(request, "Anda tidak memiliki hak akses.")
        return redirect('main:dashboard')

    # Ambil data status filter
    status_filter = request.GET.get('status', '')

    # Ambil email
    email = request.session.get('email')

    with connection.cursor() as cursor:
        # Ambil data (jika ada status filter yang dipilih)
        if status_filter in ('Menunggu', 'Disetujui', 'Ditolak'):
            cursor.execute("""
                SELECT c.id, c.maskapai, m.nama_maskapai, c.bandara_asal, ba.kota,
                       c.bandara_tujuan, bt.kota, c.tanggal_penerbangan, c.flight_number,
                       c.nomor_tiket, c.kelas_kabin, c.pnr, c.status_penerimaan,
                       c.timestamp, c.email_staf
                FROM CLAIM_MISSING_MILES c
                    JOIN MASKAPAI m ON c.maskapai = m.kode_maskapai
                    JOIN BANDARA ba ON c.bandara_asal = ba.iata_code
                    JOIN BANDARA bt ON c.bandara_tujuan = bt.iata_code
                WHERE c.email_member = %s AND c.status_penerimaan = %s
                ORDER BY c.timestamp DESC
            """, [email, status_filter])
        
        # Ambil data (jika tidak ada status filter yang dipilih)
        else:
            cursor.execute("""
                SELECT c.id, c.maskapai, m.nama_maskapai, c.bandara_asal, ba.kota,
                       c.bandara_tujuan, bt.kota, c.tanggal_penerbangan, c.flight_number,
                       c.nomor_tiket, c.kelas_kabin, c.pnr, c.status_penerimaan,
                       c.timestamp, c.email_staf
                FROM CLAIM_MISSING_MILES c
                    JOIN MASKAPAI m ON c.maskapai = m.kode_maskapai
                    JOIN BANDARA ba ON c.bandara_asal = ba.iata_code
                    JOIN BANDARA bt ON c.bandara_tujuan = bt.iata_code
                WHERE c.email_member = %s
                ORDER BY c.timestamp DESC
            """, [email])

        # Data mapping
        rows = cursor.fetchall()
        claims = []
        for row in rows:
            claims.append({
                'id': row[0],
                'maskapai': row[1],
                'nama_maskapai': row[2],
                'bandara_asal': row[3],
                'nama_asal': f"{row[3]} - {row[4]}",
                'bandara_tujuan': row[5],
                'nama_tujuan': f"{row[5]} - {row[6]}",
                'tanggal_penerbangan': row[7],
                'flight_number': row[8],
                'nomor_tiket': row[9],
                'kelas_kabin': row[10],
                'pnr': row[11],
                'status_penerimaan': row[12],
                'timestamp': row[13],
                'email_staf': row[14],
            })

        # Ambil daftar maskapai utk dropdown
        cursor.execute('''
            SELECT kode_maskapai, nama_maskapai 
            FROM MASKAPAI 
            ORDER BY nama_maskapai
        ''')
        maskapai_list = cursor.fetchall()

        # Ambil daftar bandara utk dropdown
        cursor.execute('''
            SELECT iata_code, nama, kota, negara 
            FROM BANDARA 
            ORDER BY kota
        ''')
        bandara_rows = cursor.fetchall()
        bandara_list = [(r[0], r[1], r[2], r[3]) for r in bandara_rows]

    return render(request, 'claim_member.html', {
        'claims': claims,
        'status_filter': status_filter,
        'maskapai_list': maskapai_list,
        'bandara_list': bandara_list,
    })

# U - Edit Claim - Member
def claim_edit(request, claim_id):
    # Cek apakah sudah login
    if not request.session.get('email'):
        messages.error(request, "Anda harus login terlebih dahulu.")
        return redirect('main:login')

    # Cek role jika bukan member redirect ke dashboard
    if request.session.get('role') != 'member':
        messages.error(request, "Anda tidak memiliki hak akses.")
        return redirect('main:dashboard')

    if request.method == 'POST':
        errors = []

        # Ambil data dari form
        maskapai            = request.POST.get('maskapai', '').strip()
        bandara_asal        = request.POST.get('bandara_asal', '').strip()
        bandara_tujuan      = request.POST.get('bandara_tujuan', '').strip()
        tanggal_penerbangan = request.POST.get('tanggal_penerbangan', '').strip()
        flight_number       = request.POST.get('flight_number', '').strip()
        nomor_tiket         = request.POST.get('nomor_tiket', '').strip()
        kelas_kabin         = request.POST.get('kelas_kabin', '').strip()
        pnr                 = request.POST.get('pnr', '').strip()

        # Validasi required field
        required_fields = [
            maskapai, bandara_asal, bandara_tujuan, tanggal_penerbangan, flight_number, nomor_tiket, kelas_kabin, pnr
        ]
        if any(not f for f in required_fields):
            errors.append('Semua field wajib diisi.')

        # Validasi kelas_kabin
        if kelas_kabin and kelas_kabin not in ('Economy', 'Business', 'First'):
            errors.append('Kelas kabin tidak valid.')

        # Validasi bandara asal dan tujuan tidak boleh sama
        if bandara_asal and bandara_tujuan and bandara_asal == bandara_tujuan:
            errors.append('Bandara asal dan tujuan tidak boleh sama.')

        # Update data jika tdk ada error
        if not errors:
            email = request.session.get('email')
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE CLAIM_MISSING_MILES
                        SET maskapai = %s, bandara_asal = %s, bandara_tujuan = %s, tanggal_penerbangan = %s, flight_number = %s, nomor_tiket = %s, kelas_kabin = %s, pnr = %s
                        WHERE id = %s AND email_member = %s AND status_penerimaan = 'Menunggu'
                    """, [
                        maskapai, bandara_asal, bandara_tujuan,
                        tanggal_penerbangan, flight_number,
                        nomor_tiket, kelas_kabin, pnr,
                        claim_id, email,
                    ])
            except Exception as e:
                errors.append(str(e))

        # Jika ada error, tampilkan pesan error
        if errors:
            messages.error(request, ' '.join(errors))
        else:
            messages.success(request, 'Claim berhasil diupdate.')

    return redirect('miles:claim_member_list')

# D - Batalkan Claim - Member
def claim_delete(request, claim_id):
    # Cek apakah sudah login
    if not request.session.get('email'):
        messages.error(request, "Anda harus login terlebih dahulu.")
        return redirect('main:login')

    # Cek role jika bukan member redirect ke dashboard
    if request.session.get('role') != 'member':
        messages.error(request, "Anda tidak memiliki hak akses.")
        return redirect('main:dashboard')

    if request.method == 'POST':
        email = request.session.get('email')
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM CLAIM_MISSING_MILES
                WHERE id = %s AND email_member = %s AND status_penerimaan = 'Menunggu'
            """, [claim_id, email])

    return redirect('miles:claim_member_list')

# R - Daftar Claim - Staff
def claim_staff_list(request):
    # Cek apakah sudah login
    if not request.session.get('email'):
        messages.error(request, "Anda harus login terlebih dahulu.")
        return redirect('main:login')

    # Cek role jika bukan staff redirect ke dashboard
    if request.session.get('role') != 'staff':
        messages.error(request, "Anda tidak memiliki hak akses.")
        return redirect('main:dashboard')

    # Ambil filter
    status_filter   = request.GET.get('status', '')
    maskapai_filter = request.GET.get('maskapai', '')
    tanggal_dari    = request.GET.get('tanggal_dari', '')
    tanggal_sampai  = request.GET.get('tanggal_sampai', '')

    with connection.cursor() as cursor:
        # Ambil data
        query = """
            SELECT c.id, p.salutation || ' ' || p.first_mid_name || ' ' || p.last_name,
                   c.email_member, c.maskapai, m.nama_maskapai,
                   c.bandara_asal, ba.kota, c.bandara_tujuan, bt.kota,
                   c.tanggal_penerbangan, c.flight_number, c.kelas_kabin,
                   c.timestamp, c.status_penerimaan
            FROM claim_missing_miles c
                JOIN maskapai m  ON c.maskapai       = m.kode_maskapai
                JOIN bandara ba  ON c.bandara_asal   = ba.iata_code
                JOIN bandara bt  ON c.bandara_tujuan = bt.iata_code
                JOIN member mb   ON c.email_member   = mb.email
                JOIN pengguna p  ON mb.email         = p.email
            WHERE 1=1
        """
        params = []

        # Filter status
        if status_filter in ('Menunggu', 'Disetujui', 'Ditolak'):
            query += " AND c.status_penerimaan = %s"
            params.append(status_filter)

        # Filter maskapai
        if maskapai_filter:
            query += " AND c.maskapai = %s"
            params.append(maskapai_filter)

        # Filter tanggal
        if tanggal_dari:
            query += " AND c.timestamp::date >= %s"
            params.append(tanggal_dari)

        if tanggal_sampai:
            query += " AND c.timestamp::date <= %s"
            params.append(tanggal_sampai)

        # Urutkan data 
        query += " ORDER BY c.timestamp DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Format data
        claims = [
            {
                'id'                 : row[0],
                'nama_member'        : row[1],
                'email_member'       : row[2],
                'maskapai'           : row[3],
                'nama_maskapai'      : row[4],
                'rute'               : f"{row[5]} ({row[6]}) → {row[7]} ({row[8]})",
                'tanggal_penerbangan': row[9],
                'flight_number'      : row[10],
                'kelas_kabin'        : row[11],
                'timestamp'          : row[12],
                'status_penerimaan'  : row[13],
            }
            for row in rows
        ]

        # Ambil list maskapai utk filter
        cursor.execute('''SELECT kode_maskapai, nama_maskapai 
                            FROM MASKAPAI 
                            ORDER BY nama_maskapai
        ''')
        maskapai_list = cursor.fetchall()

    return render(request, 'claim_staff.html', {
        'claims'          : claims,
        'maskapai_list'   : maskapai_list,
        'status_filter'   : status_filter,
        'maskapai_filter' : maskapai_filter,
        'tanggal_dari'    : tanggal_dari,
        'tanggal_sampai'  : tanggal_sampai,
    })

# U - Ubah Claim (Approve) - Staff
def claim_approve(request, claim_id):
    # Cek apakah sudah login
    if not request.session.get('email'):
        messages.error(request, "Anda harus login terlebih dahulu.")
        return redirect('main:login')

    # Cek role jika bukan staff redirect ke dashboard
    if request.session.get('role') != 'staff':
        messages.error(request, "Anda tidak memiliki hak akses.")
        return redirect('main:dashboard')

    if request.method == 'POST':
        # Ambil email
        email_staf = request.session.get('email')

        # Update status penerimaan jadi 'Disetujui'
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE claim_missing_miles
                SET status_penerimaan = 'Disetujui', email_staf = %s
                WHERE id = %s AND status_penerimaan = 'Menunggu'
            """, [email_staf, claim_id])

    return redirect('miles:claim_staff_list')

# U - Ubah Claim (Reject) - Staff
def claim_reject(request, claim_id):
    # Cek apakah sudah login
    if not request.session.get('email'):
        messages.error(request, "Anda harus login terlebih dahulu.")
        return redirect('main:login')

    # Cek role jika bukan staff redirect ke dashboard
    if request.session.get('role') != 'staff':
        messages.error(request, "Anda tidak memiliki hak akses.")
        return redirect('main:dashboard')

    if request.method == 'POST':
        # Ambil email
        email_staf = request.session.get('email')

        # Update status penerimaan jadi 'Ditolak'
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE claim_missing_miles
                SET status_penerimaan = 'Ditolak', email_staf = %s
                WHERE id = %s AND status_penerimaan = 'Menunggu'
            """, [email_staf, claim_id])

    return redirect('miles:claim_staff_list')

# R - Riwayat Transfer - Member
def transfer_list(request):
    # Cek apakah sudah login
    if not request.session.get('email'):
        messages.error(request, "Anda harus login terlebih dahulu.")
        return redirect('main:login')

    # Cek role jika bukan member redirect ke dashboard
    if request.session.get('role') != 'member':
        messages.error(request, "Anda tidak memiliki hak akses.")
        return redirect('main:dashboard')

    # Ambil email
    email = request.session.get('email')

    with connection.cursor() as cursor:
        # Ambil data 
        cursor.execute("""
            SELECT t.email_member_1, t.email_member_2, t.timestamp, t.jumlah, t.catatan,
                   p1.salutation || ' ' || p1.first_mid_name || ' ' || p1.last_name,
                   p2.salutation || ' ' || p2.first_mid_name || ' ' || p2.last_name
            FROM TRANSFER t
                JOIN PENGGUNA p1 ON t.email_member_1 = p1.email
                JOIN PENGGUNA p2 ON t.email_member_2 = p2.email
            WHERE t.email_member_1 = %s OR t.email_member_2 = %s
            ORDER BY t.timestamp DESC
        """, [email, email])
        rows = cursor.fetchall()

        # Format data
        transfers = []
        for row in rows:
            is_sender = (row[0] == email)
            transfers.append({
                'timestamp': row[2],
                'email_member_1': row[0],
                'email_member_2': row[1],
                'jumlah': row[3],
                'catatan': row[4],
                'tipe': 'Kirim' if is_sender else 'Terima',
                'nama_lawan': row[6] if is_sender else row[5],
                'email_lawan': row[1] if is_sender else row[0],
            })

        # Ambil award miles
        cursor.execute('''
            SELECT award_miles 
            FROM MEMBER 
            WHERE email = %s
        ''', [email])
        award_miles = cursor.fetchone()[0]

    return render(request, 'transfer.html', {
        'transfers': transfers,
        'award_miles': award_miles,
    })

# C - Buat Transfer - Member
def transfer_create(request):
    # Cek apakah sudah login
    if not request.session.get('email'):
        messages.error(request, "Anda harus login terlebih dahulu.")
        return redirect('main:login')

    # Cek role jika bukan member redirect ke dashboard
    if request.session.get('role') != 'member':
        messages.error(request, "Anda tidak memiliki hak akses.")
        return redirect('main:dashboard')

    if request.method == 'POST':
        errors = []

        # Ambil data dari form
        email_pengirim = request.session.get('email')
        email_penerima = request.POST.get('email_penerima', '').strip()
        jumlah_str     = request.POST.get('jumlah', '0').strip()
        catatan        = request.POST.get('catatan', '').strip()

        # Validasi jumlah
        try:
            jumlah = int(jumlah_str)
        except ValueError:
            jumlah = 0
            errors.append('Jumlah miles harus berupa angka.')

        if jumlah <= 0:
            errors.append('Jumlah miles harus lebih dari 0.')

        # Cek email
        if not email_penerima:
            errors.append('Email penerima wajib diisi.')
        elif email_penerima.lower() == email_pengirim.lower():
            errors.append('Anda tidak bisa mengirim miles ke diri sendiri.')

        # Jika tidak ada error lakukan transfer
        if not errors:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO TRANSFER
                            (email_member_1, email_member_2, timestamp, jumlah, catatan)
                        VALUES
                            (%s, %s, CURRENT_TIMESTAMP, %s, %s)
                    """, [email_pengirim, email_penerima, jumlah, catatan or None])
            except Exception as e:
                error_msg = str(e).split('CONTEXT:')[0] 
                errors.append(error_msg)

        # Jika ada error, kembalikan ke transfer page dgn pesan error
        if errors:
            with connection.cursor() as cursor:
                cursor.execute('''
                    SELECT award_miles 
                    FROM MEMBER 
                    WHERE email = %s
                ''', [email_pengirim])
                award_miles = cursor.fetchone()[0]
                
            return render(request, 'transfer.html', {
                'transfers': [],
                'award_miles': award_miles,
                'errors': errors,
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
