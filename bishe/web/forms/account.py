from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django import forms
from django.db.models import Q

from web import models
from django.conf import settings
import random
from web.utils.tencent.sms import send_sms_single
from web.utils.encrypt import to_md5
from django_redis import get_redis_connection


class BootStrapForm(object):
    bootstrap_class_exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name in self.bootstrap_class_exclude:
                continue
            old_class = field.widget.attrs.get('class', "")
            field.widget.attrs['class'] = '{} form-control'.format(old_class)
            field.widget.attrs['placeholder'] = '请输入%s' % (field.label,)


class RegistModelForm(BootStrapForm, forms.ModelForm):
    mobile_phone = forms.CharField(label='手机号',
                                   validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$'),])
    password = forms.CharField(label='密码', min_length=8, max_length=64, error_messages={'min_length':"密码长度不能小于8位", 'max_length': '密码长度不能大于64位'}, widget=forms.PasswordInput)

    confirm_password = forms.CharField(label='确认密码', widget=forms.PasswordInput)
    code = forms.CharField(label='验证码')

    class Meta:
        model = models.UserInfo
        fields = ['username', 'email', 'password', 'confirm_password', 'mobile_phone', 'code']


    def clean_username(self):
        username = self.cleaned_data['username']
        exist = models.UserInfo.objects.filter(username=username).exists()
        if exist:
            raise ValidationError("用户名已存在！")

        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        exist = models.UserInfo.objects.filter(email=email).exists()
        if exist:
            raise ValidationError("邮箱已存在！")

        return email

    def clean_password(self):
        pwd = self.cleaned_data['password']
        pwd = to_md5(pwd)
        return pwd

    def clean_confirm_password(self):
        pwd = self.cleaned_data.get('password')
        confirm_pwd = to_md5(self.cleaned_data['confirm_password'])
        if pwd != confirm_pwd:
            raise ValidationError("两次密码输入不一致！")
        return confirm_pwd


    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if exists:
            raise ValidationError("手机号已存在！")
        return mobile_phone

    def clean_code(self):
        code = self.cleaned_data["code"]
        mobile_phone = self.cleaned_data.get('mobile_phone')
        if not mobile_phone:
            return code
        conn = get_redis_connection()
        redis_code = conn.get(mobile_phone)
        if not redis_code:
            raise ValidationError("验证码失效或未发送，请重新发送！")
        redis_str_code = redis_code.decode('utf-8')
        if code.strip() != redis_str_code:
            raise ValidationError("验证码错误，请重新输入！")
        return code


class SendSmsForm(forms.Form):
    mobile_phone = forms.CharField(label='手机号',
                                   validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$'), ])

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        tpl = self.request.GET.get('tpl')
        tpl_id = settings.TENCENT_SMS_TEMPLATE.get(tpl)
        if not tpl_id:
            raise ValidationError('短信模板错误！')
        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if tpl == 'login':
            if not exists:
                raise ValidationError("手机号未注册！")
        else:
            if exists:
                raise ValidationError('手机号已注册！')

        code = random.randrange(10000, 99999)
        sms = send_sms_single(mobile_phone, tpl_id, [code, ])
        if sms['result'] != 0:
            raise ValidationError("短信发送失败，{}".format(sms['errmsg']))

        conn = get_redis_connection()
        conn.set(mobile_phone, code, ex=60)
        return mobile_phone


class LoginSmsForm(BootStrapForm, forms.Form):
    mobile_phone = forms.CharField(label='手机号',
                                   validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$'),])
    code = forms.CharField(label='验证码')

    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        user_obj = models.UserInfo.objects.filter(mobile_phone=mobile_phone).first()
        if not user_obj:
            raise ValidationError("手机号未注册！")
        return user_obj

    def clean_code(self):
        code = self.cleaned_data["code"]
        user_obj = self.cleaned_data.get('mobile_phone')
        if not user_obj:
            return code
        mobile_phone = user_obj.mobile_phone
        conn = get_redis_connection()
        redis_code = conn.get(mobile_phone)
        if not redis_code:
            raise ValidationError("验证码失效或未发送！")
        redis_str_code = redis_code.decode('utf-8')
        if code.strip() != redis_str_code:
            raise ValidationError("验证码错误，请重新输入！")
        return code


class LoginPwdForm(BootStrapForm, forms.Form):
    username = forms.CharField(label='邮箱或手机号')
    password = forms.CharField(label='密码',
                               widget=forms.PasswordInput)
    imgcode = forms.CharField(label='验证码')

    def __init__(self,request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_username(self):
        username = self.cleaned_data['username']
        user_obj = models.UserInfo.objects.filter(Q(mobile_phone=username)|Q(email=username)).first()
        if not user_obj:
            raise ValidationError("用户不存在！")
        return user_obj

    def clean_imgcode(self):
        imgcode = self.cleaned_data['imgcode']
        session_code = self.request.session.get('image_code')
        if not session_code:
            raise ValidationError("验证码已过期！")
        if imgcode.upper() != session_code.upper():
            raise ValidationError("验证码错误！")
        return imgcode

    def clean_password(self):
        user_obj = self.cleaned_data.get('username')
        password = to_md5(self.cleaned_data['password'])
        if not user_obj:
            return password
        user_pwd = user_obj.password
        if user_pwd != password:
            raise ValidationError("用户名或密码错误！")
        return password


class ChangePwdModelForm(BootStrapForm, forms.ModelForm):
    new_pwd = forms.CharField(label='新密码', min_length=8, max_length=64,
                               error_messages={'min_length': "密码长度不能小于8位", 'max_length': '密码长度不能大于64位'},
                               widget=forms.PasswordInput)
    confirm_new_pwd = forms.CharField(label='确认密码', min_length=8, max_length=64,
                               error_messages={'min_length': "密码长度不能小于8位", 'max_length': '密码长度不能大于64位'},
                               widget=forms.PasswordInput)
    pwd = forms.CharField(label='原密码', widget=forms.PasswordInput)

    class Meta:
        model = models.UserInfo
        fields = ['pwd', 'new_pwd', 'confirm_new_pwd']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean(self):
        pwd = self.cleaned_data.get('pwd')
        new_pwd = self.cleaned_data.get('new_pwd')
        confirm_new_pwd = self.cleaned_data.get('confirm_new_pwd')
        if not pwd or not new_pwd or not confirm_new_pwd:
            return self.cleaned_data
        pwd = to_md5(pwd)
        new_pwd = to_md5(new_pwd)
        confirm_new_pwd = to_md5(confirm_new_pwd)
        if pwd != self.request.tracer.user.password:
            self.add_error('pwd', '密码输入错误，请重新输入！')
            return self.cleaned_data
        if pwd == new_pwd:
            self.add_error('new_pwd', '新密码不能与原密码相同！')
            return self.cleaned_data
        if new_pwd != confirm_new_pwd:
            self.add_error('confirm_new_pwd', '两次密码输入不一致！')
            return self.cleaned_data
        self.cleaned_data['pwd'] = new_pwd
        return self.cleaned_data


