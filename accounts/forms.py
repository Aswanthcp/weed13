from django import forms

from orders.models import ProfileAddress

from .models import Account, UserProfile


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'PlaceHolder': 'Enter Password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'PlaceHolder': 'Confirm Password'
    }))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name',
                  'phone_number', 'email', 'password']

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "Passwords do not match"
            )

        if len(password) < 8:
            raise forms.ValidationError(
                "Password should Contain minimum of 8 characters!"
            )

        phone_number = cleaned_data.get('phone_number')
        if len(phone_number) != 10:
            raise forms.ValidationError(
                "Enter a valid Phone number"
            )

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Phone Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Email Address'

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class VerifyForm(forms.Form):
    code = forms.CharField(max_length=8, required=True, help_text='')


class otploginForm(forms.Form):
    phone_number = forms.CharField(max_length=13, required=True, help_text='')


class VerifyotpForm(forms.Form):
    code = forms.CharField(max_length=8, required=True, help_text='')


class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['address_line_1', 'address_line_2',
                  'city', 'state', 'country', 'pincode']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class AddressForm(forms.ModelForm):
    class Meta:
        model = ProfileAddress
        fields = ['address_line_1', 'address_line_2',
                  'city', 'state', 'country', 'pincode']

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
