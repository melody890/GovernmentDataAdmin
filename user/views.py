import datetime
import pytz
from uuid import uuid4
from PIL import Image, ImageDraw, ImageFont
import random
from io import BytesIO

from notifications.signals import notify
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .forms import UserLoginForm, UserRegisterForm, ProfileForm, ResetForm, ResetPwForm, PermissionApplyForm
from .models import Profile, ConfirmString, ApplyList, DisposeRecord, PostRecord
from event.models import EventSource, DisposeUnit, Event

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
                print(data)
                print(user)
                if user:
                    login(request, user)
                    return redirect(to="home:dashboard")
                else:
                    return error_page(request=request, info="账号或密码输入有误。请重新输入。")
            else:
                return error_page(request=request, info="账号或密码或验证码输入不合法")
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

def congratulate_page(request, info):
    context = {
        "info": info,
    }
    return render(request, "user/congratulate.html", context)

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
                return congratulate_page(request=request, info="验证邮件已发出，请前往邮箱验证")
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

    notices = user.notifications.unread()

    apply_list = ApplyList.objects.all()

    dispose_record = DisposeRecord.objects.filter(disposer=request.user.username)
    post_record = PostRecord.objects.filter(poster=request.user.username)

    dispose_events = []
    for record in reversed(dispose_record):
        if Event.objects.filter(rec_id=record.eventID).exists():
            event = Event.objects.get(rec_id=record.eventID)
        dispose_events.append(event)

    post_events = []
    for record in reversed(post_record):
        if Event.objects.filter(rec_id=record.eventID).exists():
            event = Event.objects.get(rec_id=record.eventID)
        post_events.append(event)

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
            'notices': notices,
            'apply_list':apply_list,
            'post_events':post_events[:20],
            'dispose_events':dispose_events[:20],
        }
        return render(request, 'user/edit.html', context)
    else:
        return error_page(request, "请使用GET或POST请求数据。")

def make_confirm_string(user):
    code = str(uuid4())
    ConfirmString.objects.create(code=code, user=user)
    return code


def confirm_email(mode, email, code, host, username):
    print(mode, email, code, host, username)
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
        notify.send(
            confirm.user,
            recipient=User.objects.filter(is_superuser=1),
            verb='注册了新账号',
        )
        confirm.user.is_active = True
        confirm.user.save()
        confirm.delete()
        message = '恭喜您注册成功，赶快尝试登录吧！'
    return congratulate_page(request, message)


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
            return congratulate_page(request, "验证邮件已发送，请往邮箱进行验证")
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
        notify.send(
            confirm.user,
            recipient=User.objects.filter(is_superuser=1),
            verb='重置了账号',
        )
        newpassword = request.POST.get('newpassword')
        confirm.user.set_password(newpassword)
        confirm.user.save()
        confirm.delete()
        return congratulate_page(request, '恭喜您重置成功，赶快尝试登录吧！')
    elif request.method == 'GET':
        reset_pw_form = ResetPwForm()
        context = {'form': reset_pw_form}
        return render(request, 'user/resetconfirm.html', context)
    else:
        return error_page(request, "请使用GET或POST请求数据。")

def ajax_val(request):
    if  request.is_ajax():
        cs = CaptchaStore.objects.filter(response=request.GET['response'], hashkey=request.GET['hashkey'])
        if cs:
            json_data={'status':1}
        else:
            json_data = {'status':0}
        return JsonResponse(json_data)
    else:
        json_data = {'status':0}
        return JsonResponse(json_data)

def apply_permission(request):
    if request.method == 'POST':
        if ApplyList.objects.filter(user=request.user).exists():
            return error_page(request,'你已经提交申请，无需重复操作')
        if not Profile.objects.filter(user=request.user).exists():
            profile = Profile.objects.create(user=request.user)
        else:
            profile = Profile.objects.get(user=request.user)
        apply_form = PermissionApplyForm(request.POST)
        if apply_form.is_valid():
            form_data = apply_form.cleaned_data
            if profile.is_disposer:
                return error_page(request, "你已经拥有处理员权限")
            if profile.is_poster:
                return error_page(request, "你已经拥有上传员权限")
            if request.user.is_superuser:
                return error_page(request, "你已经拥有"+form_data.get('apply_permission')+"权限")
            notify.send(
                request.user,
                recipient=User.objects.filter(is_superuser=1),
                verb='代表'+form_data.get('apply_unit') + '申请' + form_data.get('apply_permission') + '权限',
            )
            ApplyList.objects.create(user=request.user, apply_permission=form_data.get('apply_permission'), apply_unit=form_data.get('apply_unit'), validation=form_data.get('validation'))
            return redirect("user:permissionApply")
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    else:
        apply_form = PermissionApplyForm()
        sources = EventSource.objects.all()
        units = DisposeUnit.objects.all()
        apply_permissions = ['处理员','上传员']
        context = {
            'form': PermissionApplyForm,
            'sources': sources,
            'units': units,
            'apply_permissions':apply_permissions,
        }
        return render(request, 'user/permissionapply.html', context)

def view_permission(request):
    if not request.user.is_superuser:
        return error_page(request,'您没有权限进行此操作')
    dispose_profiles = Profile.objects.filter(is_disposer=True)
    post_profiles = Profile.objects.filter(is_poster=True)
    superusers = User.objects.filter(is_superuser=True)
    applications = ApplyList.objects.all()
    context = { 'dispose_profiles':dispose_profiles,
                'post_profiles':post_profiles,
                'superusers':superusers,
                'applications':applications,
               }
    return render(request, 'user/permissionview.html', context)

def permission_delete(request,id):
    if not request.user.is_superuser:
        return error_page(request,'您没有权限进行此操作')
    user = User.objects.get(id=id)
    profile = Profile.objects.get(user=user)
    notify.send(
        request.user,
        recipient=User.objects.filter(is_superuser=1),
        verb='撤除了' + profile.user.username + '关于' + profile.unit + '的权限',
    )
    notify.send(
        request.user,
        recipient=profile.user,
        verb='撤除了' + '你' + '关于' + profile.unit + '的权限',
    )
    profile.is_poster = False
    profile.is_disposer = False
    profile.unit = ''
    profile.save()
    return redirect(to='user:permissionView')

def reject_permission(request, id):
    if not request.user.is_superuser:
        return error_page(request,'您没有权限进行此操作')
    user = User.objects.get(id=id)
    application = ApplyList.objects.get(user=user)
    notify.send(
        request.user,
        recipient=User.objects.filter(is_superuser=1),
        verb='拒绝了' + application.user.username + '关于' + application.apply_unit + '的' + application.apply_permission + '权限的申请',
    )
    notify.send(
        request.user,
        recipient=application.user,
        verb='拒绝了' + '你' + '关于' + application.apply_unit + '的' + application.apply_permission + '权限的申请',
    )
    application.delete()
    return redirect(to='user:permissionView')

def accept_permission(request, id):
    if not request.user.is_superuser:
        return error_page(request,'您没有权限进行此操作')
    user = User.objects.get(id=id)
    profile = Profile.objects.get(user=user)
    application = ApplyList.objects.get(user=user)
    if application.apply_permission == '处理员':
        profile.is_disposer = True
    else:
        profile.is_poster = True
    profile.unit = application.apply_unit
    profile.save()
    notify.send(
        request.user,
        recipient=User.objects.filter(is_superuser=1),
        verb='接受了' + application.user.username + '关于' + application.apply_unit + '的' + application.apply_permission + '权限的申请',
    )
    notify.send(
        request.user,
        recipient=application.user,
        verb='接受了' + '你' + '关于' + application.apply_unit + '的' + application.apply_permission + '权限的申请',
    )
    application.delete()
    return redirect(to='user:permissionView')