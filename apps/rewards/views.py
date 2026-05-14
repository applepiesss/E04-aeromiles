from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from datetime import datetime


# Hardcoded data for Redeem Hadiah feature
PENYEDIA_DATA = {
    1: {'id': 1, 'nama': 'Kopi House'},
    2: {'id': 2, 'nama': 'Cinema Premiere'},
    3: {'id': 3, 'nama': 'Fashion Boutique'},
    4: {'id': 4, 'nama': 'Supermarket XYZ'},
    5: {'id': 5, 'nama': 'Hotel Mewah'},
    6: {'id': 6, 'nama': 'E-Money Provider'},
    7: {'id': 7, 'nama': 'Travel Agency'},
    8: {'id': 8, 'nama': 'Fine Dining'},
}

HADIAH_DATA = [
    {
        'kode_hadiah': 'RWD-001',
        'nama': 'Voucher Kopi Rp50.000',
        'miles': 500,
        'deskripsi': 'Nikmati kopi gratis atau potongan harga di gerai partner kami.',
        'valid_start_date': '2025-01-01',
        'program_end': '2025-12-31',
        'id_penyedia': 1,
    },
    {
        'kode_hadiah': 'RWD-002',
        'nama': 'Tiket Nonton Bioskop Premiere',
        'miles': 1200,
        'deskripsi': 'Satu tiket nonton film premier di akhir pekan, berlaku di seluruh cabang.',
        'valid_start_date': '2025-02-01',
        'program_end': '2025-11-30',
        'id_penyedia': 2,
    },
    {
        'kode_hadiah': 'RWD-003',
        'nama': 'Merchandise Kaos Eksklusif',
        'miles': 2500,
        'deskripsi': 'Kaos edisi terbatas khusus untuk member loyalty program.',
        'valid_start_date': '2025-03-01',
        'program_end': '2026-06-30',
        'id_penyedia': 3,
    },
    {
        'kode_hadiah': 'RWD-004',
        'nama': 'Diskon 20% Belanja Supermarket',
        'miles': 800,
        'deskripsi': 'Potongan harga maksimal Rp100.000 untuk belanja bulanan Anda.',
        'valid_start_date': '2025-01-15',
        'program_end': '2026-05-15',
        'id_penyedia': 4,
    },
    {
        'kode_hadiah': 'RWD-005',
        'nama': 'Voucher Menginap Hotel Bintang 4',
        'miles': 15000,
        'deskripsi': 'Gratis menginap 1 malam untuk tipe kamar Deluxe (termasuk sarapan).',
        'valid_start_date': '2025-06-01',
        'program_end': '2026-12-31',
        'id_penyedia': 5,
    },
    {
        'kode_hadiah': 'RWD-006',
        'nama': 'E-Money Saldo Rp100.000',
        'miles': 1000,
        'deskripsi': 'Top up saldo e-money langsung ke nomor ponsel yang terdaftar.',
        'valid_start_date': '2025-01-01',
        'program_end': '2026-01-01',
        'id_penyedia': 6,
    },
    {
        'kode_hadiah': 'RWD-007',
        'nama': 'Paket Liburan Bali 3H2M',
        'miles': 50000,
        'deskripsi': 'Paket tour lengkap ke Bali untuk 1 orang, sudah termasuk tiket pesawat.',
        'valid_start_date': '2025-08-01',
        'program_end': '2026-12-31',
        'id_penyedia': 7,
    },
    {
        'kode_hadiah': 'RWD-008',
        'nama': 'Voucher Makan Malam Romantis',
        'miles': 3500,
        'deskripsi': 'Set menu fine dining untuk 2 orang di restoran mitra kami.',
        'valid_start_date': '2025-02-10',
        'program_end': '2026-03-10',
        'id_penyedia': 8,
    },
    {
        'kode_hadiah': 'RWD-009',
        'nama': 'Gratis Bagasi Pesawat 10kg',
        'miles': 2000,
        'deskripsi': 'Tambahan kuota bagasi penerbangan domestik untuk kenyamanan liburan Anda.',
        'valid_start_date': '2025-01-01',
        'program_end': '2026-12-31',
        'id_penyedia': 1,
    },
    {
        'kode_hadiah': 'RWD-010',
        'nama': 'Akses Airport Premium Lounge',
        'miles': 3000,
        'deskripsi': 'Akses gratis ke premium lounge di bandara selama maksimal 3 jam.',
        'valid_start_date': '2025-04-01',
        'program_end': '2026-12-31',
        'id_penyedia': 2,
    },
]

# Member's award miles balance
MEMBER_MILES = {
    'MEM0001234': 5000,  # john.doe@aeromiles.com
}

# Hardcoded redemption history
RIWAYAT_REDEEM = [
    {
        'id': 1,
        'member_id': 'MEM0001234',
        'kode_hadiah': 'RWD-001',
        'nama_hadiah': 'Voucher Kopi Rp50.000',
        'miles_used': 500,
        'timestamp': '2026-03-15 14:32:00',
    },
    {
        'id': 2,
        'member_id': 'MEM0001234',
        'kode_hadiah': 'RWD-004',
        'nama_hadiah': 'Diskon 20% Belanja Supermarket',
        'miles_used': 800,
        'timestamp': '2026-03-10 10:15:00',
    },
    {
        'id': 3,
        'member_id': 'MEM0001234',
        'kode_hadiah': 'RWD-009',
        'nama_hadiah': 'Gratis Bagasi Pesawat 10kg',
        'miles_used': 2000,
        'timestamp': '2026-02-28 16:45:00',
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
def redeem_hadiah(request):
    """Display reward catalog and redemption history for members"""
    # For mockup, use hardcoded member
    member_id = 'MEM0001234'
    current_miles = MEMBER_MILES.get(member_id, 0)
    
    # Filter hadiah that are still valid (today >= valid_start_date AND today <= program_end)
    today = datetime.now().date()
    valid_hadiah = []
    
    for hadiah in HADIAH_DATA:
        valid_start = datetime.strptime(hadiah['valid_start_date'], '%Y-%m-%d').date()
        program_end = datetime.strptime(hadiah['program_end'], '%Y-%m-%d').date()
        
        if valid_start <= today <= program_end:
            # Enrich with provider info
            penyedia = PENYEDIA_DATA.get(hadiah['id_penyedia'], {})
            hadiah_enriched = hadiah.copy()
            hadiah_enriched['penyedia_nama'] = penyedia.get('nama', 'Unknown')
            hadiah_enriched['penyedia_logo'] = penyedia.get('logo', '')
            valid_hadiah.append(hadiah_enriched)
    
    # Get redemption history
    riwayat = RIWAYAT_REDEEM.copy()
    
    context = {
        'member_id': member_id,
        'current_miles': current_miles,
        'hadiah_list': valid_hadiah,
        'riwayat_redeem': riwayat,
        'member_name': MEMBER_DATA['first_mid_name'] + ' ' + MEMBER_DATA['last_name'],
    }
    
    return render(request, 'redeem_hadiah.html', context)


@require_http_methods(["POST"])
def process_redeem(request):
    """Process reward redemption"""
    member_id = 'MEM0001234'
    current_miles = MEMBER_MILES.get(member_id, 0)
    kode_hadiah = request.POST.get('kode_hadiah', '')
    
    # Find hadiah
    hadiah_found = None
    for hadiah in HADIAH_DATA:
        if hadiah['kode_hadiah'] == kode_hadiah:
            hadiah_found = hadiah
            break
    
    if not hadiah_found:
        messages.error(request, 'Hadiah tidak ditemukan.')
        return redirect('rewards:redeem_hadiah')
    
    # Validate: date still valid
    today = datetime.now().date()
    valid_start = datetime.strptime(hadiah_found['valid_start_date'], '%Y-%m-%d').date()
    program_end = datetime.strptime(hadiah_found['program_end'], '%Y-%m-%d').date()
    
    if not (valid_start <= today <= program_end):
        messages.error(request, 'Hadiah sudah tidak berlaku atau belum aktif.')
        return redirect('rewards:redeem_hadiah')
    
    # Validate: sufficient miles
    if current_miles < hadiah_found['miles']:
        messages.error(request, f'Miles Anda tidak cukup. Anda memiliki {current_miles} miles, tetapi membutuhkan {hadiah_found["miles"]} miles.')
        return redirect('rewards:redeem_hadiah')
    
    # Deduct miles (mockup - dalam implementasi nyata akan update database)
    new_miles = current_miles - hadiah_found['miles']
    MEMBER_MILES[member_id] = new_miles
    
    # Add to redemption history (mockup)
    new_redeem = {
        'id': len(RIWAYAT_REDEEM) + 1,
        'member_id': member_id,
        'kode_hadiah': hadiah_found['kode_hadiah'],
        'nama_hadiah': hadiah_found['nama'],
        'miles_used': hadiah_found['miles'],
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    RIWAYAT_REDEEM.insert(0, new_redeem)  # Add to beginning
    
    messages.success(request, f'Hadiah "{hadiah_found["nama"]}" berhasil di-redeem! {hadiah_found["miles"]} miles telah dipotong.')
    return redirect('rewards:redeem_hadiah')

app_name = 'rewards'
