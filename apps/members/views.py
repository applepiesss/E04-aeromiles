from django.shortcuts import render
from django.views.decorators.http import require_http_methods

app_name = 'members'

# Hardcoded tier data
TIERS = [
    {
        'id': 'TIR-BLU',
        'nama': 'Blue',
        'minimal_frekuensi_terbang': 0,
        'minimal_tier_miles': 0,
        'benefits': [
            {'icon': '🎫', 'text': 'Akumulasi miles dari setiap penerbangan'},
            {'icon': '📱', 'text': 'Akses aplikasi mobile AeroMiles'},
            {'icon': '📧', 'text': 'Notifikasi promosi dan penawaran khusus'},
        ]
    },
    {
        'id': 'TIR-SLV',
        'nama': 'Silver',
        'minimal_frekuensi_terbang': 25,
        'minimal_tier_miles': 25000,
        'benefits': [
            {'icon': '🎫', 'text': '+10% bonus miles setiap penerbangan'},
            {'icon': '🛫', 'text': 'Prioritas boarding dan check-in'},
            {'icon': '🏨', 'text': 'Diskon 10% hotel partner AeroMiles'},
            {'icon': '💳', 'text': 'Status elite di maskapai partner'},
        ]
    },
    {
        'id': 'TIR-GLD',
        'nama': 'Gold',
        'minimal_frekuensi_terbang': 50,
        'minimal_tier_miles': 50000,
        'benefits': [
            {'icon': '🎫', 'text': '+25% bonus miles setiap penerbangan'},
            {'icon': '🛫', 'text': 'Prioritas boarding dan seat selection'},
            {'icon': '🎁', 'text': 'Upgrade gratis ke business class'},
            {'icon': '🏨', 'text': 'Diskon 20% hotel dan restoran partner'},
            {'icon': '🎫', 'text': '2 free miles voucher per tahun'},
        ]
    },
    {
        'id': 'TIR-PLT',
        'nama': 'Platinum',
        'minimal_frekuensi_terbang': 100,
        'minimal_tier_miles': 100000,
        'benefits': [
            {'icon': '🎫', 'text': '+50% bonus miles setiap penerbangan'},
            {'icon': '🛫', 'text': 'Priority boarding & premium lounge access'},
            {'icon': '🎁', 'text': 'Unlimited upgrade ke business class'},
            {'icon': '🏨', 'text': 'Diskon 30% hotel dan restoran partner'},
            {'icon': '🎫', 'text': '5 free miles voucher per tahun'},
            {'icon': '👥', 'text': 'Dedicated concierge service'},
        ]
    },
]

# Hardcoded current member tier status (sample data)
CURRENT_MEMBER_TIER = {
    'current_tier': 'TIR-SLV',  # Silver
    'current_miles': 45000,
    'current_flights': 40,
    'name': 'John Michael Doe',
}


def get_tier_info():
    """Calculate tier information including next tier and miles needed"""
    tiers = TIERS
    current_tier_id = CURRENT_MEMBER_TIER['current_tier']
    current_miles = CURRENT_MEMBER_TIER['current_miles']
    
    # Find index of current tier
    current_tier_idx = next((i for i, t in enumerate(tiers) if t['id'] == current_tier_id), 0)
    
    # Add calculated fields
    enriched_tiers = []
    for i, tier in enumerate(tiers):
        tier_info = tier.copy()
        tier_info['is_current'] = (tier['id'] == current_tier_id)
        
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
    
    return enriched_tiers

@require_http_methods(["GET"])
def tier_info(request):
    """Display tier information and current member tier"""
    tiers = get_tier_info()
    member = CURRENT_MEMBER_TIER.copy()
    
    context = {
        'tiers': tiers,
        'member': member,
    }
    
    return render(request, 'tier_info.html', context)
