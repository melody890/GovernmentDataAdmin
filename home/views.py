from django.shortcuts import render

from django.contrib.auth.decorators import login_required


@login_required(login_url='/user/login/')
def dashboard(request):
    context = {
        'cur_page': "dashboard"
    }
    return render(request, "home/dashboard.html", context)


def error_page(request, info):
    context = {
        "info": info,
    }
    return render(request, "home/error.html", context)
