from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.paginator import Paginator

from .forms import EventForm
from .models import Property, Street, Type, EventSource, DisposeUnit, Event, Community, SubType


@login_required(login_url='/user/login/')
def event_post(request):
    if request.method == 'POST':
        event_post_form = EventForm(request.POST)
        if event_post_form.is_valid():
            form_data = event_post_form.cleaned_data
            new_event = Event()
            new_event.author = User.objects.get(id=request.user.id)
            new_event.property = Property.objects.get(name=form_data['property'])
            new_event.community = Community.objects.get(name=form_data['community'])
            new_event.event_src = EventSource.objects.get(name=form_data['event_src'])
            new_event.sub_type = SubType.objects.get(name=form_data['sub_type'])
            new_event.dispose_unit = DisposeUnit.objects.get(name=form_data['dispose_unit'])
            new_event.save()
            return redirect(to="event:post")
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    else:
        post_form = EventForm()
        properties = Property.objects.all()
        streets = Street.objects.all()
        types = Type.objects.all()
        sources = EventSource.objects.all()
        units = DisposeUnit.objects.all()
        context = {
            'form': post_form,
            'properties': properties,
            'streets': streets,
            'types': types,
            'sources': sources,
            'units': units,
        }
        return render(request, 'event/post.html', context)


@login_required(login_url='/user/login/')
def event_list(request):
    search = request.GET.get('search')
    events = Event.objects.all()
    properties = Property.objects.all()
    types = Type.objects.all()

    if search:
        events = events.filter(
            Q(dispose_unit__name=search) |
            Q(event_src__name=search) |
            Q(property__name=search) |
            Q(community__name=search) |
            Q(community__street__name=search) |
            Q(community__street__district__name=search) |
            Q(sub_type__name=search) |
            Q(sub_type__main_type__name=search) |
            Q(sub_type__main_type__type__name=search)
        )
    else:
        search = ""

    paginator = Paginator(events, 20)
    page = request.GET.get('page')
    event_list = paginator.get_page(page)

    context = {
        "properties": properties,
        "event_list": event_list,
        "types": types,
        "search": search,
    }
    return render(request, 'event/list.html', context)


@login_required(login_url='/user/login/')
def event_dispose(request):
    context = {}
    return render(request, 'event/list.html', context)
