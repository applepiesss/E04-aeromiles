from django.shortcuts import redirect, render

DUMMY_PENGGUNA = {
    'judy.hopps@yahoo.com': {
        'password': 'password123', 
        'salutation': 'Ms.',       
        'first_mid_name': 'Judy',
        'last_name': 'Hopps',
        'country_code': '+1',     
        'mobile_number': '5554941103',
        'tanggal_lahir': '1994-11-03',
        'kewarganegaraan': 'Amerika',
        'role': 'member'           
    },
    'nick.wilde@yahoo.com': {
        'password': 'password456',
        'salutation': 'Mr.',
        'first_mid_name': 'Nick',
        'last_name': 'Wilde',
        'country_code': '+1',
        'mobile_number': '5558560622',
        'tanggal_lahir': '1985-06-22',
        'kewarganegaraan': 'Amerika',
        'role': 'staff'
    },
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