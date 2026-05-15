from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import connection, DatabaseError
from datetime import datetime

app_name = 'rewards'

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
def redeem_hadiah(request):
    email = request.session.get('email')
    
    if not email or request.session.get('role') != 'member':
        return redirect('main:login')
    
    try:
        with connection.cursor() as cursor:
            # Fetch member's award miles
            cursor.execute("""
                SELECT award_miles FROM MEMBER WHERE email = %s
            """, [email])
            member = dictfetchone(cursor)
            
            if not member:
                messages.error(request, 'Member tidak ditemukan.')
                return redirect('main:dashboard')
            
            current_miles = member['award_miles']
            
            # Fetch member name for display
            cursor.execute("""
                SELECT first_mid_name, last_name FROM PENGGUNA WHERE email = %s
            """, [email])
            pengguna = dictfetchone(cursor)
            member_name = f"{pengguna['first_mid_name']} {pengguna['last_name']}" if pengguna else "Member"
            
            # Fetch all hadiah with penyedia info
            cursor.execute("""
                SELECT 
                    h.kode_hadiah,
                    h.nama,
                    h.miles,
                    h.deskripsi,
                    h.valid_start_date,
                    h.program_end,
                    h.id_penyedia
                FROM HADIAH h
                WHERE CURRENT_DATE BETWEEN h.valid_start_date AND h.program_end
                ORDER BY h.miles ASC
            """)
            hadiah_list = dictfetchall(cursor)
            
            # Fetch redemption history
            cursor.execute("""
                SELECT 
                    r.email_member,
                    r.kode_hadiah,
                    h.nama as nama_hadiah,
                    h.miles as miles_used,
                    r.timestamp
                FROM REDEEM r
                JOIN HADIAH h ON r.kode_hadiah = h.kode_hadiah
                WHERE r.email_member = %s
                ORDER BY r.timestamp DESC
            """, [email])
            riwayat_redeem = dictfetchall(cursor)
        
        context = {
            'current_miles': current_miles,
            'hadiah_list': hadiah_list,
            'riwayat_redeem': riwayat_redeem,
            'member_name': member_name,
        }
        
        return render(request, 'redeem_hadiah.html', context)
    
    except DatabaseError as e:
        messages.error(request, f'Terjadi kesalahan database: {str(e)}')
        return redirect('main:dashboard')
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('main:dashboard')


@require_http_methods(["POST"])
def process_redeem(request):
    """Process reward redemption"""
    email = request.session.get('email')
    
    if not email or request.session.get('role') != 'member':
        return redirect('main:login')
    
    kode_hadiah = request.POST.get('kode_hadiah', '').strip()
    
    if not kode_hadiah:
        messages.error(request, 'Hadiah tidak valid.')
        return redirect('rewards:redeem_hadiah')
    
    try:
        # Call function to handle validation, insert, and return pesan
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT fn_redeem_hadiah(%s, %s) as pesan
            """, [email, kode_hadiah])
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
    
    return redirect('rewards:redeem_hadiah')

