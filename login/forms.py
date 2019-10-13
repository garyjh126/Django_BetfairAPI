from django import forms
from .models import User
import requests
from . import keys
from django.core.validators import MinValueValidator, MaxValueValidator


# class RegistrationForm(forms.ModelForm):
#     username = forms.CharField(label='Username')
#     password = forms.CharField(widget=forms.PasswordInput, label='Password')

#     class Meta: 
#         model = User # allows us to call form.save from within views.py
#         fields = ('username', 'password') 

class LoginForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    payload = None
    headers = None

    def log_betfair(self, username, password):
        LoginForm.payload = 'username='+username+'&password='+password
        LoginForm.headers = {'X-Application': keys.app_key, 'Content-Type': 'application/x-www-form-urlencoded'}
        resp = requests.post('https://identitysso-cert.betfair.com/api/certlogin', data=self.payload, cert=('/home/gary/Desktop/Development/Betfair/Python/betfair/login/client-2048.crt', '/home/gary/Desktop/Development/Betfair/Python/betfair/login/client-2048.key'), headers=self.headers)

        if resp.status_code == 200:
            resp_json = resp.json()
            print(resp_json['loginStatus'])
            if not(resp_json['loginStatus'] == 'INVALID_USERNAME_OR_PASSWORD'):
                print(resp_json['sessionToken'])
                LoginForm.ssoid = resp_json['sessionToken']
        else:
            print("Request failed.")  
                    
class GenerateRandomUserForm(forms.Form):
    total = forms.IntegerField(
        validators=[
            MinValueValidator(50),
            MaxValueValidator(500)
        ]
    )

