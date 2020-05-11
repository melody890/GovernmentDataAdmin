from captcha.fields import CaptchaField

from django import forms
from django.contrib.auth.models import User
from .models import Profile


class ProfileForm(forms.ModelForm):
    username = forms.CharField()

    class Meta:
        model = Profile
        fields = ('phone', 'avatar', 'bio')


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()
    captcha = CaptchaField(error_messages={'invalid':'验证码错误啊'})


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField()
    password2 = forms.CharField()

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_password2(self):
        data = self.cleaned_data
        if data.get('password') == data.get('password2'):
            return data.get('password')
        else:
            raise forms.ValidationError("两次密码输入不一致，请重试。")

class ResetForm(forms.Form):
    username = forms.CharField()
    email = forms.CharField()

class ResetPwForm(forms.Form):
    password = forms.CharField()