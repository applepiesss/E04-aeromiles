from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from datetime import datetime
from collections import defaultdict


# Hardcoded Member Data
MEMBERS = {
    'tony.stark@gmail.com': {'name': 'Tony Stark', 'member_number': 'MEM001'},
    'peter.parker@gmail.com': {'name': 'Peter Parker', 'member_number': 'MEM002'},
    'steve.rogers@gmail.com': {'name': 'Steve Rogers', 'member_number': 'MEM003'},
    'bruce.banner@gmail.com': {'name': 'Bruce Banner', 'member_number': 'MEM004'},
    'natasha.romanoff@gmail.com': {'name': 'Natasha Romanoff', 'member_number': 'MEM005'},
    'wanda.maximoff@gmail.com': {'name': 'Wanda Maximoff', 'member_number': 'MEM006'},
    'satoru.gojo@gmail.com': {'name': 'Satoru Gojo', 'member_number': 'MEM007'},
    'megumi.fushiguro@gmail.com': {'name': 'Megumi Fushiguro', 'member_number': 'MEM008'},
    'yuji.itadori@gmail.com': {'name': 'Yuji Itadori', 'member_number': 'MEM009'},
    'nobara.kugisaki@gmail.com': {'name': 'Nobara Kugisaki', 'member_number': 'MEM010'},
    'toji.fushiguro@gmail.com': {'name': 'Toji Fushiguro', 'member_number': 'MEM011'},
    'kento.nanami@gmail.com': {'name': 'Kento Nanami', 'member_number': 'MEM012'},
    'shoko.ieiri@gmail.com': {'name': 'Shoko Ieiri', 'member_number': 'MEM013'},
    'choso.kamo@gmail.com': {'name': 'Choso Kamo', 'member_number': 'MEM014'},
    'suguru.geto@gmail.com': {'name': 'Suguru Geto', 'member_number': 'MEM015'},
    'judy.hopps@yahoo.com': {'name': 'Judy Hopps', 'member_number': 'MEM016'},
    'nick.wilde@yahoo.com': {'name': 'Nick Wilde', 'member_number': 'MEM017'},
    'strawberry.shortcake@gmail.com': {'name': 'Strawberry Shortcake', 'member_number': 'MEM018'},
    'blueberry.muffin@gmail.com': {'name': 'Blueberry Muffin', 'member_number': 'MEM019'},
    'orange.blossom@gmail.com': {'name': 'Orange Blossom', 'member_number': 'MEM020'},
    'twilight.sparkle@yahoo.com': {'name': 'Twilight Sparkle', 'member_number': 'MEM021'},
    'pinkie.pie@yahoo.com': {'name': 'Pinkie Pie', 'member_number': 'MEM022'},
    'rainbow.dash@yahoo.com': {'name': 'Rainbow Dash', 'member_number': 'MEM023'},
    'mike.wheeler@gmail.com': {'name': 'Mike Wheeler', 'member_number': 'MEM024'},
    'will.byers@gmail.com': {'name': 'Will Byers', 'member_number': 'MEM025'},
    'dustin.henderson@gmail.com': {'name': 'Dustin Henderson', 'member_number': 'MEM026'},
    'lucas.sinclair@gmail.com': {'name': 'Lucas Sinclair', 'member_number': 'MEM027'},
    'max.mayfield@gmail.com': {'name': 'Max Mayfield', 'member_number': 'MEM028'},
    'jane.hopper@gmail.com': {'name': 'Jane Hopper', 'member_number': 'MEM029'},
    'steve.harrington@gmail.com': {'name': 'Steve Harrington', 'member_number': 'MEM030'},
    'nancy.wheeler@gmail.com': {'name': 'Nancy Wheeler', 'member_number': 'MEM031'},
    'larajean.songcovey@ui.ac.id': {'name': 'Lara Jean Song Covey', 'member_number': 'MEM032'},
    'peter.kavinsky@ui.ac.id': {'name': 'Peter Kavinsky', 'member_number': 'MEM033'},
    'kitty.songcovey@ui.ac.id': {'name': 'Kitty Song Covey', 'member_number': 'MEM034'},
    'margot.songcovey@ui.ac.id': {'name': 'Margot Song Covey', 'member_number': 'MEM035'},
    'josh.sanderson@ui.ac.id': {'name': 'Josh Sanderson', 'member_number': 'MEM036'},
}

# Reward Products
HADIAH_DATA = [
    {'kode': 'RWD-001', 'nama': 'Diskon Hotel 10%', 'miles': 500},
    {'kode': 'RWD-002', 'nama': 'Upgrade Seat', 'miles': 1500},
    {'kode': 'RWD-003', 'nama': 'Free Baggage', 'miles': 800},
    {'kode': 'RWD-004', 'nama': 'Diskon Voucher 15%', 'miles': 1000},
    {'kode': 'RWD-005', 'nama': 'Priority Boarding', 'miles': 2000},
    {'kode': 'RWD-006', 'nama': 'Lounge Access', 'miles': 3000},
    {'kode': 'RWD-007', 'nama': 'Free Flight 1 Way', 'miles': 10000},
    {'kode': 'RWD-008', 'nama': 'Hotel Night Stay', 'miles': 5000},
    {'kode': 'RWD-009', 'nama': 'Diskon 20%', 'miles': 2500},
    {'kode': 'RWD-010', 'nama': 'Airport Lounge Pass', 'miles': 4000},
    {'kode': 'RWD-011', 'nama': 'Pet Travel Fee', 'miles': 1200},
    {'kode': 'RWD-012', 'nama': 'Miles Multiplier 2x', 'miles': 6000},
]

# Award Miles Package Products
AWARD_MILES_PACKAGES = [
    {'id': 'AMP-001', 'harga_paket': 150000.00, 'jumlah_award_miles': 1000},
    {'id': 'AMP-002', 'harga_paket': 650000.00, 'jumlah_award_miles': 5000},
    {'id': 'AMP-003', 'harga_paket': 1250000.00, 'jumlah_award_miles': 10000},
    {'id': 'AMP-004', 'harga_paket': 2800000.00, 'jumlah_award_miles': 25000},
    {'id': 'AMP-005', 'harga_paket': 5200000.00, 'jumlah_award_miles': 50000},
]

# Transfer Transactions
TRANSFER_DATA = [
    {'id': 1, 'from_member': 'tony.stark@gmail.com', 'to_member': 'peter.parker@gmail.com', 'jumlah': 5000, 'waktu': '2025-01-10 09:15:00', 'catatan': 'Dana tambahan untuk perlengkapan magang Stark Industries'},
    {'id': 2, 'from_member': 'steve.rogers@gmail.com', 'to_member': 'tony.stark@gmail.com', 'jumlah': 50, 'waktu': '2025-01-12 14:30:00', 'catatan': 'Ganti uang kopi dan donat kemarin'},
    {'id': 3, 'from_member': 'bruce.banner@gmail.com', 'to_member': 'tony.stark@gmail.com', 'jumlah': 1200, 'waktu': '2025-02-05 10:00:00', 'catatan': 'Ganti rugi peralatan lab yang tidak sengaja rusak'},
    {'id': 4, 'from_member': 'natasha.romanoff@gmail.com', 'to_member': 'wanda.maximoff@gmail.com', 'jumlah': 300, 'waktu': '2025-02-14 19:00:00', 'catatan': 'Patungan hadiah ulang tahun Vision'},
    {'id': 5, 'from_member': 'satoru.gojo@gmail.com', 'to_member': 'megumi.fushiguro@gmail.com', 'jumlah': 2500, 'waktu': '2025-03-01 08:00:00', 'catatan': 'Uang saku bulanan. Jangan lupa makan enak!'},
    {'id': 6, 'from_member': 'yuji.itadori@gmail.com', 'to_member': 'nobara.kugisaki@gmail.com', 'jumlah': 150, 'waktu': '2025-03-05 16:45:00', 'catatan': 'Titip belikan crepes di Harajuku'},
    {'id': 7, 'from_member': 'toji.fushiguro@gmail.com', 'to_member': 'megumi.fushiguro@gmail.com', 'jumlah': 10000, 'waktu': '2025-04-10 12:00:00', 'catatan': 'Uang jajan. Jangan bilang-bilang Gojo.'},
    {'id': 8, 'from_member': 'kento.nanami@gmail.com', 'to_member': 'yuji.itadori@gmail.com', 'jumlah': 800, 'waktu': '2025-04-15 17:30:00', 'catatan': 'Bonus lembur misi minggu lalu. Kerja bagus.'},
    {'id': 9, 'from_member': 'judy.hopps@yahoo.com', 'to_member': 'nick.wilde@yahoo.com', 'jumlah': 75, 'waktu': '2025-05-12 13:20:00', 'catatan': 'Patungan beli Jumbo-pop untuk Pawpsicles'},
    {'id': 10, 'from_member': 'strawberry.shortcake@gmail.com', 'to_member': 'blueberry.muffin@gmail.com', 'jumlah': 200, 'waktu': '2025-05-20 10:10:00', 'catatan': 'Beli bahan baku tambahan untuk toko kue'},
    {'id': 11, 'from_member': 'twilight.sparkle@yahoo.com', 'to_member': 'pinkie.pie@yahoo.com', 'jumlah': 500, 'waktu': '2025-06-01 15:00:00', 'catatan': 'Modal untuk dekorasi pesta kejutan Applejack'},
    {'id': 12, 'from_member': 'mike.wheeler@gmail.com', 'to_member': 'will.byers@gmail.com', 'jumlah': 60, 'waktu': '2025-07-04 20:00:00', 'catatan': 'Beli dadu 20-sisi yang baru untuk kampanye D&D'},
    {'id': 13, 'from_member': 'dustin.henderson@gmail.com', 'to_member': 'steve.harrington@gmail.com', 'jumlah': 35, 'waktu': '2025-07-10 21:30:00', 'catatan': 'Uang bensin karena sudah antar jemput malam ini'},
    {'id': 14, 'from_member': 'lucas.sinclair@gmail.com', 'to_member': 'max.mayfield@gmail.com', 'jumlah': 100, 'waktu': '2025-08-15 18:00:00', 'catatan': 'Kalah taruhan main Dig Dug di Arcade'},
    {'id': 15, 'from_member': 'larajean.songcovey@ui.ac.id', 'to_member': 'peter.kavinsky@ui.ac.id', 'jumlah': 45, 'waktu': '2025-09-05 16:20:00', 'catatan': 'Uang bensin untuk perjalanan ke kampus'},
    {'id': 16, 'from_member': 'kitty.songcovey@ui.ac.id', 'to_member': 'margot.songcovey@ui.ac.id', 'jumlah': 150, 'waktu': '2025-09-10 09:00:00', 'catatan': 'Kirim uang jajan dari rumah'},
    {'id': 17, 'from_member': 'josh.sanderson@ui.ac.id', 'to_member': 'margot.songcovey@ui.ac.id', 'jumlah': 300, 'waktu': '2025-10-01 12:00:00', 'catatan': 'Kado kecil untuk ulang tahunmu. Miss you!'},
]

# Redeem Transactions
REDEEM_DATA = [
    {'id': 1, 'email_member': 'tony.stark@gmail.com', 'kode_hadiah': 'RWD-007', 'waktu': '2025-08-15 10:00:00'},
    {'id': 2, 'email_member': 'tony.stark@gmail.com', 'kode_hadiah': 'RWD-005', 'waktu': '2025-10-20 14:30:00'},
    {'id': 3, 'email_member': 'tony.stark@gmail.com', 'kode_hadiah': 'RWD-010', 'waktu': '2025-12-01 09:15:00'},
    {'id': 4, 'email_member': 'steve.rogers@gmail.com', 'kode_hadiah': 'RWD-009', 'waktu': '2025-03-10 08:45:00'},
    {'id': 5, 'email_member': 'steve.rogers@gmail.com', 'kode_hadiah': 'RWD-011', 'waktu': '2025-05-12 11:20:00'},
    {'id': 6, 'email_member': 'satoru.gojo@gmail.com', 'kode_hadiah': 'RWD-005', 'waktu': '2025-06-15 16:00:00'},
    {'id': 7, 'email_member': 'satoru.gojo@gmail.com', 'kode_hadiah': 'RWD-008', 'waktu': '2025-07-22 19:30:00'},
    {'id': 8, 'email_member': 'natasha.romanoff@gmail.com', 'kode_hadiah': 'RWD-012', 'waktu': '2025-07-05 13:10:00'},
    {'id': 9, 'email_member': 'wanda.maximoff@gmail.com', 'kode_hadiah': 'RWD-008', 'waktu': '2025-02-14 20:00:00'},
    {'id': 10, 'email_member': 'megumi.fushiguro@gmail.com', 'kode_hadiah': 'RWD-002', 'waktu': '2025-04-10 18:00:00'},
    {'id': 11, 'email_member': 'yuji.itadori@gmail.com', 'kode_hadiah': 'RWD-003', 'waktu': '2025-05-01 10:30:00'},
    {'id': 12, 'email_member': 'nobara.kugisaki@gmail.com', 'kode_hadiah': 'RWD-004', 'waktu': '2025-02-28 15:45:00'},
    {'id': 13, 'email_member': 'kento.nanami@gmail.com', 'kode_hadiah': 'RWD-001', 'waktu': '2025-01-15 07:30:00'},
    {'id': 14, 'email_member': 'shoko.ieiri@gmail.com', 'kode_hadiah': 'RWD-012', 'waktu': '2025-09-09 17:00:00'},
    {'id': 15, 'email_member': 'larajean.songcovey@ui.ac.id', 'kode_hadiah': 'RWD-004', 'waktu': '2025-03-20 16:15:00'},
    {'id': 16, 'email_member': 'peter.kavinsky@ui.ac.id', 'kode_hadiah': 'RWD-006', 'waktu': '2025-04-05 09:00:00'},
    {'id': 17, 'email_member': 'kitty.songcovey@ui.ac.id', 'kode_hadiah': 'RWD-002', 'waktu': '2025-06-30 19:00:00'},
    {'id': 18, 'email_member': 'mike.wheeler@gmail.com', 'kode_hadiah': 'RWD-003', 'waktu': '2025-08-01 14:20:00'},
    {'id': 19, 'email_member': 'dustin.henderson@gmail.com', 'kode_hadiah': 'RWD-001', 'waktu': '2025-08-02 15:10:00'},
    {'id': 20, 'email_member': 'max.mayfield@gmail.com', 'kode_hadiah': 'RWD-002', 'waktu': '2025-08-10 20:30:00'},
    {'id': 21, 'email_member': 'jane.hopper@gmail.com', 'kode_hadiah': 'RWD-006', 'waktu': '2025-11-11 11:11:00'},
    {'id': 22, 'email_member': 'twilight.sparkle@yahoo.com', 'kode_hadiah': 'RWD-002', 'waktu': '2025-05-20 18:45:00'},
    {'id': 23, 'email_member': 'pinkie.pie@yahoo.com', 'kode_hadiah': 'RWD-006', 'waktu': '2025-06-05 10:00:00'},
    {'id': 24, 'email_member': 'judy.hopps@yahoo.com', 'kode_hadiah': 'RWD-001', 'waktu': '2025-03-15 08:30:00'},
    {'id': 25, 'email_member': 'strawberry.shortcake@gmail.com', 'kode_hadiah': 'RWD-004', 'waktu': '2025-02-10 16:00:00'},
]

# Member Award Miles Package Purchase
PACKAGE_PURCHASE_DATA = [
    {'id': 1, 'id_package': 'AMP-001', 'email_member': 'strawberry.shortcake@gmail.com', 'waktu': '2024-01-15 10:30:00'},
    {'id': 2, 'id_package': 'AMP-002', 'email_member': 'blueberry.muffin@gmail.com', 'waktu': '2024-01-20 14:15:00'},
    {'id': 3, 'id_package': 'AMP-003', 'email_member': 'orange.blossom@gmail.com', 'waktu': '2024-02-05 09:00:00'},
    {'id': 4, 'id_package': 'AMP-001', 'email_member': 'judy.hopps@yahoo.com', 'waktu': '2024-02-14 16:45:00'},
    {'id': 5, 'id_package': 'AMP-004', 'email_member': 'nick.wilde@yahoo.com', 'waktu': '2024-03-01 11:20:00'},
    {'id': 6, 'id_package': 'AMP-005', 'email_member': 'choso.kamo@gmail.com', 'waktu': '2024-03-10 08:30:00'},
    {'id': 7, 'id_package': 'AMP-002', 'email_member': 'yuji.itadori@gmail.com', 'waktu': '2024-03-25 13:10:00'},
    {'id': 8, 'id_package': 'AMP-003', 'email_member': 'megumi.fushiguro@gmail.com', 'waktu': '2024-04-02 15:55:00'},
    {'id': 9, 'id_package': 'AMP-001', 'email_member': 'will.byers@gmail.com', 'waktu': '2024-04-18 10:05:00'},
    {'id': 10, 'id_package': 'AMP-004', 'email_member': 'peter.parker@gmail.com', 'waktu': '2024-05-01 12:00:00'},
    {'id': 11, 'id_package': 'AMP-005', 'email_member': 'suguru.geto@gmail.com', 'waktu': '2024-05-12 14:40:00'},
    {'id': 12, 'id_package': 'AMP-002', 'email_member': 'kento.nanami@gmail.com', 'waktu': '2024-05-20 09:25:00'},
    {'id': 13, 'id_package': 'AMP-003', 'email_member': 'shoko.ieiri@gmail.com', 'waktu': '2024-06-05 16:15:00'},
    {'id': 14, 'id_package': 'AMP-001', 'email_member': 'rainbow.dash@yahoo.com', 'waktu': '2024-06-15 11:50:00'},
    {'id': 15, 'id_package': 'AMP-004', 'email_member': 'nancy.wheeler@gmail.com', 'waktu': '2024-07-01 10:10:00'},
    {'id': 16, 'id_package': 'AMP-005', 'email_member': 'satoru.gojo@gmail.com', 'waktu': '2024-07-10 13:35:00'},
    {'id': 17, 'id_package': 'AMP-002', 'email_member': 'bruce.banner@gmail.com', 'waktu': '2024-08-05 08:45:00'},
    {'id': 18, 'id_package': 'AMP-003', 'email_member': 'wanda.maximoff@gmail.com', 'waktu': '2024-08-20 15:20:00'},
    {'id': 19, 'id_package': 'AMP-001', 'email_member': 'tony.stark@gmail.com', 'waktu': '2024-09-01 11:00:00'},
    {'id': 20, 'id_package': 'AMP-005', 'email_member': 'steve.rogers@gmail.com', 'waktu': '2024-09-15 14:30:00'},
]

# Approved Missing Miles Claims (these cannot be deleted)
APPROVED_CLAIMS_DATA = [
    {'id': 1, 'email_member': 'tony.stark@gmail.com', 'jumlah': 500, 'waktu': '2025-03-01 10:00:00', 'alasan': 'Missing miles dari flight TX123'},
    {'id': 2, 'email_member': 'steve.rogers@gmail.com', 'jumlah': 1000, 'waktu': '2025-04-15 14:30:00', 'alasan': 'Sistem error pada transfer miles'},
    {'id': 3, 'email_member': 'satoru.gojo@gmail.com', 'jumlah': 300, 'waktu': '2025-05-20 09:00:00', 'alasan': 'Miles tidak terakumulasi dari transaksi'},
]


def get_hadiah_name(kode):
    """Get hadiah name by code"""
    for hadiah in HADIAH_DATA:
        if hadiah['kode'] == kode:
            return hadiah['nama']
    return 'Unknown'


def get_hadiah_miles(kode):
    """Get hadiah miles by code"""
    for hadiah in HADIAH_DATA:
        if hadiah['kode'] == kode:
            return hadiah['miles']
    return 0


def get_package_data(id_package):
    """Get package data by ID"""
    for pkg in AWARD_MILES_PACKAGES:
        if pkg['id'] == id_package:
            return pkg
    return None


def get_member_name(email):
    """Get member name by email"""
    return MEMBERS.get(email, {}).get('name', 'Unknown')


def build_all_transactions():
    """Build combined list of all transactions"""
    transactions = []
    
    # Add transfers
    for transfer in TRANSFER_DATA:
        transactions.append({
            'id': f"TRANS-{transfer['id']}",
            'type': 'Transfer',
            'from_member': transfer['from_member'],
            'from_member_name': get_member_name(transfer['from_member']),
            'to_member': transfer['to_member'],
            'to_member_name': get_member_name(transfer['to_member']),
            'member': f"{get_member_name(transfer['from_member'])} → {get_member_name(transfer['to_member'])}",
            'jumlah': transfer['jumlah'],
            'waktu': transfer['waktu'],
            'catatan': transfer.get('catatan', ''),
            'deletable': True,
            'sort_date': transfer['waktu'],
        })
    
    # Add redeems
    for redeem in REDEEM_DATA:
        transactions.append({
            'id': f"REDEEM-{redeem['id']}",
            'type': 'Redeem',
            'email_member': redeem['email_member'],
            'member_name': get_member_name(redeem['email_member']),
            'member': get_member_name(redeem['email_member']),
            'kode_hadiah': redeem['kode_hadiah'],
            'hadiah_name': get_hadiah_name(redeem['kode_hadiah']),
            'jumlah': get_hadiah_miles(redeem['kode_hadiah']),
            'waktu': redeem['waktu'],
            'deletable': True,
            'sort_date': redeem['waktu'],
        })
    
    # Add package purchases
    for purchase in PACKAGE_PURCHASE_DATA:
        pkg = get_package_data(purchase['id_package'])
        if pkg:
            transactions.append({
                'id': f"PACKAGE-{purchase['id']}",
                'type': 'Pembelian Package',
                'email_member': purchase['email_member'],
                'member_name': get_member_name(purchase['email_member']),
                'member': get_member_name(purchase['email_member']),
                'package_id': purchase['id_package'],
                'jumlah': pkg['jumlah_award_miles'],
                'harga': pkg['harga_paket'],
                'waktu': purchase['waktu'],
                'deletable': False,
                'sort_date': purchase['waktu'],
            })
    
    # Add approved claims
    for claim in APPROVED_CLAIMS_DATA:
        transactions.append({
            'id': f"CLAIM-{claim['id']}",
            'type': 'Klaim Disetujui',
            'email_member': claim['email_member'],
            'member_name': get_member_name(claim['email_member']),
            'member': get_member_name(claim['email_member']),
            'jumlah': claim['jumlah'],
            'waktu': claim['waktu'],
            'alasan': claim['alasan'],
            'deletable': False,
            'sort_date': claim['waktu'],
        })
    
    # Sort by date descending
    transactions.sort(key=lambda x: x['sort_date'], reverse=True)
    return transactions


@require_http_methods(["GET"])
def laporan_transaksi(request):
    """Display transaction report dashboard"""
    all_transactions = build_all_transactions()
    
    # Apply filters
    filter_type = request.GET.get('filter_type', 'all')
    filter_member = request.GET.get('filter_member', 'all')
    filter_date_from = request.GET.get('filter_date_from', '')
    filter_date_to = request.GET.get('filter_date_to', '')
    
    filtered_transactions = all_transactions.copy()
    
    # Filter by type
    if filter_type != 'all':
        filtered_transactions = [t for t in filtered_transactions if t['type'] == filter_type]
    
    # Filter by member
    if filter_member != 'all':
        filtered_transactions = [t for t in filtered_transactions if t.get('member_name') == filter_member or t.get('from_member') == filter_member or t.get('to_member') == filter_member]
    
    # Filter by date range
    if filter_date_from or filter_date_to:
        filtered_transactions_by_date = []
        for t in filtered_transactions:
            trans_date = datetime.strptime(t['waktu'], '%Y-%m-%d %H:%M:%S')
            if filter_date_from:
                from_date = datetime.strptime(filter_date_from + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
                if trans_date < from_date:
                    continue
            if filter_date_to:
                to_date = datetime.strptime(filter_date_to + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
                if trans_date > to_date:
                    continue
            filtered_transactions_by_date.append(t)
        filtered_transactions = filtered_transactions_by_date
    
    # Calculate statistics
    total_transfer = sum(t['jumlah'] for t in all_transactions if t['type'] == 'Transfer')
    total_redeem = sum(t['jumlah'] for t in all_transactions if t['type'] == 'Redeem')
    total_package = sum(t['jumlah'] for t in all_transactions if t['type'] == 'Pembelian Package')
    total_claims = sum(t['jumlah'] for t in all_transactions if t['type'] == 'Klaim Disetujui')
    
    # Calculate current month redeems
    current_date = datetime(2026, 4, 30)  # Current date as per context
    month_start = datetime(current_date.year, current_date.month, 1)
    month_end = datetime(current_date.year, current_date.month + 1 if current_date.month < 12 else 1, 1) if current_date.month < 12 else datetime(current_date.year + 1, 1, 1)
    
    month_redeems = 0
    for t in all_transactions:
        if t['type'] == 'Redeem':
            trans_date = datetime.strptime(t['waktu'], '%Y-%m-%d %H:%M:%S')
            if month_start <= trans_date < month_end:
                month_redeems += t['jumlah']
    
    # Get unique members for dropdown
    unique_members = sorted(set([get_member_name(email) for email in MEMBERS.keys()]))
    transaction_types = ['Transfer', 'Redeem', 'Pembelian Package', 'Klaim Disetujui']
    
    # Calculate top members by total miles
    member_miles = defaultdict(int)
    for t in all_transactions:
        if t['type'] in ['Redeem', 'Pembelian Package', 'Klaim Disetujui']:
            member_miles[t['member_name']] += t['jumlah']
    
    top_members = sorted(member_miles.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Calculate most active members in transfer & redeem
    member_activity = defaultdict(int)
    for t in all_transactions:
        if t['type'] in ['Transfer', 'Redeem']:
            if t['type'] == 'Transfer':
                member_activity[t['from_member_name']] += 1
                member_activity[t['to_member_name']] += 1
            else:
                member_activity[t['member_name']] += 1
    
    active_members = sorted(member_activity.items(), key=lambda x: x[1], reverse=True)[:10]
    
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
        'total_redeem': total_redeem,
        'total_package': total_package,
        'total_claims': total_claims,
        'total_miles': total_transfer + total_redeem + total_package + total_claims,
        'month_redeems': month_redeems,
        'top_members': top_members,
        'active_members': active_members,
        'view_type': request.GET.get('view_type', 'transactions'),
    }
    
    return render(request, 'laporan_transaksi.html', context)


@require_http_methods(["POST"])
def delete_transaction(request):
    """Delete transaction (only allowed for Transfer and Redeem)"""
    transaction_id = request.POST.get('transaction_id', '')
    
    # Verify transaction is deletable (would normally check database)
    # For mockup, only allow deletion of Transfer and Redeem transactions
    if not transaction_id.startswith(('TRANS-', 'REDEEM-')):
        messages.error(request, 'Riwayat klaim yang sudah disetujui tidak dapat dihapus.')
    else:
        messages.success(request, f'Riwayat transaksi {transaction_id} berhasil dihapus.')
    
    return redirect('staf:laporan_transaksi')

