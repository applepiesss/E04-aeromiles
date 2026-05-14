from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
import datetime

def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

# Create your views here.

def daftar_hadiah(request):
    request.session['role'] = 'staff'

    request.session['username'] = 'Staf Admin'
    return render(request, 'manajemen_hadiah_penyedia.html')

def manage_mitra_view(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT email_mitra, id_penyedia, nama_mitra, tanggal_kerja_sama
            FROM MITRA
            ORDER BY tanggal_kerja_sama DESC
        """)
        partners = dictfetchall(cursor)
    for p in partners:
        if p['tanggal_kerja_sama']:
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
            if is_update:
                cursor.execute("""
                    UPDATE MITRA 
                    SET nama_mitra = %s, tanggal_kerja_sama = %s 
                    WHERE email_mitra = %s
                """, [nama, join_date, email])
                messages.success(request, "Data mitra berhasil diupdate.")
            else:
                try:
                    cursor.execute("INSERT INTO PENYEDIA DEFAULT VALUES RETURNING id")
                    id_penyedia = cursor.fetchone()[0]
                    
                    cursor.execute("""
                        INSERT INTO MITRA (email_mitra, id_penyedia, nama_mitra, tanggal_kerja_sama)
                        VALUES (%s, %s, %s, %s)
                    """, [email, id_penyedia, nama, join_date])
                    messages.success(request, "Mitra baru berhasil didaftarkan.")
                except Exception as e:
                    messages.error(request, "Gagal mendaftarkan mitra: Email mungkin sudah terdaftar.")
                    
    return redirect('vendors:manage_mitra')

def delete_mitra(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        with connection.cursor() as cursor:
            cursor.execute("SELECT id_penyedia FROM MITRA WHERE email_mitra = %s", [email])
            row = cursor.fetchone()
            if row:
                id_penyedia = row[0]
                cursor.execute("DELETE FROM PENYEDIA WHERE id = %s", [id_penyedia])
                messages.success(request, "Mitra beserta hadiah yang terkait berhasil dihapus.")
                
    return redirect('vendors:manage_mitra')


def daftar_hadiah(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT h.kode_hadiah, h.nama, h.miles, h.deskripsi, 
                    h.valid_start_date, h.program_end, h.id_penyedia,
                    COALESCE(m.nama_mitra, mas.nama_maskapai) as nama_penyedia
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
                r['status'] = 'expired'
                r['status_text'] = 'Kadaluarsa'
                r['badge_class'] = 'badge-inactive'
            elif today < r['valid_start_date']:
                r['status'] = 'upcoming'
                r['status_text'] = 'Akan Datang'
                r['badge_class'] = 'badge-inactive'
            else:
                r['status'] = 'active'
                r['status_text'] = 'Aktif'
                r['badge_class'] = 'badge-active'

        cursor.execute("""
            SELECT id_penyedia as id, nama_maskapai as nama FROM MASKAPAI
            UNION
            SELECT id_penyedia as id, nama_mitra as nama FROM MITRA
            ORDER BY nama ASC
        """)
        vendors = dictfetchall(cursor)

    return render(request, 'manajemen_hadiah_penyedia.html', {
        'rewards': rewards, 
        'vendors': vendors
    })