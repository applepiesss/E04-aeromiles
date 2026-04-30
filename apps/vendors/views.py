from django.shortcuts import render

# Create your views here.

def daftar_hadiah(request):
    request.session['role'] = 'staff'

    request.session['username'] = 'Staf Admin'
    return render(request, 'manajemen_hadiah_penyedia.html')

def manage_mitra_view(request):
    request.session['role'] = 'staff'
    return render(request, 'manajemen_mitra.html')
