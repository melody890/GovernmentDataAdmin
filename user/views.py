import datetime
import pytz
from uuid import uuid4

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .forms import UserLoginForm, UserRegisterForm, ProfileForm, ResetForm, ResetPwForm
from .models import Profile, ConfirmString

from home.views import error_page


def user_login(request):
    user = request.user
    if user.is_authenticated:
        return redirect(to="home:dashboard")
    else:
        if request.method == 'POST':
            user_login_form = UserLoginForm(data=request.POST)
            if user_login_form.is_valid():
                data = user_login_form.cleaned_data
                user = authenticate(username=data['username'], password=data['password'])
                if user:
                    login(request, user)
                    return redirect(to="home:dashboard")
                else:
                    return error_page(request=request, info="账号或密码输入有误。请重新输入。")
            else:
                return error_page(request=request, info="账号或密码输入不合法")
        elif request.method == 'GET':
            user_login_form = UserLoginForm()
            context = {'form': user_login_form}
            return render(request, 'user/login.html', context)
        else:
            return error_page(request=request, info="请使用GET或POST请求数据。")


@login_required(login_url='/user/login/')
def user_logout(request):
    logout(request)
    return redirect(to="user:login")


def user_register(request):
    user = request.user
    if user.is_authenticated:
        return redirect(to="index")
    else:
        if request.method == 'POST':
            user_register_form = UserRegisterForm(data=request.POST)
            if user_register_form.is_valid():
                new_user = user_register_form.save(commit=False)
                new_user.set_password(user_register_form.cleaned_data['password'])
                new_user.is_active = False
                new_user.save()
                email = request.POST.get('email')
                code = make_confirm_string(new_user)
                confirm_email('confirm2register',email, code,request.get_host(), new_user.username)
                return HttpResponse("验证邮件已发出，请前往邮箱验证")
            else:
                return error_page(request=request, info="注册表单有误。请重新输入。")
        elif request.method == 'GET':
            user_register_form = UserRegisterForm()
            context = {'form': user_register_form}
            return render(request, 'user/register.html', context)
        else:
            return error_page(request=request, info="请使用GET或POST请求数据。")


@login_required(login_url='/user/login/')
def user_delete(request, id):
    user = User.objects.get(id=id)
    if request.user == user:
        logout(request)
        user.delete()
        return redirect(to="user:login")
    else:
        return error_page(request=request, info="你没有删除操作的权限。")


@login_required(login_url='/user/login/')
def profile_edit(request, id):
    user = User.objects.get(id=id)

    if Profile.objects.filter(user_id=id).exists():
        profile = Profile.objects.get(user_id=id)
    else:
        profile = Profile.objects.create(user=user)

    if request.method == 'POST':
        if request.user != user:
            return error_page(request, "您没有权限修改此用户信息。")

        profile_form = ProfileForm(request.POST, request.FILES)
        print(profile_form)
        if profile_form.is_valid():
            profile_cd = profile_form.cleaned_data
            print(profile_cd)
            user.username = profile_cd['username']
            profile.phone = profile_cd['phone']
            profile.bio = profile_cd['bio']

            if 'avatar' in request.FILES:
                profile.avatar = profile_cd['avatar']

            user.save()
            profile.save()

            return redirect("user:edit", id=id)
        else:
            return error_page(request, "注册表单有误。请重新输入。")

    elif request.method == 'GET':
        profile_form = ProfileForm()
        context = {
            'profile_form': profile_form,
            'profile': profile,
            'user': user,
        }
        return render(request, 'user/edit.html', context)
    else:
        return error_page(request, "请使用GET或POST请求数据。")


def make_confirm_string(user):
    code = str(uuid4())
    ConfirmString.objects.create(code=code, user=user)
    return code


def confirm_email(mode, email, code, host, username):

    text_content = '''这里是政府大数据平台\
                        如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！'''     

    if mode == 'confirm2register':
        subject = '请完成政府大数据平台的注册确认'
        html_content = '''
                            <p style="text-align:center">亲爱的{}, 你好!</p>
                            <p style="text-align:center">政府大数据平台已经收到您的注册信息，恭喜你注册成功，请点击以下的链接完成注册吧</p>
                            <p style="text-align:center"><a href="http://{}/user/register/confirm/{}" target=blank>完成注册，开始政府数据可视化体验吧</a></p>
                            <p style="text-align:center">如果不能无法点击链接，请将下列链接复制粘贴到浏览器输入栏</p> 
                            <p style="text-align:center">http://{}/user/register/confirm/{}</p>
                            <p style="text-align:center">此链接有效期为{}天</p>
                            <p style="text-align:center;color:grey;">来自政府大数据可视化平台</p>
                            '''.format(username, host, code, host, code, settings.CONFIRM_DAYS)
    elif mode == 'confirm2reset':
        subject = '请完成政府大数据平台的密码重置'
        html_content = '''
                            <p style="text-align:center">亲爱的{}, 你好!</p>
                            <p style="text-align:center">政府大数据平台已经收到您的重置请求，恭喜你验证成功，请点击以下的链接完成重置吧</p>
                            <p style="text-align:center"><a href="http://{}/user/reset/confirm/{}" target=blank>完成重置，重新开始政府数据可视化体验吧</a></p>
                            <p style="text-align:center">如果不能无法点击链接，请将下列链接复制粘贴到浏览器输入栏</p> 
                            <p style="text-align:center">http://{}/user/reset/confirm/{}</p>
                            <p style="text-align:center">此链接有效期为{}天</p>
                            <p style="text-align:center;color:grey;">来自政府大数据可视化平台</p>
                            '''.format(username, host, code, host, code, settings.CONFIRM_DAYS)
    else:
        subject = None
        html_content = ""

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")

    msg.send()


def register_confirm(request, code):
    try:
        confirm = ConfirmString.objects.get(code=code)
    except:
        return error_page(request, '无效的确认请求!')

    c_time = confirm.c_time
    now = datetime.datetime.now()
    now = now.replace(tzinfo=pytz.timezone('UTC'))
    if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message = '您的邮件已经过期！请重新注册!'
    else:
        confirm.user.is_active = True
        confirm.user.save()
        confirm.delete()
        message = '恭喜您注册成功，赶快尝试登录吧！'
    return HttpResponse(message)


def reset_password(request):
    if request.method == 'POST':
        reset_pw_form = ResetForm(data=request.POST)
        if reset_pw_form.is_valid():
            email = request.POST.get('email')
            username = request.POST.get('username')
            try:
                user = User.objects.get(username=username)
            except:
                return error_page(request, "账号不存在")
            if email != user.email:
                return error_page(request, "账号或邮箱输入错误")
            code = make_confirm_string(user)
            confirm_email('confirm2reset', email, code, request.get_host(), username)
            return HttpResponse("验证邮件已发送，请往邮箱进行验证")
        else:
            return error_page(request, "账号或邮箱输入不合法")
    elif request.method == 'GET':
        reset_form = ResetForm()
        context = {'form': reset_form}
        return render(request, 'user/reset.html', context)
    else:
        return error_page(request, "请使用GET或POST请求数据。")


def reset_confirm(request, code):
    try:
        confirm = ConfirmString.objects.get(code=code)
    except:
        return error_page(request, '无效的确认请求!')

    if request.method == 'POST':
        newpassword = request.POST.get('newpassword')
        confirm.user.set_password(newpassword)
        confirm.user.save()
        confirm.delete()
        return HttpResponse('恭喜您重置成功，赶快尝试登录吧！')    
    elif request.method == 'GET':
        reset_pw_form = ResetPwForm()
        context = {'form': reset_pw_form}
        return render(request, 'user/resetconfirm.html', context)
    else:
        return error_page(request, "请使用GET或POST请求数据。")
