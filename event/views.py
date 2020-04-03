from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.paginator import Paginator
from django.apps import apps

from .forms import EventForm
from .models import Property, Street, Type, EventSource, DisposeUnit, Event, Community, SubType


def update_number():
    properties = Property.objects.all()
    for pro in properties:
        num = pro.event.count()
        pro.number = num
        pro.save()

    communities = Community.objects.all()
    for community in communities:
        num = community.event.count()
        community.number = num
        community.save()
        street = community.street
        street.number += num
        street.save()

    sources = EventSource.objects.all()
    for source in sources:
        num = source.event.count()
        source.number = num
        source.save()

    units = DisposeUnit.objects.all()
    for unit in units:
        num = unit.event.count()
        unit.number = num
        unit.save()

    sub_types = SubType.objects.all()
    for sub_type in sub_types:
        num = sub_type.event.count()
        sub_type.number = num
        sub_type.save()
        main_type = sub_type.main_type
        main_type.number += num
        main_type.save()
        type = main_type.type
        type.number += num
        type.save()


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


def filter_model(keyword):
    models = apps.get_app_config('event').get_models()
    for model in models:
        data_list = model.objects.all()
        for data in data_list:
            try:
                if data.name == keyword:
                    return model, data
            except:
                continue
    return None, None


def my_filter(keyword, events_list):
    events_list = events_list.filter(
        Q(dispose_unit__name=keyword) |
        Q(event_src__name=keyword) |
        Q(property__name=keyword) |
        Q(community__name=keyword) |
        Q(community__street__name=keyword) |
        Q(community__street__district__name=keyword) |
        Q(sub_type__name=keyword) |
        Q(sub_type__main_type__name=keyword) |
        Q(sub_type__main_type__type__name=keyword)
    )
    return events_list


@login_required(login_url='/user/login/')
def event_list(request):
    events = Event.objects.all()
    properties = Property.objects.all()
    types = Type.objects.all()
    sources = EventSource.objects.all()

    paginator = Paginator(events, 20)
    page = request.GET.get('page')
    events_list = paginator.get_page(page)

    context = {
        "properties": properties,
        "event_list": events_list,
        "types": types,
        "src": sources,
    }
    return render(request, 'event/list.html', context)


@login_required(login_url='/user/login/')
def event_dispose(request):
    context = {}
    return render(request, 'event/list.html', context)
