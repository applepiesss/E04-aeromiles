from django.shortcuts import redirect, render
import datetime;

BULAN_ID = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun',
            'Jul', 'Ags', 'Sep', 'Okt', 'Nov', 'Des']

def _fmt_tanggal(iso_str):
    try:
        d = datetime.date.fromisoformat(iso_str)
        return f"{d.day:02d} {BULAN_ID[d.month]} {d.year}"
    except Exception:
        return iso_str

MEMBERS_LIST = [
    {'nomor_member':'M0001','email':'strawberry.shortcake@gmail.com','salutation':'Ms.','first_mid_name':'Strawberry','last_name':'Shortcake','nama_lengkap':'Ms. Strawberry Shortcake','id_tier':'TIR-BLU','tier':'Blue','award_miles':1200,'total_miles':3500,'tanggal_bergabung':'10 Jan 2023','country_code':'+1','mobile_number':'5551901615','tanggal_lahir_iso':'1990-06-15','kewarganegaraan':'American'},
    {'nomor_member':'M0002','email':'blueberry.muffin@gmail.com','salutation':'Ms.','first_mid_name':'Blueberry','last_name':'Muffin','nama_lengkap':'Ms. Blueberry Muffin','id_tier':'TIR-BLU','tier':'Blue','award_miles':800,'total_miles':2100,'tanggal_bergabung':'14 Feb 2023','country_code':'+1','mobile_number':'5551912320','tanggal_lahir_iso':'1991-03-20','kewarganegaraan':'American'},
    {'nomor_member':'M0003','email':'orange.blossom@gmail.com','salutation':'Ms.','first_mid_name':'Orange','last_name':'Blossom','nama_lengkap':'Ms. Orange Blossom','id_tier':'TIR-BLU','tier':'Blue','award_miles':2300,'total_miles':4800,'tanggal_bergabung':'22 Mar 2023','country_code':'+1','mobile_number':'5551891005','tanggal_lahir_iso':'1989-10-05','kewarganegaraan':'American'},
    {'nomor_member':'M0004','email':'lemon.merringue@gmail.com','salutation':'Ms.','first_mid_name':'Lemon','last_name':'Merringue','nama_lengkap':'Ms. Lemon Merringue','id_tier':'TIR-BLU','tier':'Blue','award_miles':500,'total_miles':1500,'tanggal_bergabung':'05 Apr 2023','country_code':'+1','mobile_number':'5551920722','tanggal_lahir_iso':'1992-07-22','kewarganegaraan':'American'},
    {'nomor_member':'M0005','email':'plum.pudding@gmail.com','salutation':'Mr.','first_mid_name':'Plum','last_name':'Pudding','nama_lengkap':'Mr. Plum Pudding','id_tier':'TIR-BLU','tier':'Blue','award_miles':3100,'total_miles':6200,'tanggal_bergabung':'18 Mei 2023','country_code':'+1','mobile_number':'5551881201','tanggal_lahir_iso':'1988-12-01','kewarganegaraan':'American'},
    {'nomor_member':'M0006','email':'cherry.jam@gmail.com','salutation':'Ms.','first_mid_name':'Cherry','last_name':'Jam','nama_lengkap':'Ms. Cherry Jam','id_tier':'TIR-BLU','tier':'Blue','award_miles':1750,'total_miles':4100,'tanggal_bergabung':'30 Jun 2023','country_code':'+1','mobile_number':'5551930430','tanggal_lahir_iso':'1993-04-30','kewarganegaraan':'American'},
    {'nomor_member':'M0007','email':'raspberry.torte@gmail.com','salutation':'Ms.','first_mid_name':'Raspberry','last_name':'Torte','nama_lengkap':'Ms. Raspberry Torte','id_tier':'TIR-BLU','tier':'Blue','award_miles':950,'total_miles':2700,'tanggal_bergabung':'11 Jul 2023','country_code':'+1','mobile_number':'5551900914','tanggal_lahir_iso':'1990-09-14','kewarganegaraan':'American'},
    {'nomor_member':'M0008','email':'judy.hopps@yahoo.com','salutation':'Ms.','first_mid_name':'Judy','last_name':'Hopps','nama_lengkap':'Ms. Judy Hopps','id_tier':'TIR-BLU','tier':'Blue','award_miles':2600,'total_miles':5500,'tanggal_bergabung':'19 Ags 2023','country_code':'+1','mobile_number':'5554941103','tanggal_lahir_iso':'1994-11-03','kewarganegaraan':'American'},
    {'nomor_member':'M0009','email':'nick.wilde@yahoo.com','salutation':'Mr.','first_mid_name':'Nick','last_name':'Wilde','nama_lengkap':'Mr. Nick Wilde','id_tier':'TIR-BLU','tier':'Blue','award_miles':1400,'total_miles':3800,'tanggal_bergabung':'03 Sep 2023','country_code':'+1','mobile_number':'5558560622','tanggal_lahir_iso':'1985-06-22','kewarganegaraan':'American'},
    {'nomor_member':'M0010','email':'fru.fru@yahoo.com','salutation':'Ms.','first_mid_name':'Fru','last_name':'Fru','nama_lengkap':'Ms. Fru Fru','id_tier':'TIR-BLU','tier':'Blue','award_miles':300,'total_miles':900,'tanggal_bergabung':'27 Okt 2023','country_code':'+1','mobile_number':'5559960214','tanggal_lahir_iso':'1996-02-14','kewarganegaraan':'American'},
    {'nomor_member':'M0011','email':'pawbert.linxley@yahoo.com','salutation':'Mr.','first_mid_name':'Pawbert','last_name':'Linxley','nama_lengkap':'Mr. Pawbert Linxley','id_tier':'TIR-BLU','tier':'Blue','award_miles':4200,'total_miles':9800,'tanggal_bergabung':'14 Nov 2023','country_code':'+1','mobile_number':'5558050519','tanggal_lahir_iso':'1980-05-19','kewarganegaraan':'American'},
    {'nomor_member':'M0012','email':'choso.kamo@gmail.com','salutation':'Mr.','first_mid_name':'Choso','last_name':'Kamo','nama_lengkap':'Mr. Choso Kamo','id_tier':'TIR-BLU','tier':'Blue','award_miles':3700,'total_miles':8300,'tanggal_bergabung':'01 Des 2023','country_code':'+81','mobile_number':'8031234001','tanggal_lahir_iso':'1981-01-07','kewarganegaraan':'Japanese'},
    {'nomor_member':'M0013','email':'hiromi.hiruguma@gmail.com','salutation':'Mr.','first_mid_name':'Hiromi','last_name':'Hiruguma','nama_lengkap':'Mr. Hiromi Hiruguma','id_tier':'TIR-BLU','tier':'Blue','award_miles':1100,'total_miles':2900,'tanggal_bergabung':'08 Jan 2024','country_code':'+81','mobile_number':'8031234002','tanggal_lahir_iso':'1999-08-15','kewarganegaraan':'Japanese'},
    {'nomor_member':'M0014','email':'yuji.itadori@gmail.com','salutation':'Mr.','first_mid_name':'Yuji','last_name':'Itadori','nama_lengkap':'Mr. Yuji Itadori','id_tier':'TIR-BLU','tier':'Blue','award_miles':2900,'total_miles':6700,'tanggal_bergabung':'22 Feb 2024','country_code':'+81','mobile_number':'8031234003','tanggal_lahir_iso':'2000-03-20','kewarganegaraan':'Japanese'},
    {'nomor_member':'M0015','email':'megumi.fushiguro@gmail.com','salutation':'Mr.','first_mid_name':'Megumi','last_name':'Fushiguro','nama_lengkap':'Mr. Megumi Fushiguro','id_tier':'TIR-BLU','tier':'Blue','award_miles':4800,'total_miles':11200,'tanggal_bergabung':'15 Mar 2024','country_code':'+81','mobile_number':'8031234004','tanggal_lahir_iso':'2000-12-22','kewarganegaraan':'Japanese'},
    {'nomor_member':'M0016','email':'nobara.kugisaki@gmail.com','salutation':'Ms.','first_mid_name':'Nobara','last_name':'Kugisaki','nama_lengkap':'Ms. Nobara Kugisaki','id_tier':'TIR-BLU','tier':'Blue','award_miles':3300,'total_miles':7600,'tanggal_bergabung':'09 Apr 2024','country_code':'+81','mobile_number':'8031234005','tanggal_lahir_iso':'2001-08-07','kewarganegaraan':'Japanese'},
    {'nomor_member':'M0017','email':'will.byers@gmail.com','salutation':'Mr.','first_mid_name':'Will','last_name':'Byers','nama_lengkap':'Mr. Will Byers','id_tier':'TIR-BLU','tier':'Blue','award_miles':650,'total_miles':1800,'tanggal_bergabung':'20 Mei 2024','country_code':'+1','mobile_number':'5557110322','tanggal_lahir_iso':'1971-03-22','kewarganegaraan':'American'},
    {'nomor_member':'M0018','email':'holly.wheeler@gmail.com','salutation':'Ms.','first_mid_name':'Holly','last_name':'Wheeler','nama_lengkap':'Ms. Holly Wheeler','id_tier':'TIR-BLU','tier':'Blue','award_miles':200,'total_miles':600,'tanggal_bergabung':'11 Jun 2024','country_code':'+1','mobile_number':'5558220719','tanggal_lahir_iso':'1982-07-19','kewarganegaraan':'American'},
    {'nomor_member':'M0019','email':'erica.sinclair@gmail.com','salutation':'Ms.','first_mid_name':'Erica','last_name':'Sinclair','nama_lengkap':'Ms. Erica Sinclair','id_tier':'TIR-BLU','tier':'Blue','award_miles':1900,'total_miles':4400,'tanggal_bergabung':'04 Jul 2024','country_code':'+1','mobile_number':'5557750702','tanggal_lahir_iso':'1975-07-02','kewarganegaraan':'American'},
    {'nomor_member':'M0020','email':'peter.parker@gmail.com','salutation':'Mr.','first_mid_name':'Peter','last_name':'Parker','nama_lengkap':'Mr. Peter Parker','id_tier':'TIR-BLU','tier':'Blue','award_miles':4500,'total_miles':10500,'tanggal_bergabung':'30 Ags 2024','country_code':'+1','mobile_number':'5552010810','tanggal_lahir_iso':'2001-08-10','kewarganegaraan':'American'},

    {'nomor_member':'M0021','email':'suguru.geto@gmail.com','salutation':'Mr.','first_mid_name':'Suguru','last_name':'Geto','nama_lengkap':'Mr. Suguru Geto','id_tier':'TIR-SLV','tier':'Silver','award_miles':8200,'total_miles':27000,'tanggal_bergabung':'01 Mar 2022','country_code':'+81','mobile_number':'8031234007','tanggal_lahir_iso':'1989-02-03','kewarganegaraan':'Japanese'},
    {'nomor_member':'M0022','email':'toji.fushiguro@gmail.com','salutation':'Mr.','first_mid_name':'Toji','last_name':'Fushiguro','nama_lengkap':'Mr. Toji Fushiguro','id_tier':'TIR-SLV','tier':'Silver','award_miles':11500,'total_miles':33800,'tanggal_bergabung':'17 Apr 2022','country_code':'+81','mobile_number':'8031234008','tanggal_lahir_iso':'1971-03-01','kewarganegaraan':'Japanese'},
    {'nomor_member':'M0023','email':'kento.nanami@gmail.com','salutation':'Mr.','first_mid_name':'Kento','last_name':'Nanami','nama_lengkap':'Mr. Kento Nanami','id_tier':'TIR-SLV','tier':'Silver','award_miles':9800,'total_miles':30200,'tanggal_bergabung':'29 Mei 2022','country_code':'+81','mobile_number':'8031234009','tanggal_lahir_iso':'1985-06-28','kewarganegaraan':'Japanese'},
    {'nomor_member':'M0024','email':'shoko.ieiri@gmail.com','salutation':'Dr.','first_mid_name':'Shoko','last_name':'Ieiri','nama_lengkap':'Dr. Shoko Ieiri','id_tier':'TIR-SLV','tier':'Silver','award_miles':14300,'total_miles':41500,'tanggal_bergabung':'12 Jun 2022','country_code':'+81','mobile_number':'8031234010','tanggal_lahir_iso':'1989-09-05','kewarganegaraan':'Japanese'},
    {'nomor_member':'M0025','email':'yuki.tsukumo@gmail.com','salutation':'Ms.','first_mid_name':'Yuki','last_name':'Tsukumo','nama_lengkap':'Ms. Yuki Tsukumo','id_tier':'TIR-SLV','tier':'Silver','award_miles':12600,'total_miles':36900,'tanggal_bergabung':'25 Jul 2022','country_code':'+81','mobile_number':'8031234011','tanggal_lahir_iso':'1984-12-31','kewarganegaraan':'Japanese'},
    {'nomor_member':'M0026','email':'yuta.okkotsu@gmail.com','salutation':'Mr.','first_mid_name':'Yuta','last_name':'Okkotsu','nama_lengkap':'Mr. Yuta Okkotsu','id_tier':'TIR-SLV','tier':'Silver','award_miles':7700,'total_miles':25400,'tanggal_bergabung':'08 Ags 2022','country_code':'+81','mobile_number':'8031234012','tanggal_lahir_iso':'2000-03-07','kewarganegaraan':'Japanese'},
    {'nomor_member':'M0027','email':'maki.zenin@gmail.com','salutation':'Ms.','first_mid_name':'Maki','last_name':'Zenin','nama_lengkap':'Ms. Maki Zenin','id_tier':'TIR-SLV','tier':'Silver','award_miles':10100,'total_miles':31700,'tanggal_bergabung':'19 Sep 2022','country_code':'+81','mobile_number':'8031234013','tanggal_lahir_iso':'2001-01-20','kewarganegaraan':'Japanese'},
    {'nomor_member':'M0028','email':'twilight.sparkle@yahoo.com','salutation':'Ms.','first_mid_name':'Twilight','last_name':'Sparkle','nama_lengkap':'Ms. Twilight Sparkle','id_tier':'TIR-SLV','tier':'Silver','award_miles':13800,'total_miles':39200,'tanggal_bergabung':'31 Okt 2022','country_code':'+1','mobile_number':'5551951022','tanggal_lahir_iso':'1995-10-22','kewarganegaraan':'American'},
    {'nomor_member':'M0029','email':'pinkie.pie@yahoo.com','salutation':'Ms.','first_mid_name':'Pinkie','last_name':'Pie','nama_lengkap':'Ms. Pinkie Pie','id_tier':'TIR-SLV','tier':'Silver','award_miles':6900,'total_miles':26800,'tanggal_bergabung':'14 Nov 2022','country_code':'+1','mobile_number':'5551960503','tanggal_lahir_iso':'1996-05-03','kewarganegaraan':'American'},
    {'nomor_member':'M0030','email':'rainbow.dash@yahoo.com','salutation':'Ms.','first_mid_name':'Rainbow','last_name':'Dash','nama_lengkap':'Ms. Rainbow Dash','id_tier':'TIR-SLV','tier':'Silver','award_miles':15200,'total_miles':44700,'tanggal_bergabung':'02 Des 2022','country_code':'+1','mobile_number':'5551950401','tanggal_lahir_iso':'1995-04-01','kewarganegaraan':'American'},
    {'nomor_member':'M0031','email':'jonathan.byers@gmail.com','salutation':'Mr.','first_mid_name':'Jonathan','last_name':'Byers','nama_lengkap':'Mr. Jonathan Byers','id_tier':'TIR-SLV','tier':'Silver','award_miles':8800,'total_miles':28500,'tanggal_bergabung':'25 Jan 2023','country_code':'+1','mobile_number':'5556671201','tanggal_lahir_iso':'1967-12-01','kewarganegaraan':'American'},
    {'nomor_member':'M0032','email':'mike.wheeler@gmail.com','salutation':'Mr.','first_mid_name':'Mike','last_name':'Wheeler','nama_lengkap':'Mr. Mike Wheeler','id_tier':'TIR-SLV','tier':'Silver','award_miles':9400,'total_miles':29900,'tanggal_bergabung':'17 Feb 2023','country_code':'+1','mobile_number':'5557110407','tanggal_lahir_iso':'1971-04-07','kewarganegaraan':'American'},
    {'nomor_member':'M0033','email':'nancy.wheeler@gmail.com','salutation':'Ms.','first_mid_name':'Nancy','last_name':'Wheeler','nama_lengkap':'Ms. Nancy Wheeler','id_tier':'TIR-SLV','tier':'Silver','award_miles':11900,'total_miles':35600,'tanggal_bergabung':'08 Mar 2023','country_code':'+1','mobile_number':'5556671114','tanggal_lahir_iso':'1967-11-14','kewarganegaraan':'American'},
    {'nomor_member':'M0034','email':'lucas.sinclair@gmail.com','salutation':'Mr.','first_mid_name':'Lucas','last_name':'Sinclair','nama_lengkap':'Mr. Lucas Sinclair','id_tier':'TIR-SLV','tier':'Silver','award_miles':13100,'total_miles':38300,'tanggal_bergabung':'20 Apr 2023','country_code':'+1','mobile_number':'5557110601','tanggal_lahir_iso':'1971-06-01','kewarganegaraan':'American'},
    {'nomor_member':'M0035','email':'dustin.henderson@gmail.com','salutation':'Mr.','first_mid_name':'Dustin','last_name':'Henderson','nama_lengkap':'Mr. Dustin Henderson','id_tier':'TIR-SLV','tier':'Silver','award_miles':7200,'total_miles':25100,'tanggal_bergabung':'05 Mei 2023','country_code':'+1','mobile_number':'5557110110','tanggal_lahir_iso':'1971-01-10','kewarganegaraan':'American'},

    {'nomor_member':'M0036','email':'satoru.gojo@gmail.com','salutation':'Mr.','first_mid_name':'Satoru','last_name':'Gojo','nama_lengkap':'Mr. Satoru Gojo','id_tier':'TIR-GLD','tier':'Gold','award_miles':28000,'total_miles':72000,'tanggal_bergabung':'15 Jan 2021','country_code':'+81','mobile_number':'8031234006','tanggal_lahir_iso':'1989-12-07','kewarganegaraan':'Japanese'},
    {'nomor_member':'M0037','email':'bruce.banner@gmail.com','salutation':'Dr.','first_mid_name':'Bruce','last_name':'Banner','nama_lengkap':'Dr. Bruce Banner','id_tier':'TIR-GLD','tier':'Gold','award_miles':35500,'total_miles':89300,'tanggal_bergabung':'22 Mar 2021','country_code':'+1','mobile_number':'5556911218','tanggal_lahir_iso':'1969-12-18','kewarganegaraan':'American'},
    {'nomor_member':'M0038','email':'natasha.romanoff@gmail.com','salutation':'Ms.','first_mid_name':'Natasha','last_name':'Romanoff','nama_lengkap':'Ms. Natasha Romanoff','id_tier':'TIR-GLD','tier':'Gold','award_miles':22800,'total_miles':61500,'tanggal_bergabung':'09 Mei 2021','country_code':'+7','mobile_number':'9161234567','tanggal_lahir_iso':'1984-11-22','kewarganegaraan':'Russian'},
    {'nomor_member':'M0039','email':'wanda.maximoff@gmail.com','salutation':'Ms.','first_mid_name':'Wanda','last_name':'Maximoff','nama_lengkap':'Ms. Wanda Maximoff','id_tier':'TIR-GLD','tier':'Gold','award_miles':31200,'total_miles':79600,'tanggal_bergabung':'31 Jul 2021','country_code':'+421','mobile_number':'9001234567','tanggal_lahir_iso':'1989-02-10','kewarganegaraan':'Sokovian'},
    {'nomor_member':'M0040','email':'scott.lang@gmail.com','salutation':'Mr.','first_mid_name':'Scott','last_name':'Lang','nama_lengkap':'Mr. Scott Lang','id_tier':'TIR-GLD','tier':'Gold','award_miles':27600,'total_miles':70200,'tanggal_bergabung':'14 Sep 2021','country_code':'+1','mobile_number':'5557240415','tanggal_lahir_iso':'1972-04-15','kewarganegaraan':'American'},
    {'nomor_member':'M0041','email':'steve.harrington@gmail.com','salutation':'Mr.','first_mid_name':'Steve','last_name':'Harrington','nama_lengkap':'Mr. Steve Harrington','id_tier':'TIR-GLD','tier':'Gold','award_miles':24100,'total_miles':63800,'tanggal_bergabung':'03 Nov 2021','country_code':'+1','mobile_number':'5556660922','tanggal_lahir_iso':'1966-09-22','kewarganegaraan':'American'},
    {'nomor_member':'M0042','email':'max.mayfield@gmail.com','salutation':'Ms.','first_mid_name':'Max','last_name':'Mayfield','nama_lengkap':'Ms. Max Mayfield','id_tier':'TIR-GLD','tier':'Gold','award_miles':38900,'total_miles':96200,'tanggal_bergabung':'27 Jan 2022','country_code':'+1','mobile_number':'5557110906','tanggal_lahir_iso':'1971-09-06','kewarganegaraan':'American'},
    {'nomor_member':'M0043','email':'jane.hopper@gmail.com','salutation':'Ms.','first_mid_name':'Jane','last_name':'Hopper','nama_lengkap':'Ms. Jane Hopper','id_tier':'TIR-GLD','tier':'Gold','award_miles':21500,'total_miles':57900,'tanggal_bergabung':'18 Mar 2022','country_code':'+1','mobile_number':'5557111028','tanggal_lahir_iso':'1971-10-28','kewarganegaraan':'American'},
    {'nomor_member':'M0044','email':'larajean.songcovey@ui.ac.id','salutation':'Ms.','first_mid_name':'Lara Jean Song','last_name':'Covey','nama_lengkap':'Ms. Lara Jean Song Covey','id_tier':'TIR-GLD','tier':'Gold','award_miles':33700,'total_miles':85400,'tanggal_bergabung':'07 Mei 2022','country_code':'+1','mobile_number':'5551990420','tanggal_lahir_iso':'1999-04-20','kewarganegaraan':'American'},
    {'nomor_member':'M0045','email':'margot.songcovey@ui.ac.id','salutation':'Ms.','first_mid_name':'Margot Song','last_name':'Covey','nama_lengkap':'Ms. Margot Song Covey','id_tier':'TIR-GLD','tier':'Gold','award_miles':29400,'total_miles':75100,'tanggal_bergabung':'22 Jul 2022','country_code':'+1','mobile_number':'7911234567','tanggal_lahir_iso':'1997-08-12','kewarganegaraan':'American'},

    {'nomor_member':'M0046','email':'tony.stark@gmail.com','salutation':'Mr.','first_mid_name':'Tony','last_name':'Stark','nama_lengkap':'Mr. Tony Stark','id_tier':'TIR-PLT','tier':'Platinum','award_miles':185000,'total_miles':420000,'tanggal_bergabung':'01 Jan 2020','country_code':'+1','mobile_number':'5557000529','tanggal_lahir_iso':'1970-05-29','kewarganegaraan':'American'},
    {'nomor_member':'M0047','email':'steve.rogers@gmail.com','salutation':'Mr.','first_mid_name':'Steve','last_name':'Rogers','nama_lengkap':'Mr. Steve Rogers','id_tier':'TIR-PLT','tier':'Platinum','award_miles':142000,'total_miles':310000,'tanggal_bergabung':'15 Mar 2020','country_code':'+1','mobile_number':'5551180704','tanggal_lahir_iso':'1918-07-04','kewarganegaraan':'American'},
    {'nomor_member':'M0048','email':'kitty.songcovey@ui.ac.id','salutation':'Ms.','first_mid_name':'Kitty Song','last_name':'Covey','nama_lengkap':'Ms. Kitty Song Covey','id_tier':'TIR-PLT','tier':'Platinum','award_miles':108500,'total_miles':235000,'tanggal_bergabung':'28 Jun 2020','country_code':'+1','mobile_number':'5552030630','tanggal_lahir_iso':'2003-06-30','kewarganegaraan':'American'},
    {'nomor_member':'M0049','email':'peter.kavinsky@ui.ac.id','salutation':'Mr.','first_mid_name':'Peter','last_name':'Kavinsky','nama_lengkap':'Mr. Peter Kavinsky','id_tier':'TIR-PLT','tier':'Platinum','award_miles':167300,'total_miles':380500,'tanggal_bergabung':'10 Sep 2020','country_code':'+1','mobile_number':'5551990622','tanggal_lahir_iso':'1999-06-22','kewarganegaraan':'American'},
    {'nomor_member':'M0050','email':'josh.sanderson@ui.ac.id','salutation':'Mr.','first_mid_name':'Josh','last_name':'Sanderson','nama_lengkap':'Mr. Josh Sanderson','id_tier':'TIR-PLT','tier':'Platinum','award_miles':129800,'total_miles':275200,'tanggal_bergabung':'05 Des 2020','country_code':'+1','mobile_number':'5559940315','tanggal_lahir_iso':'1994-03-15','kewarganegaraan':'American'},
]

IDENTITAS_LIST = {
    'judy.hopps@yahoo.com': [
        {
            'nomor': 'US-KTP-008',
            'jenis': 'KTP',
            'negara_penerbit': 'United States',
            'tanggal_terbit_iso': '2011-11-03',
            'tanggal_habis_iso': '9999-12-31',
        },
        {
            'nomor': 'US-PP-JH-001',
            'jenis': 'Paspor',
            'negara_penerbit': 'United States',
            'tanggal_terbit_iso': '2019-06-01',
            'tanggal_habis_iso': '2029-06-01',
        },
    ],
}


def kelola_member(request):
    role = request.session.get('role')
    if role != 'staff':
        return redirect('main:dashboard')
    return render(request, 'kelola_member.html', {'members': MEMBERS_LIST})


def tambah_member(request):
    if request.method == 'POST':
        # frontend-only, no real DB op
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
        habis_iso = item['tanggal_habis_iso']
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
            'tanggal_terbit_display': _fmt_tanggal(item['tanggal_terbit_iso']),
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
    context = {
        'identitas_list': _build_identitas(raw),
    }
    return render(request, 'identitas.html', context)


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
