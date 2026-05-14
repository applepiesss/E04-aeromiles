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