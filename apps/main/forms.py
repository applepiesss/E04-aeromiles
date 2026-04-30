from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from .models import Member, Staff, SALUTATION_CHOICES


class MemberProfileForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['salutation', 'first_mid_name', 'last_name', 'country_code', 
                  'phone_number', 'nationality', 'date_of_birth']
        widgets = {
            'salutation': forms.Select(choices=SALUTATION_CHOICES, attrs={
                'class': 'w-full px-4 py-2 border border-blue-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'first_mid_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-blue-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'First and Middle Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-blue-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Last Name'
            }),
            'country_code': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-blue-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': '+62'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-blue-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Phone Number',
                'type': 'tel'
            }),
            'nationality': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-blue-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nationality'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-blue-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
        }


class StaffProfileForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['salutation', 'first_mid_name', 'last_name', 'country_code', 
                  'phone_number', 'nationality', 'date_of_birth', 'airline_code']
        widgets = {
            'salutation': forms.Select(choices=SALUTATION_CHOICES, attrs={
                'class': 'w-full px-4 py-2 border border-blue-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'first_mid_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-blue-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'First and Middle Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-blue-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Last Name'
            }),
            'country_code': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-blue-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': '+62'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-blue-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Phone Number',
                'type': 'tel'
            }),
            'nationality': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-blue-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nationality'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-blue-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
            'airline_code': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-blue-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Airline Code (e.g., GA)',
                'maxlength': '10'
            }),
        }


class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        label='Password Lama',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-blue-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Masukkan password lama'
        })
    )
    new_password = forms.CharField(
        label='Password Baru',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-blue-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Masukkan password baru'
        })
    )
    confirm_password = forms.CharField(
        label='Konfirmasi Password Baru',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-blue-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Konfirmasi password baru'
        })
    )

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if self.user and not self.user.check_password(old_password):
            raise forms.ValidationError('Password lama tidak sesuai.')
        return old_password

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        if len(new_password) < 8:
            raise forms.ValidationError('Password baru harus minimal 8 karakter.')
        return new_password

    def clean_confirm_password(self):
        new_password = self.cleaned_data.get('new_password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError('Password baru dan konfirmasi tidak cocok.')
        return confirm_password
