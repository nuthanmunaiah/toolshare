from django import forms
from django.forms.models import formset_factory

from app.models.account import *


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_num', 'pickup_arrangements', 'send_reminders']


class UserAddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ['country']


UserProfileFormSet = formset_factory(UserProfileForm, UserAddressForm)


class ChangePasswordForm(forms.ModelForm):
    id = forms.CharField(widget=forms.HiddenInput())
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Old password',
                                   required=True)
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='New password',
                                   required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                                       label='Confirm New password', required=True)

    class Meta:
        model = User
        fields = ['id', 'old_password', 'new_password', 'confirm_password']

    def clean(self):
        super(ChangePasswordForm, self).clean()
        old_password = self.cleaned_data.get('old_password')
        new_password = self.cleaned_data.get('new_password')
        confirm_password = self.cleaned_data.get('confirm_password')
        id = self.cleaned_data.get('id')
        user = User.objects.get(pk=id)
        if not user.check_password(old_password):
            self._errors['old_password'] = self.error_class(['Old password don\'t match'])
        if new_password and new_password != confirm_password:
            self._errors['new_password'] = self.error_class(['Passwords don\'t match'])
        return self.cleaned_data