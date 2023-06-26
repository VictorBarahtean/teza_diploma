from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Profile


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'Title':'test'}))
    password = forms.CharField(widget=forms.PasswordInput)

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
    
    def clean(self):
        cd = self.cleaned_data
        
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Parola nu conincide.')

        if User.objects.filter(email=cd['email']).count() > 0:
            raise forms.ValidationError('Utilizator cu asa email deja exista.')

        validate_password(cd['password'], self.instance)
        
        return cd

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('date_of_brith', 'photo')

class SearchForm(forms.Form):
    search_query = forms.CharField(max_length=100)
    type_search = forms.CharField(max_length=10)