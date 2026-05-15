from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.db import connection
import datetime

app_name = 'members'

# Tier benefits
TIER_BENEFITS = {
    'TIR-BLU': [
        {'icon': '🎫', 'text': 'Akumulasi miles dari setiap penerbangan'},
        {'icon': '📱', 'text': 'Akses aplikasi mobile AeroMiles'},
        {'icon': '📧', 'text': 'Notifikasi promosi dan penawaran khusus'},
    ],
    'TIR-SLV': [
        {'icon': '🎫', 'text': '+10% bonus miles setiap penerbangan'},
        {'icon': '🛫', 'text': 'Prioritas boarding dan check-in'},
        {'icon': '🏨', 'text': 'Diskon 10% hotel partner AeroMiles'},
        {'icon': '💳', 'text': 'Status elite di maskapai partner'},
    ],
    'TIR-GLD': [
        {'icon': '🎫', 'text': '+25% bonus miles setiap penerbangan'},
        {'icon': '🛫', 'text': 'Prioritas boarding dan seat selection'},
        {'icon': '🎁', 'text': 'Upgrade gratis ke business class'},
        {'icon': '🏨', 'text': 'Diskon 20% hotel dan restoran partner'},
        {'icon': '🎫', 'text': '2 free miles voucher per tahun'},
    ],
    'TIR-PLT': [
        {'icon': '🎫', 'text': '+50% bonus miles setiap penerbangan'},
        {'icon': '🛫', 'text': 'Priority boarding & premium lounge access'},
        {'icon': '🎁', 'text': 'Unlimited upgrade ke business class'},
        {'icon': '🏨', 'text': 'Diskon 30% hotel dan restoran partner'},
        {'icon': '🎫', 'text': '5 free miles voucher per tahun'},
        {'icon': '👥', 'text': 'Dedicated concierge service'},
    ],
}


def dictfetchall(cursor):
    """Convert database rows to list of dicts"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def dictfetchone(cursor):
    """Convert single database row to dict"""
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    return dict(zip(columns, row)) if row else None


def get_tier_info_from_db():
    """Fetch all tiers from database"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id_tier, nama, minimal_frekuensi_terbang, minimal_tier_miles
                FROM TIER
                ORDER BY minimal_tier_miles ASC
            """)
            tiers = dictfetchall(cursor)
            
            # Add benefits from hardcoded dictionary
            for tier in tiers:
                tier['benefits'] = TIER_BENEFITS.get(tier['id_tier'], [])
                tier['id'] = tier['id_tier']  # Add 'id' alias for compatibility
            
            return tiers
    except Exception:
        return []


def get_tier_info_for_member(email):
    """Calculate tier information for a specific member including next tier and miles needed"""
    try:
        # Fetch member data
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT nomor_member, id_tier, award_miles, total_miles
                FROM MEMBER
                WHERE email = %s
            """, [email])
            member_data = dictfetchone(cursor)
        
        if not member_data:
            return None, None
        
        current_tier_id = member_data['id_tier']
        current_miles = member_data['total_miles']
        current_flights = member_data['award_miles']
        
        # Fetch member name
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT salutation, first_mid_name, last_name
                FROM PENGGUNA
                WHERE email = %s
            """, [email])
            user_data = dictfetchone(cursor)
        
        name = f"{user_data['salutation']} {user_data['first_mid_name']} {user_data['last_name']}" if user_data else "Member"
        
        # Get all tiers
        tiers = get_tier_info_from_db()
        
        # Add calculated fields
        enriched_tiers = []
        for i, tier in enumerate(tiers):
            tier_info = tier.copy()
            tier_info['is_current'] = (tier['id_tier'] == current_tier_id)
            
            # Calculate miles needed to reach next tier
            if i < len(tiers) - 1:
                next_tier = tiers[i + 1]
                miles_needed_for_next = next_tier['minimal_tier_miles'] - current_miles
                tier_info['miles_to_next'] = max(0, miles_needed_for_next)
                tier_info['next_tier_name'] = next_tier['nama']
                
                # Calculate progress percentage for current tier
                if tier_info['is_current']:
                    current_tier_min_miles = tier['minimal_tier_miles']
                    next_tier_min_miles = next_tier['minimal_tier_miles']
                    miles_in_range = next_tier_min_miles - current_tier_min_miles
                    miles_since_current = current_miles - current_tier_min_miles
                    progress_percentage = int((miles_since_current / miles_in_range) * 100) if miles_in_range > 0 else 0
                    tier_info['progress_percentage'] = min(progress_percentage, 100)
                else:
                    tier_info['progress_percentage'] = 0
            else:
                tier_info['miles_to_next'] = None
                tier_info['next_tier_name'] = None
                tier_info['progress_percentage'] = 0 if not tier_info['is_current'] else 100
            
            enriched_tiers.append(tier_info)
        
        member = {
            'name': name,
            'current_miles': current_miles,
            'current_flights': current_flights,
        }
        
        return enriched_tiers, member
    except Exception:
        return None, None


@require_http_methods(["GET"])
def tier_info(request):
    """Display tier information and current member tier"""
    email = request.session.get('email')
    
    if not email:
        context = {'tiers': [], 'member': None}
        return render(request, 'tier_info.html', context)
    
    tiers, member = get_tier_info_for_member(email)
    
    if tiers is None:
        # Fallback to showing all tiers without member-specific data
        tiers = get_tier_info_from_db()
        member = None
    
    context = {
        'tiers': tiers or [],
        'member': member or {},
    }
    
    return render(request, 'tier_info.html', context)
from django.shortcuts import redirect, render
import datetime

BULAN_ID = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Ags', 'Sep', 'Okt', 'Nov', 'Des']

def _fmt_tanggal(iso_str):
    try:
        if isinstance(iso_str, datetime.date):
            d = iso_str
        else:
            d = datetime.date.fromisoformat(iso_str)
        return f"{d.day:02d} {BULAN_ID[d.month]} {d.year}"
    except Exception:
        return iso_str

DUMMY_TIER = {
    'TIR-BLU': 'Blue',
    'TIR-SLV': 'Silver',
    'TIR-GLD': 'Gold',
    'TIR-PLT': 'Platinum',
}

def _nama(p):
    return f"{p['salutation']} {p['first_mid_name']} {p['last_name']}"

MEMBERS_LIST = [
    {'nomor_member': 'M0001', 'email': 'strawberry.shortcake@gmail.com', 'salutation': 'Ms.', 'first_mid_name': 'Strawberry', 'last_name': 'Shortcake', 'id_tier': 'TIR-BLU', 'award_miles': 1200, 'total_miles': 3500, 'tanggal_bergabung': '2023-01-10', 'country_code': '+1', 'mobile_number': '5551901615', 'tanggal_lahir': '1990-06-15', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0002', 'email': 'blueberry.muffin@gmail.com', 'salutation': 'Ms.', 'first_mid_name': 'Blueberry', 'last_name': 'Muffin', 'id_tier': 'TIR-BLU', 'award_miles': 800, 'total_miles': 2100, 'tanggal_bergabung': '2023-02-14', 'country_code': '+1', 'mobile_number': '5551912320', 'tanggal_lahir': '1991-03-20', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0003', 'email': 'orange.blossom@gmail.com', 'salutation': 'Ms.', 'first_mid_name': 'Orange', 'last_name': 'Blossom', 'id_tier': 'TIR-BLU', 'award_miles': 2300, 'total_miles': 4800, 'tanggal_bergabung': '2023-03-22', 'country_code': '+1', 'mobile_number': '5551891005', 'tanggal_lahir': '1989-10-05', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0004', 'email': 'lemon.merringue@gmail.com', 'salutation': 'Ms.', 'first_mid_name': 'Lemon', 'last_name': 'Merringue', 'id_tier': 'TIR-BLU', 'award_miles': 500, 'total_miles': 1500, 'tanggal_bergabung': '2023-04-05', 'country_code': '+1', 'mobile_number': '5551920722', 'tanggal_lahir': '1992-07-22', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0005', 'email': 'plum.pudding@gmail.com', 'salutation': 'Mr.', 'first_mid_name': 'Plum', 'last_name': 'Pudding', 'id_tier': 'TIR-BLU', 'award_miles': 3100, 'total_miles': 6200, 'tanggal_bergabung': '2023-05-18', 'country_code': '+1', 'mobile_number': '5551881201', 'tanggal_lahir': '1988-12-01', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0006', 'email': 'cherry.jam@gmail.com', 'salutation': 'Ms.', 'first_mid_name': 'Cherry', 'last_name': 'Jam', 'id_tier': 'TIR-BLU', 'award_miles': 1750, 'total_miles': 4100, 'tanggal_bergabung': '2023-06-30', 'country_code': '+1', 'mobile_number': '5551930430', 'tanggal_lahir': '1993-04-30', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0007', 'email': 'raspberry.torte@gmail.com', 'salutation': 'Ms.', 'first_mid_name': 'Raspberry', 'last_name': 'Torte', 'id_tier': 'TIR-BLU', 'award_miles': 950, 'total_miles': 2700, 'tanggal_bergabung': '2023-07-11', 'country_code': '+1', 'mobile_number': '5551900914', 'tanggal_lahir': '1990-09-14', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0008', 'email': 'judy.hopps@yahoo.com', 'salutation': 'Ms.', 'first_mid_name': 'Judy', 'last_name': 'Hopps', 'id_tier': 'TIR-BLU', 'award_miles': 2600, 'total_miles': 5500, 'tanggal_bergabung': '2023-08-19', 'country_code': '+1', 'mobile_number': '5554941103', 'tanggal_lahir': '1994-11-03', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0009', 'email': 'nick.wilde@yahoo.com', 'salutation': 'Mr.', 'first_mid_name': 'Nick', 'last_name': 'Wilde', 'id_tier': 'TIR-BLU', 'award_miles': 1400, 'total_miles': 3800, 'tanggal_bergabung': '2023-09-03', 'country_code': '+1', 'mobile_number': '5558560622', 'tanggal_lahir': '1985-06-22', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0010', 'email': 'fru.fru@yahoo.com', 'salutation': 'Ms.', 'first_mid_name': 'Fru', 'last_name': 'Fru', 'id_tier': 'TIR-BLU', 'award_miles': 300, 'total_miles': 900, 'tanggal_bergabung': '2023-10-27', 'country_code': '+1', 'mobile_number': '5559960214', 'tanggal_lahir': '1996-02-14', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0011', 'email': 'pawbert.linxley@yahoo.com', 'salutation': 'Mr.', 'first_mid_name': 'Pawbert', 'last_name': 'Linxley', 'id_tier': 'TIR-BLU', 'award_miles': 4200, 'total_miles': 9800, 'tanggal_bergabung': '2023-11-14', 'country_code': '+1', 'mobile_number': '5558050519', 'tanggal_lahir': '1980-05-19', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0012', 'email': 'choso.kamo@gmail.com', 'salutation': 'Mr.', 'first_mid_name': 'Choso', 'last_name': 'Kamo', 'id_tier': 'TIR-BLU', 'award_miles': 3700, 'total_miles': 8300, 'tanggal_bergabung': '2023-12-01', 'country_code': '+81', 'mobile_number': '8031234001', 'tanggal_lahir': '1981-01-07', 'kewarganegaraan': 'Japanese'},
    {'nomor_member': 'M0013', 'email': 'hiromi.hiruguma@gmail.com', 'salutation': 'Mr.', 'first_mid_name': 'Hiromi', 'last_name': 'Hiruguma', 'id_tier': 'TIR-BLU', 'award_miles': 1100, 'total_miles': 2900, 'tanggal_bergabung': '2024-01-08', 'country_code': '+81', 'mobile_number': '8031234002', 'tanggal_lahir': '1999-08-15', 'kewarganegaraan': 'Japanese'},
    {'nomor_member': 'M0014', 'email': 'yuji.itadori@gmail.com', 'salutation': 'Mr.', 'first_mid_name': 'Yuji', 'last_name': 'Itadori', 'id_tier': 'TIR-BLU', 'award_miles': 2900, 'total_miles': 6700, 'tanggal_bergabung': '2024-02-22', 'country_code': '+81', 'mobile_number': '8031234003', 'tanggal_lahir': '2000-03-20', 'kewarganegaraan': 'Japanese'},
    {'nomor_member': 'M0015', 'email': 'megumi.fushiguro@gmail.com', 'salutation': 'Mr.', 'first_mid_name': 'Megumi', 'last_name': 'Fushiguro', 'id_tier': 'TIR-BLU', 'award_miles': 4800, 'total_miles': 11200, 'tanggal_bergabung': '2024-03-15', 'country_code': '+81', 'mobile_number': '8031234004', 'tanggal_lahir': '2000-12-22', 'kewarganegaraan': 'Japanese'},
    {'nomor_member': 'M0016', 'email': 'nobara.kugisaki@gmail.com', 'salutation': 'Ms.', 'first_mid_name': 'Nobara', 'last_name': 'Kugisaki', 'id_tier': 'TIR-BLU', 'award_miles': 3300, 'total_miles': 7600, 'tanggal_bergabung': '2024-04-09', 'country_code': '+81', 'mobile_number': '8031234005', 'tanggal_lahir': '2001-08-07', 'kewarganegaraan': 'Japanese'},
    {'nomor_member': 'M0017', 'email': 'will.byers@gmail.com', 'salutation': 'Mr.', 'first_mid_name': 'Will', 'last_name': 'Byers', 'id_tier': 'TIR-BLU', 'award_miles': 650, 'total_miles': 1800, 'tanggal_bergabung': '2024-05-20', 'country_code': '+1', 'mobile_number': '5557110322', 'tanggal_lahir': '1971-03-22', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0018', 'email': 'holly.wheeler@gmail.com', 'salutation': 'Ms.', 'first_mid_name': 'Holly', 'last_name': 'Wheeler', 'id_tier': 'TIR-BLU', 'award_miles': 200, 'total_miles': 600, 'tanggal_bergabung': '2024-06-11', 'country_code': '+1', 'mobile_number': '5558220719', 'tanggal_lahir': '1982-07-19', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0019', 'email': 'erica.sinclair@gmail.com', 'salutation': 'Ms.', 'first_mid_name': 'Erica', 'last_name': 'Sinclair', 'id_tier': 'TIR-BLU', 'award_miles': 1900, 'total_miles': 4400, 'tanggal_bergabung': '2024-07-04', 'country_code': '+1', 'mobile_number': '5557750702', 'tanggal_lahir': '1975-07-02', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0020', 'email': 'peter.parker@gmail.com', 'salutation': 'Mr.', 'first_mid_name': 'Peter', 'last_name': 'Parker', 'id_tier': 'TIR-BLU', 'award_miles': 4500, 'total_miles': 10500, 'tanggal_bergabung': '2024-08-30', 'country_code': '+1', 'mobile_number': '5552010810', 'tanggal_lahir': '2001-08-10', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0021', 'email': 'suguru.geto@gmail.com', 'salutation': 'Mr.', 'first_mid_name': 'Suguru', 'last_name': 'Geto', 'id_tier': 'TIR-SLV', 'award_miles': 8200, 'total_miles': 27000, 'tanggal_bergabung': '2022-03-01', 'country_code': '+81', 'mobile_number': '8031234007', 'tanggal_lahir': '1989-02-03', 'kewarganegaraan': 'Japanese'},
    {'nomor_member': 'M0022', 'email': 'toji.fushiguro@gmail.com', 'salutation': 'Mr.', 'first_mid_name': 'Toji', 'last_name': 'Fushiguro', 'id_tier': 'TIR-SLV', 'award_miles': 11500, 'total_miles': 33800, 'tanggal_bergabung': '2022-04-17', 'country_code': '+81', 'mobile_number': '8031234008', 'tanggal_lahir': '1971-03-01', 'kewarganegaraan': 'Japanese'},
    {'nomor_member': 'M0023', 'email': 'kento.nanami@gmail.com', 'salutation': 'Mr.', 'first_mid_name': 'Kento', 'last_name': 'Nanami', 'id_tier': 'TIR-SLV', 'award_miles': 9800, 'total_miles': 30200, 'tanggal_bergabung': '2022-05-29', 'country_code': '+81', 'mobile_number': '8031234009', 'tanggal_lahir': '1985-06-28', 'kewarganegaraan': 'Japanese'},
    {'nomor_member': 'M0024', 'email': 'shoko.ieiri@gmail.com', 'salutation': 'Dr.', 'first_mid_name': 'Shoko', 'last_name': 'Ieiri', 'id_tier': 'TIR-SLV', 'award_miles': 14300, 'total_miles': 41500, 'tanggal_bergabung': '2022-06-12', 'country_code': '+81', 'mobile_number': '8031234010', 'tanggal_lahir': '1989-09-05', 'kewarganegaraan': 'Japanese'},
    {'nomor_member': 'M0025', 'email': 'yuki.tsukumo@gmail.com', 'salutation': 'Ms.', 'first_mid_name': 'Yuki', 'last_name': 'Tsukumo', 'id_tier': 'TIR-SLV', 'award_miles': 12600, 'total_miles': 36900, 'tanggal_bergabung': '2022-07-25', 'country_code': '+81', 'mobile_number': '8031234011', 'tanggal_lahir': '1984-12-31', 'kewarganegaraan': 'Japanese'},
    {'nomor_member': 'M0026', 'email': 'yuta.okkotsu@gmail.com', 'salutation': 'Mr.', 'first_mid_name': 'Yuta', 'last_name': 'Okkotsu', 'id_tier': 'TIR-SLV', 'award_miles': 7700, 'total_miles': 25400, 'tanggal_bergabung': '2022-08-08', 'country_code': '+81', 'mobile_number': '8031234012', 'tanggal_lahir': '2000-03-07', 'kewarganegaraan': 'Japanese'},
    {'nomor_member': 'M0027', 'email': 'maki.zenin@gmail.com', 'salutation': 'Ms.', 'first_mid_name': 'Maki', 'last_name': 'Zenin', 'id_tier': 'TIR-SLV', 'award_miles': 10100, 'total_miles': 31700, 'tanggal_bergabung': '2022-09-19', 'country_code': '+81', 'mobile_number': '8031234013', 'tanggal_lahir': '2001-01-20', 'kewarganegaraan': 'Japanese'},
    {'nomor_member': 'M0028', 'email': 'twilight.sparkle@yahoo.com', 'salutation': 'Ms.', 'first_mid_name': 'Twilight', 'last_name': 'Sparkle', 'id_tier': 'TIR-SLV', 'award_miles': 13800, 'total_miles': 39200, 'tanggal_bergabung': '2022-10-31', 'country_code': '+1', 'mobile_number': '5551951022', 'tanggal_lahir': '1995-10-22', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0029', 'email': 'pinkie.pie@yahoo.com', 'salutation': 'Ms.', 'first_mid_name': 'Pinkie', 'last_name': 'Pie', 'id_tier': 'TIR-SLV', 'award_miles': 6900, 'total_miles': 26800, 'tanggal_bergabung': '2022-11-14', 'country_code': '+1', 'mobile_number': '5551960503', 'tanggal_lahir': '1996-05-03', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0030', 'email': 'rainbow.dash@yahoo.com', 'salutation': 'Ms.', 'first_mid_name': 'Rainbow', 'last_name': 'Dash', 'id_tier': 'TIR-SLV', 'award_miles': 15200, 'total_miles': 44700, 'tanggal_bergabung': '2022-12-02', 'country_code': '+1', 'mobile_number': '5551950401', 'tanggal_lahir': '1995-04-01', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0031', 'email': 'jonathan.byers@gmail.com', 'salutation': 'Mr.', 'first_mid_name': 'Jonathan', 'last_name': 'Byers', 'id_tier': 'TIR-SLV', 'award_miles': 8800, 'total_miles': 28500, 'tanggal_bergabung': '2023-01-25', 'country_code': '+1', 'mobile_number': '5556671201', 'tanggal_lahir': '1967-12-01', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0032', 'email': 'mike.wheeler@gmail.com', 'salutation': 'Mr.', 'first_mid_name': 'Mike', 'last_name': 'Wheeler', 'id_tier': 'TIR-SLV', 'award_miles': 9400, 'total_miles': 29900, 'tanggal_bergabung': '2023-02-17', 'country_code': '+1', 'mobile_number': '5557110407', 'tanggal_lahir': '1971-04-07', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0033', 'email': 'nancy.wheeler@gmail.com', 'salutation': 'Ms.', 'first_mid_name': 'Nancy', 'last_name': 'Wheeler', 'id_tier': 'TIR-SLV', 'award_miles': 11900, 'total_miles': 35600, 'tanggal_bergabung': '2023-03-08', 'country_code': '+1', 'mobile_number': '5556671114', 'tanggal_lahir': '1967-11-14', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0034', 'email': 'lucas.sinclair@gmail.com', 'salutation': 'Mr.', 'first_mid_name': 'Lucas', 'last_name': 'Sinclair', 'id_tier': 'TIR-SLV', 'award_miles': 13100, 'total_miles': 38300, 'tanggal_bergabung': '2023-04-20', 'country_code': '+1', 'mobile_number': '5557110601', 'tanggal_lahir': '1971-06-01', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0035', 'email': 'dustin.henderson@gmail.com', 'salutation': 'Mr.', 'first_mid_name': 'Dustin', 'last_name': 'Henderson', 'id_tier': 'TIR-SLV', 'award_miles': 7200, 'total_miles': 25100, 'tanggal_bergabung': '2023-05-05', 'country_code': '+1', 'mobile_number': '5557110110', 'tanggal_lahir': '1971-01-10', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0036', 'email': 'satoru.gojo@gmail.com', 'salutation': 'Mr.', 'first_mid_name': 'Satoru', 'last_name': 'Gojo', 'id_tier': 'TIR-GLD', 'award_miles': 28000, 'total_miles': 72000, 'tanggal_bergabung': '2021-01-15', 'country_code': '+81', 'mobile_number': '8031234006', 'tanggal_lahir': '1989-12-07', 'kewarganegaraan': 'Japanese'},
    {'nomor_member': 'M0037', 'email': 'bruce.banner@gmail.com', 'salutation': 'Dr.', 'first_mid_name': 'Bruce', 'last_name': 'Banner', 'id_tier': 'TIR-GLD', 'award_miles': 35500, 'total_miles': 89300, 'tanggal_bergabung': '2021-03-22', 'country_code': '+1', 'mobile_number': '5556911218', 'tanggal_lahir': '1969-12-18', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0038', 'email': 'natasha.romanoff@gmail.com', 'salutation': 'Ms.', 'first_mid_name': 'Natasha', 'last_name': 'Romanoff', 'id_tier': 'TIR-GLD', 'award_miles': 22800, 'total_miles': 61500, 'tanggal_bergabung': '2021-05-09', 'country_code': '+7', 'mobile_number': '9161234567', 'tanggal_lahir': '1984-11-22', 'kewarganegaraan': 'Russian'},
    {'nomor_member': 'M0039', 'email': 'wanda.maximoff@gmail.com', 'salutation': 'Ms.', 'first_mid_name': 'Wanda', 'last_name': 'Maximoff', 'id_tier': 'TIR-GLD', 'award_miles': 31200, 'total_miles': 79600, 'tanggal_bergabung': '2021-07-31', 'country_code': '+421', 'mobile_number': '9001234567', 'tanggal_lahir': '1989-02-10', 'kewarganegaraan': 'Sokovian'},
    {'nomor_member': 'M0040', 'email': 'scott.lang@gmail.com', 'salutation': 'Mr.', 'first_mid_name': 'Scott', 'last_name': 'Lang', 'id_tier': 'TIR-GLD', 'award_miles': 27600, 'total_miles': 70200, 'tanggal_bergabung': '2021-09-14', 'country_code': '+1', 'mobile_number': '5557240415', 'tanggal_lahir': '1972-04-15', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0041', 'email': 'steve.harrington@gmail.com', 'salutation': 'Mr.', 'first_mid_name': 'Steve', 'last_name': 'Harrington', 'id_tier': 'TIR-GLD', 'award_miles': 24100, 'total_miles': 63800, 'tanggal_bergabung': '2021-11-03', 'country_code': '+1', 'mobile_number': '5556660922', 'tanggal_lahir': '1966-09-22', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0042', 'email': 'max.mayfield@gmail.com', 'salutation': 'Ms.', 'first_mid_name': 'Max', 'last_name': 'Mayfield', 'id_tier': 'TIR-GLD', 'award_miles': 38900, 'total_miles': 96200, 'tanggal_bergabung': '2022-01-27', 'country_code': '+1', 'mobile_number': '5557110906', 'tanggal_lahir': '1971-09-06', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0043', 'email': 'jane.hopper@gmail.com', 'salutation': 'Ms.', 'first_mid_name': 'Jane', 'last_name': 'Hopper', 'id_tier': 'TIR-GLD', 'award_miles': 21500, 'total_miles': 57900, 'tanggal_bergabung': '2022-03-18', 'country_code': '+1', 'mobile_number': '5557111028', 'tanggal_lahir': '1971-10-28', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0044', 'email': 'larajean.songcovey@ui.ac.id', 'salutation': 'Ms.', 'first_mid_name': 'Lara Jean Song', 'last_name': 'Covey', 'id_tier': 'TIR-GLD', 'award_miles': 33700, 'total_miles': 85400, 'tanggal_bergabung': '2022-05-07', 'country_code': '+1', 'mobile_number': '5551990420', 'tanggal_lahir': '1999-04-20', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0045', 'email': 'margot.songcovey@ui.ac.id', 'salutation': 'Ms.', 'first_mid_name': 'Margot Song', 'last_name': 'Covey', 'id_tier': 'TIR-GLD', 'award_miles': 29400, 'total_miles': 75100, 'tanggal_bergabung': '2022-07-22', 'country_code': '+1', 'mobile_number': '7911234567', 'tanggal_lahir': '1997-08-12', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0046', 'email': 'tony.stark@gmail.com', 'salutation': 'Mr.', 'first_mid_name': 'Tony', 'last_name': 'Stark', 'id_tier': 'TIR-PLT', 'award_miles': 185000, 'total_miles': 420000, 'tanggal_bergabung': '2020-01-01', 'country_code': '+1', 'mobile_number': '5557000529', 'tanggal_lahir': '1970-05-29', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0047', 'email': 'steve.rogers@gmail.com', 'salutation': 'Mr.', 'first_mid_name': 'Steve', 'last_name': 'Rogers', 'id_tier': 'TIR-PLT', 'award_miles': 142000, 'total_miles': 310000, 'tanggal_bergabung': '2020-03-15', 'country_code': '+1', 'mobile_number': '5551180704', 'tanggal_lahir': '1918-07-04', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0048', 'email': 'kitty.songcovey@ui.ac.id', 'salutation': 'Ms.', 'first_mid_name': 'Kitty Song', 'last_name': 'Covey', 'id_tier': 'TIR-PLT', 'award_miles': 108500, 'total_miles': 235000, 'tanggal_bergabung': '2020-06-28', 'country_code': '+1', 'mobile_number': '5552030630', 'tanggal_lahir': '2003-06-30', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0049', 'email': 'peter.kavinsky@ui.ac.id', 'salutation': 'Mr.', 'first_mid_name': 'Peter', 'last_name': 'Kavinsky', 'id_tier': 'TIR-PLT', 'award_miles': 167300, 'total_miles': 380500, 'tanggal_bergabung': '2020-09-10', 'country_code': '+1', 'mobile_number': '5551990622', 'tanggal_lahir': '1999-06-22', 'kewarganegaraan': 'American'},
    {'nomor_member': 'M0050', 'email': 'josh.sanderson@ui.ac.id', 'salutation': 'Mr.', 'first_mid_name': 'Josh', 'last_name': 'Sanderson', 'id_tier': 'TIR-PLT', 'award_miles': 129800, 'total_miles': 275200, 'tanggal_bergabung': '2020-12-05', 'country_code': '+1', 'mobile_number': '5559940315', 'tanggal_lahir': '1994-03-15', 'kewarganegaraan': 'American'},
]

IDENTITAS_LIST = {
    'judy.hopps@yahoo.com': [
        {
            'nomor': 'US-KTP-008',
            'jenis': 'KTP',
            'negara_penerbit': 'United States',
            'tanggal_terbit': '2011-11-03',
            'tanggal_habis': '9999-12-31',
        },
    ],
}

def kelola_member(request):
    role = request.session.get('role')
    if role != 'staff':
        return redirect('main:dashboard')
    members = [
        {
            **m,
            'nama_lengkap': _nama(m),
            'tier': DUMMY_TIER.get(m['id_tier'], '-'),
            'tanggal_bergabung': _fmt_tanggal(m['tanggal_bergabung']),
        }
        for m in MEMBERS_LIST
    ]
    return render(request, 'kelola_member.html', {'members': members})

def tambah_member(request):
    if request.method == 'POST':
        pass
    return redirect('members:kelola_member')

def edit_member(request, nomor):
    if request.method == 'POST':
        pass
    return redirect('members:kelola_member')

def hapus_member(request, nomor):
    if request.method == 'POST':
        pass
    return redirect('members:kelola_member')

def _build_identitas(raw_list):
    today = datetime.date.today()
    result = []
    for item in raw_list:
        habis_iso = item['tanggal_habis']
        habis_date = datetime.date.fromisoformat(habis_iso)
        never_expires = habis_date >= datetime.date(9999, 12, 31)

        if never_expires:
            status = 'Aktif'
            status_class = 'badge-aktif'
            tanggal_habis_display = 'Tidak Kedaluwarsa'
        elif habis_date >= today:
            status = 'Aktif'
            status_class = 'badge-aktif'
            tanggal_habis_display = _fmt_tanggal(habis_iso)
        else:
            status = 'Kedaluwarsa'
            status_class = 'badge-kedaluwarsa'
            tanggal_habis_display = _fmt_tanggal(habis_iso)

        result.append({
            **item,
            'tanggal_terbit_display': _fmt_tanggal(item['tanggal_terbit']),
            'tanggal_habis_display': tanggal_habis_display,
            'status': status,
            'status_class': status_class,
        })
    return result

def identitas(request):
    if request.session.get('role') != 'member':
        return redirect('main:dashboard')
    email = request.session.get('email', '')
    raw = IDENTITAS_LIST.get(email, [])
    return render(request, 'identitas.html', {'identitas_list': _build_identitas(raw)})

def tambah_identitas(request):
    if request.method == 'POST':
        pass
    return redirect('members:identitas')

def edit_identitas(request, nomor):
    if request.method == 'POST':
        pass
    return redirect('members:identitas')

def hapus_identitas(request, nomor):
    if request.method == 'POST':
        pass
    return redirect('members:identitas')
