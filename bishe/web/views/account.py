"""用户账户相关功能：注册、登陆、短信、注销"""
from io import BytesIO

from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from web.forms.account import RegistModelForm, SendSmsForm, LoginSmsForm, LoginPwdForm, ChangePwdModelForm
from web.utils.code import check_code
from web import models
import uuid
import datetime


def register(request):
    if request.method == 'GET':
        form = RegistModelForm()
        return render(request, 'register.html', {"form": form})
    form = RegistModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({"status": True, 'data': '/login/pwd/'})
    return JsonResponse({"status": False, "error": form.errors})


def send_sms(request):
    form = SendSmsForm(request, data=request.GET)
    if form.is_valid():
        return JsonResponse({'status': True})
    return JsonResponse({"status": False, "error": form.errors})


def login_sms(request):
    if request.method == 'GET':
        form = LoginSmsForm()
        return render(request, 'login.html', {"form": form})
    form = LoginSmsForm(data=request.POST)
    if form.is_valid():
        user_obj = form.cleaned_data['mobile_phone']
        request.session['user_id'] = user_obj.id
        request.session.set_expiry(60 * 60 * 24 * 7)
        return JsonResponse({"status": True, "data": '/index/'})
    return JsonResponse({"status": False, "error": form.errors})


def login(request):
    if request.method == 'GET':
        form = LoginPwdForm(request)
        return render(request, 'login.html', {"form": form})
    form = LoginPwdForm(request, data=request.POST)
    if form.is_valid():
        user_obj = form.cleaned_data['username']
        request.session['user_id'] = user_obj.id
        request.session.set_expiry(60 * 60 * 24 * 7)
        return JsonResponse({"status": True, "data": '/index/'})
    return JsonResponse({"status": False, "error": form.errors})


def image_code(request):
    img, code_string = check_code()
    stream = BytesIO()
    img.save(stream, "png")
    request.session["image_code"] = code_string
    request.session.set_expiry(60)
    return HttpResponse(stream.getvalue())


def logout(request):
    request.session.clear()
    return redirect('/index/')


def editpwd(request):
    form = ChangePwdModelForm(request, data=request.POST)
    if form.is_valid():
        new_password = form.cleaned_data['pwd']
        request.tracer.user.password = new_password
        request.tracer.user.save()
        return JsonResponse({"status": True})
    return JsonResponse({"status": False, "error": form.errors})



