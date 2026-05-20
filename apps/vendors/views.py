from django.shortcuts import render, redirect
from django.db import IntegrityError, connection
from django.contrib import messages
import datetime

def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def capture_db_notices(request):
    """Helper untuk menangkap RAISE NOTICE dari PostgreSQL"""
    if connection.connection and connection.connection.notices:
        for notice in connection.connection.notices:
            msg = notice.replace("NOTICE:", "").strip()
            if msg:
                messages.success(request, msg)
        connection.connection.notices.clear()

# Create your views here.

def manage_mitra_view(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM MITRA ORDER BY tanggal_kerja_sama DESC")
        partners = dictfetchall(cursor)
    for p in partners:
        p['tanggal_kerja_sama_fmt'] = p['tanggal_kerja_sama'].strftime('%d %B %Y')
        p['tanggal_kerja_sama_iso'] = p['tanggal_kerja_sama'].strftime('%Y-%m-%d')
    return render(request, 'manajemen_mitra.html', {'partners': partners})

def save_mitra(request):
    if request.method == 'POST':
        is_update = request.POST.get('isUpdate') == 'true'
        email = request.POST.get('email')
        nama = request.POST.get('nama')
        join_date = request.POST.get('join_date')

        with connection.cursor() as cursor:
            if connection.connection: connection.connection.notices.clear()
            try:
                if is_update:
                    cursor.execute("""
                        UPDATE MITRA SET nama_mitra = %s, tanggal_kerja_sama = %s 
                        WHERE email_mitra = %s
                    """, [nama, join_date, email])
                    messages.info(request, "Data mitra berhasil diperbarui.")
                else:
                    cursor.execute("INSERT INTO PENYEDIA DEFAULT VALUES RETURNING id")
                    id_penyedia = cursor.fetchone()[0]
                    cursor.execute("""
                        INSERT INTO MITRA (email_mitra, id_penyedia, nama_mitra, tanggal_kerja_sama)
                        VALUES (%s, %s, %s, %s)
                    """, [email, id_penyedia, nama, join_date])
                    messages.success(request, f"Mitra {nama} berhasil didaftarkan.")
                
                capture_db_notices(request)

            except IntegrityError as e:
                messages.error(request, "Gagal menyimpan: Data sudah ada atau melanggar aturan database.")
            except Exception as e:
                messages.error(request, f"Terjadi kesalahan: {str(e)}")
    return redirect('vendors:manage_mitra')

def delete_mitra(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        with connection.cursor() as cursor:
            try:
                cursor.execute("SELECT id_penyedia FROM MITRA WHERE email_mitra = %s", [email])
                row = cursor.fetchone()
                if row:
                    cursor.execute("DELETE FROM PENYEDIA WHERE id = %s", [row[0]])
                    messages.success(request, "Mitra berhasil dihapus.")
                capture_db_notices(request)
            except Exception as e:
                messages.error(request, f"Gagal menghapus mitra: {str(e)}")
                
    return redirect('vendors:manage_mitra')


def daftar_hadiah(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT h.*, COALESCE(m.nama_mitra, mas.nama_maskapai) as nama_penyedia
            FROM HADIAH h
            LEFT JOIN MITRA m ON h.id_penyedia = m.id_penyedia
            LEFT JOIN MASKAPAI mas ON h.id_penyedia = mas.id_penyedia
            ORDER BY h.kode_hadiah DESC
        """)
        rewards = dictfetchall(cursor)
        
        today = datetime.date.today()
        for r in rewards:
            r['valid_start_date_iso'] = r['valid_start_date'].strftime('%Y-%m-%d')
            r['program_end_iso'] = r['program_end'].strftime('%Y-%m-%d')
            r['valid_start_date_fmt'] = r['valid_start_date'].strftime('%d %b %Y')
            r['program_end_fmt'] = r['program_end'].strftime('%d %b %Y')
            
            if today > r['program_end']:
                r['status'], r['status_text'], r['badge_class'] = 'expired', 'Kadaluarsa', 'badge-inactive'
            elif today < r['valid_start_date']:
                r['status'], r['status_text'], r['badge_class'] = 'upcoming', 'Akan Datang', 'badge-inactive'
            else:
                r['status'], r['status_text'], r['badge_class'] = 'active', 'Aktif', 'badge-active'

        cursor.execute("SELECT id_penyedia as id, nama_mitra as nama FROM MITRA UNION SELECT id_penyedia as id, nama_maskapai as nama FROM MASKAPAI")
        vendors = dictfetchall(cursor)

    return render(request, 'manajemen_hadiah_penyedia.html', {'rewards': rewards, 'vendors': vendors})

def delete_hadiah(request):
    if request.method == 'POST':
        kode = request.POST.get('kode')
        with connection.cursor() as cursor:
            try:
                cursor.execute("DELETE FROM REDEEM WHERE kode_hadiah = %s", [kode])
                cursor.execute("DELETE FROM HADIAH WHERE kode_hadiah = %s", [kode])
                messages.success(request, "Hadiah berhasil dihapus.")
                capture_db_notices(request)
            except Exception as e:
                messages.error(request, f"Gagal menghapus hadiah: {str(e)}")
            
    return redirect('vendors:daftar_hadiah')


def save_hadiah(request):
    if request.method == 'POST':
        kode = request.POST.get('kode')
        nama = request.POST.get('nama')
        vendor_id = request.POST.get('vendor')
        miles = request.POST.get('miles')
        desc = request.POST.get('desc')
        start = request.POST.get('start')
        end = request.POST.get('end')

        with connection.cursor() as cursor:
            if connection.connection: connection.connection.notices.clear()
            
            try:
                if kode: 
                    cursor.execute("""
                        UPDATE HADIAH SET nama=%s, miles=%s, deskripsi=%s, 
                        valid_start_date=%s, program_end=%s, id_penyedia=%s
                        WHERE kode_hadiah=%s
                    """, [nama, miles, desc, start, end, vendor_id, kode])
                    messages.info(request, "Hadiah berhasil diperbarui.")
                else: 
                    cursor.execute("""
                        INSERT INTO HADIAH (nama, miles, deskripsi, valid_start_date, program_end, id_penyedia)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, [nama, miles, desc, start, end, vendor_id])
                    messages.success(request, "Hadiah berhasil ditambahkan.")
                
                capture_db_notices(request)
            except Exception as e:
                messages.error(request, f"Database Error: {str(e)}")
                
    return redirect('vendors:daftar_hadiah')