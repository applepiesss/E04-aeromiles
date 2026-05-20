from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import connection, DatabaseError
from datetime import datetime
from collections import defaultdict
import base64
import json

app_name = 'staf'

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
def laporan_transaksi(request):
    """Display transaction report dashboard"""
    if request.session.get('role') != 'staff':
        return redirect('main:login')
    
    try:
        with connection.cursor() as cursor:
            # Fetch all transactions from database
            cursor.execute("""
                SELECT 
                    'TRANS-' || encode(convert_to(t.email_member_1 || '|' || t.email_member_2 || '|' || t.timestamp::text, 'UTF8'), 'base64') as id,
                    'Transfer' as type,
                    t.email_member_1 as from_member,
                    p1.first_mid_name || ' ' || p1.last_name as from_member_name,
                    t.email_member_2 as to_member,
                    p2.first_mid_name || ' ' || p2.last_name as to_member_name,
                    t.jumlah,
                    t.timestamp::text as waktu,
                    t.catatan,
                    true as deletable
                FROM TRANSFER t
                JOIN PENGGUNA p1 ON t.email_member_1 = p1.email
                JOIN PENGGUNA p2 ON t.email_member_2 = p2.email
            """)
            transfers = dictfetchall(cursor)
            
            # Redeems
            cursor.execute("""
                SELECT 
                    'REDEEM-' || encode(convert_to(r.email_member || '|' || r.kode_hadiah || '|' || r.timestamp::text, 'UTF8'), 'base64') as id,
                    'Redeem' as type,
                    r.email_member,
                    p.first_mid_name || ' ' || p.last_name as member_name,
                    r.kode_hadiah,
                    h.nama as hadiah_name,
                    h.miles as jumlah,
                    r.timestamp::text as waktu,
                    true as deletable
                FROM REDEEM r
                JOIN PENGGUNA p ON r.email_member = p.email
                JOIN HADIAH h ON r.kode_hadiah = h.kode_hadiah
            """)
            redeems = dictfetchall(cursor)
            
            # Package purchases
            cursor.execute("""
                SELECT 
                    'PACKAGE-' || encode(convert_to(m.id_award_miles_package || '|' || m.email_member || '|' || m.timestamp::text, 'UTF8'), 'base64') as id,
                    'Pembelian Package' as type,
                    m.email_member,
                    p.first_mid_name || ' ' || p.last_name as member_name,
                    m.id_award_miles_package as package_id,
                    a.jumlah_award_miles as jumlah,
                    a.harga_paket as harga,
                    m.timestamp::text as waktu,
                    false as deletable
                FROM MEMBER_AWARD_MILES_PACKAGE m
                JOIN PENGGUNA p ON m.email_member = p.email
                JOIN AWARD_MILES_PACKAGE a ON m.id_award_miles_package = a.id
            """)
            packages = dictfetchall(cursor)
            
            # Approved claims
            cursor.execute("""
                SELECT 
                    'CLAIM-' || c.id::text as id,
                    'Klaim Disetujui' as type,
                    c.email_member,
                    p.first_mid_name || ' ' || p.last_name as member_name,
                    1000 as jumlah,
                    c.timestamp::text as waktu,
                    false as deletable
                FROM CLAIM_MISSING_MILES c
                JOIN PENGGUNA p ON c.email_member = p.email
                WHERE c.status_penerimaan = 'Disetujui'
            """)
            claims = dictfetchall(cursor)
            
            # Get top 5 members using procedure
            cursor.execute("SELECT * FROM sp_top5_member_total_miles()")
            top_members_raw = dictfetchall(cursor)
            top_members = [(row['email_member'], row['total_miles']) for row in top_members_raw]
            
            # Get unique members for dropdown
            cursor.execute("""
                SELECT DISTINCT (p.first_mid_name || ' ' || p.last_name) as name
                FROM PENGGUNA p
                JOIN MEMBER m ON p.email = m.email
                ORDER BY name
            """)
            unique_members = [row['name'] for row in dictfetchall(cursor)]
        
        # Combine all transactions
        all_transactions = transfers + redeems + packages + claims
        all_transactions.sort(key=lambda x: x['waktu'], reverse=True)
        
        # Apply filters
        filter_type = request.GET.get('filter_type', 'all')
        filter_member = request.GET.get('filter_member', 'all')
        filter_date_from = request.GET.get('filter_date_from', '')
        filter_date_to = request.GET.get('filter_date_to', '')
        
        filtered_transactions = all_transactions.copy()
        
        if filter_type != 'all':
            filtered_transactions = [t for t in filtered_transactions if t['type'] == filter_type]
        
        if filter_member != 'all':
            filtered_transactions = [t for t in filtered_transactions 
                                   if t.get('member_name') == filter_member 
                                   or t.get('from_member_name') == filter_member]
        
        if filter_date_from or filter_date_to:
            filtered_by_date = []
            for t in filtered_transactions:
                trans_date = datetime.strptime(t['waktu'][:19], '%Y-%m-%d %H:%M:%S')
                if filter_date_from:
                    from_date = datetime.strptime(filter_date_from + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
                    if trans_date < from_date:
                        continue
                if filter_date_to:
                    to_date = datetime.strptime(filter_date_to + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
                    if trans_date > to_date:
                        continue
                filtered_by_date.append(t)
            filtered_transactions = filtered_by_date
        
        # Calculate statistics - filter by current month for redeems
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        def is_current_month(waktu_str):
            trans_date = datetime.strptime(waktu_str[:19], '%Y-%m-%d %H:%M:%S')
            return trans_date.month == current_month and trans_date.year == current_year
        
        total_transfer = sum(t['jumlah'] for t in all_transactions if t['type'] == 'Transfer')
        month_redeems = sum(t['jumlah'] for t in all_transactions 
                           if t['type'] == 'Redeem' and is_current_month(t['waktu']))
        total_package = sum(t['jumlah'] for t in all_transactions if t['type'] == 'Pembelian Package')
        total_claims = sum(t['jumlah'] for t in all_transactions if t['type'] == 'Klaim Disetujui')
        
        transaction_types = ['Transfer', 'Redeem', 'Pembelian Package', 'Klaim Disetujui']
        
        context = {
            'transactions': filtered_transactions,
            'all_transactions': all_transactions,
            'unique_members': unique_members,
            'transaction_types': transaction_types,
            'filter_type': filter_type,
            'filter_member': filter_member,
            'filter_date_from': filter_date_from,
            'filter_date_to': filter_date_to,
            'total_transfer': total_transfer,
            'month_redeems': month_redeems,
            'total_package': total_package,
            'total_claims': total_claims,
            'total_miles': total_transfer + month_redeems + total_package + total_claims,
            'top_members': top_members,
            'view_type': request.GET.get('view_type', 'transactions'),
        }
        
        return render(request, 'laporan_transaksi.html', context)
    
    except DatabaseError as e:
        messages.error(request, f'Terjadi kesalahan database: {str(e)}')
        return redirect('main:dashboard')
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
        return redirect('main:dashboard')


@require_http_methods(["POST"])
def delete_transaction(request):
    """Delete transaction from database (only allowed for Transfer and Redeem)"""
    if request.session.get('role') != 'staff':
        return redirect('main:login')
    
    transaction_id = request.POST.get('transaction_id', '')
    
    try:
        with connection.cursor() as cursor:
            if transaction_id.startswith('TRANS-'):
                # Decode composite key: email_member_1|email_member_2|timestamp
                try:
                    encoded_key = transaction_id[6:]  # Remove 'TRANS-' prefix
                    decoded_key = base64.b64decode(encoded_key).decode('utf-8')
                    parts = decoded_key.split('|')
                    email1, email2, timestamp_str = parts[0], parts[1], parts[2]
                    
                    cursor.execute(
                        "DELETE FROM TRANSFER WHERE email_member_1 = %s AND email_member_2 = %s AND timestamp = %s",
                        [email1, email2, timestamp_str]
                    )
                    if cursor.rowcount > 0:
                        messages.success(request, 'Transfer berhasil dihapus.')
                    else:
                        messages.error(request, 'Transfer tidak ditemukan.')
                except Exception as e:
                    messages.error(request, f'Error decoding transaction ID: {str(e)}')
            
            elif transaction_id.startswith('REDEEM-'):
                # Decode composite key: email_member|kode_hadiah|timestamp
                try:
                    encoded_key = transaction_id[7:]  # Remove 'REDEEM-' prefix
                    decoded_key = base64.b64decode(encoded_key).decode('utf-8')
                    parts = decoded_key.split('|')
                    email, kode_hadiah, timestamp_str = parts[0], parts[1], parts[2]
                    
                    cursor.execute(
                        "DELETE FROM REDEEM WHERE email_member = %s AND kode_hadiah = %s AND timestamp = %s",
                        [email, kode_hadiah, timestamp_str]
                    )
                    if cursor.rowcount > 0:
                        messages.success(request, 'Redeem berhasil dihapus.')
                    else:
                        messages.error(request, 'Redeem tidak ditemukan.')
                except Exception as e:
                    messages.error(request, f'Error decoding transaction ID: {str(e)}')
            
            else:
                # Cannot delete Package or Claims
                messages.error(request, 'Tipe transaksi ini tidak dapat dihapus.')
    
    except DatabaseError as e:
        messages.error(request, f'Terjadi kesalahan database: {str(e)}')
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan: {str(e)}')
    
    return redirect('staf:laporan_transaksi')

