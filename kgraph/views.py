from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse

from pyecharts.charts import Graph
from pyecharts.charts import WordCloud
from pyecharts import options as opts

from event.views import filter_model
from event.models import Community, SubType, Type, MainType, Event, \
    Street, District, DisposeUnit, Property, EventSource, Achieve

import random

word_item = [
    Community, SubType, Type, MainType, Street, DisposeUnit, Property, EventSource, Achieve
]


@login_required(login_url='/user/login/')
def get_kgraph(request):
    search = request.GET.get('search')
    if search:
        (model_name, model) = filter_model(search)
        if model_name and model:
            model_name = model_name.__name__
            print(model_name)
            print(str(model))
            kgraph = graph(model_name, model)
            page = "graph"
        else:
            kgraph = get_word()
            page = "wordcloud"
    else:
        kgraph = get_word()
        page = "wordcloud"

    context = {
        'graph': kgraph,
        'kg_search': search,
        "page": page,
        'cur_page': "kgraph",
    }
    return render(request, 'kgraph/kgraph.html', context)


def get_ajax(request):
    uname = request.GET.get('uname')
    # print(uname)
    if uname:
        (model_name, model) = filter_model(uname)
        if model_name and model:
            model_name = model_name.__name__
            # print(model_name)
            # print(str(model))
            kgraph = graph(model_name, model)
        else:
            kgraph = ''
    else:
        kgraph = ''

    context = {
        "graph": kgraph
    }
    # print(context)

    return JsonResponse(context)


def graph(model_name, model) -> Graph:
    (categories, nodes, links) = get_data(model_name, model)

    c = (
        Graph(
            init_opts=opts.InitOpts(width="1600px", height="800px")
        )
        .add(
            "",
            nodes=nodes,
            links=links,
            categories=categories,
            gravity=0.01,
            repulsion=300,
            linestyle_opts=opts.LineStyleOpts(color="black", curve=0.2),
            label_opts=opts.LabelOpts(is_show=True, position='inside', font_size=20),
            is_draggable=True,
            is_rotate_label=True,
            is_focusnode=True,
            layout="force",
            edge_length=200,
            edge_label=opts.LabelOpts(
                is_show=True,
                position="middle",
                font_size=15,
                formatter="{c}"
            ),
            edge_symbol=[None,'arrow']
        )
        .set_global_opts(
            legend_opts=opts.LegendOpts(is_show=True),
            title_opts=opts.TitleOpts(title=str(model)),
        )
        .dump_options_with_quotes()
    )

    return c


def get_data(model_name, model):
    if model_name == "Property":
        (categories, nodes, links) = get_property_data(model_name, model)
    elif model_name == "EventSource":
        (categories, nodes, links) = get_source_data(model_name, model)
    elif model_name == "Achieve":
        (categories, nodes, links) = get_achive_data(model_name, model)
    elif model_name == "SubType":
        (categories, nodes, links) = get_subtype_data(model_name, model)
    elif model_name == "MainType":
        (categories, nodes, links) = get_maintype_data(model)
    elif model_name == "Type":
        (categories, nodes, links) = get_type_data(model)
    elif model_name == 'Community':
        (categories, nodes, links) = get_community_data(model_name, model)
    elif model_name == "Street":
        (categories, nodes, links) = get_street_data(model_name, model)
    elif model_name == "District":
        (categories, nodes, links) = get_district_data(model_name, model)
    elif model_name == 'DisposeUnit':
        (categories, nodes, links) = get_disposeunit_data(model_name, model)
    else:
        (categories, nodes, links) = (None, None, None)

    return categories, nodes, links


def create_node(source_node, categories, cate_name, nodes, node_name, links, link_name, node_value='-'):
    categories.append(opts.GraphCategory(cate_name))
    # print(cate_name)
    length = len(categories) - 1
    nodes.append(opts.GraphNode(name=node_name, value=node_value, symbol_size=50, category=length))
    # print(node_name)
    links.append(opts.GraphLink(source=source_node, target=node_name, value=link_name))
    # print(link_name)

    return 0


# 事件性质
def get_property_data(model_name, model):
    events = model.event.get_queryset()
    intime_number = 0
    intime_to_number = 0
    overtime_number = 0
    community_list = {}
    for event in events:
        achieve = event.achieve.name
        community = event.community.name
        if community in community_list.keys():
            community_list[community] += 1
        else:
            community_list.update({community: 1})
        if achieve == "执行中":
            intime_to_number += 1
        elif achieve == '按期办结':
            overtime_number += 1
        elif achieve == "逾期办结":
            intime_number += 1

    number_max = 0
    for key in community_list:
        if community_list[key] > number_max:
            community = key
            number_max = community_list[key]

    community_model = Community.objects.get(name=community)
    street = community_model.street
    district = street.district

    categories = [
        opts.GraphCategory(name="事件性质"),
        opts.GraphCategory(name="事件数量"),
        opts.GraphCategory(name="百分比"),
        opts.GraphCategory(name="百分比"),
        # opts.GraphCategory(name="逾期办结"),
        opts.GraphCategory(name="社区"),
        opts.GraphCategory(name="街道"),
        opts.GraphCategory(name="区域"),
    ]
    nodes = [
        opts.GraphNode(name=str(model), symbol_size=80, category=0),
        opts.GraphNode(name=str(model.number), symbol_size=50, category=1),
        opts.GraphNode(name=str((round(intime_to_number*100/model.number,2)))+'%', symbol_size=50, category=2),
        opts.GraphNode(name=str((round(intime_number*100/model.number,2)))+'%', symbol_size=50, category=3),
        # opts.GraphNode(name=str(overtime_number), symbol_size=50, category=4),
        opts.GraphNode(name=community, symbol_size=50, category=5),
        opts.GraphNode(name=street.name, symbol_size=40, category=6),
        opts.GraphNode(name=district.name, symbol_size=30, category=7),
    ]
    links = [
        opts.GraphLink(source=str(model), target=str(model.number), value='事件总数'),
        opts.GraphLink(source=str(model), target=str((round(intime_to_number*100/model.number, 2)))+'%', value='执行中事件百分比'),
        opts.GraphLink(source=str(model), target=str((round(intime_number*100/model.number, 2)))+'%', value='按期办结百分比'),
        # opts.GraphLink(source=str(model), target=str(overtime_number), value=50),
        opts.GraphLink(source=str(model), target=community, value=str(model) + "下最多社区"),
        opts.GraphLink(source=community, target=street.name, value="对应街道"),
        opts.GraphLink(source=street.name, target=district.name, value="对应区域"),
    ]

    return categories, nodes, links


# 事件来源
def get_source_data(model_name, model):
    events = model.event.get_queryset()
# 对应性质
    property_list = {}
    for event in events:
        proper = event.property.name
        if proper in property_list.keys():
            property_list[proper] += 1
        else:
            property_list.update({proper: 1})

# 占事件总数百分比
    ratio = '{:.2f}%'.format(model.number / Event.objects.count() * 100)
    number_max = 0
    for key in property_list:
        if property_list[key] > number_max:
            proper = key
            number_max = property_list[key]

    categories = [
        opts.GraphCategory(name="来源"),
        opts.GraphCategory(name="数量"),
        opts.GraphCategory(name="性质"),
        opts.GraphCategory(name="百分比"),
    ]
    nodes = [
        opts.GraphNode(name=str(model), symbol_size=80, category=0),
        opts.GraphNode(name=str(model.number), symbol_size=50, category=1),
        opts.GraphNode(name=proper, symbol_size=50, category=2),
        opts.GraphNode(name=ratio, symbol_size=50, category=3),
    ]

    links = [
        opts.GraphLink(source=str(model), target=str(model.number), value="事件总数量"),
        opts.GraphLink(source=str(model), target=proper, value="对应性质"),
        opts.GraphLink(source=str(model), target=ratio, value="占事件总数百分比"),
    ]

    return categories, nodes, links


def get_achive_data(model_name, model):
    events = model.event.get_queryset()
    ratio = '{:.2f}%'.format(model.number / Event.objects.count() * 100)
    unit_list = {}

    for event in events:
        unit = event.dispose_unit.name
        if unit in unit_list:
            unit_list[unit] += 1
        else:
            unit_list.update({unit: 1})

    number_max = 0
    for key in unit_list:
        if unit_list[key] > number_max:
            unit = key
            number_max = unit_list[key]

    categories = [
        opts.GraphCategory(name="执行情况"),
        opts.GraphCategory(name="数量"),
        opts.GraphCategory(name="处置部门"),
        opts.GraphCategory(name="百分比"),
    ]

    nodes = [
        opts.GraphNode(name=str(model.name), symbol_size=80, category=0),
        opts.GraphNode(name=str(model.number), symbol_size=50, category=1),
        opts.GraphNode(name=unit, symbol_size=50, category=2),
        opts.GraphNode(name=ratio, symbol_size=50, category=3),
    ]

    links = [
        opts.GraphLink(source=str(model.name), target=str(model.number), value="事件数量"),
        opts.GraphLink(source=str(model.name), target=unit, value="最多 " + str(model.name) + " 处置机构"),
        opts.GraphLink(source=str(model.name), target=ratio, value="事件占比"),
    ]
    return categories, nodes, links


def set_number_node(model, categories, nodes, links):
    value = str(getattr(model, 'number'))
    categories.append(opts.GraphCategory(name='数量'))
    index = len(categories) - 1
    nodes.append(opts.GraphNode(name=value, symbol_size=50, category=index))
    links.append(opts.GraphLink(source=str(model), target=value, value='事件总数量'))

    return 0


def set_type_node(model_name, model, categories, nodes, links):
    if model_name == 'SubType':
        sub_model = model
        model = model.main_type

    thetype = model.type
    type_number = model.type.number
    name = '类型'
    categories.append(opts.GraphCategory(name=name))
    index = len(categories) - 1
    value = str(thetype)
    if (model_name == 'SubType' and value == str(sub_model)) or value == str(model):
        value = value + '（问题类型）'
    nodes.append(opts.GraphNode(name=value, symbol_size=50, category=index,value=type_number))
    links.append(opts.GraphLink(source=str(model), target=value, value='类型'))

    return 0


def set_max_community_node(model_name, model, categories, nodes, links):
    max_num = 0
    communities = Community.objects.all()
    if model_name == 'MainType':
        subtypes = SubType.objects.filter(main_type=model)
        for community in communities:
            events = Event.objects.filter(sub_type__in=subtypes, community=community)
            now_num = len(events)
            if now_num > max_num:
                max_num = now_num
                max_community = community
    if model_name == 'SubType':
        for community in communities:
            events = Event.objects.filter(sub_type=model, community=community)
            now_num = len(events)
            if now_num > max_num:
                max_num = now_num
                max_community = community
    if model_name == 'Type':
        maintypes = MainType.objects.filter(type=model)
        subtypes = SubType.objects.filter(main_type__in=maintypes)
        for community in communities:
            events = Event.objects.filter(sub_type__in=subtypes, community=community)
            now_num = len(events)
            if now_num > max_num:
                max_num = now_num
                max_community = community
    name = '社区'
    categories.append(opts.GraphCategory(name=name))
    index = len(categories) - 1
    value = str(max_community)
    nodes.append(opts.GraphNode(name=value, value=str(max_num), symbol_size=50, category=index))
    links.append(opts.GraphLink(source=str(model), target=value, value='发生最多的社区'))


def get_maintype_data(model):
    number = model.number
    categories = [opts.GraphCategory(name='大类')]
    nodes = [opts.GraphNode(name=str(model), symbol_size=100, category=0,value=number)]
    links = []
    # 事件数量
    set_number_node(model, categories, nodes, links)
    # 所属类型
    set_type_node('MainType', model, categories, nodes, links)
    # 事件最多社区
    set_max_community_node('MainType', model, categories, nodes, links)

    subtypes = SubType.objects.filter(main_type=model)
    name = '小类'
    categories.append(opts.GraphCategory(name=name))
    index = len(categories)-1
    for subtype in subtypes:
        value = str(subtype)
        sub_number = subtype.number
        if value == str(model) or value == str(model.type):
            value = value + '（问题小类）'
        nodes.append(opts.GraphNode(name=value, symbol_size=50, category=index, value=sub_number))
        links.append(opts.GraphLink(source=str(model), target=value, value='下属小类'))

    return categories, nodes, links


def get_type_data(model):
    number = model.number
    categories = [opts.GraphCategory(name='类型')]
    nodes = [opts.GraphNode(name=str(model), symbol_size=100, category=0,value=number)]
    links = []
    # 事件总数量
    set_number_node(model, categories, nodes, links)
    # 事件最多社区
    set_max_community_node('Type', model, categories, nodes, links)
    # 类型下所有大类
    maintypes = MainType.objects.filter(type=model)
    name = '大类'
    categories.append(opts.GraphCategory(name=name))
    index = len(categories) - 1
    for maintype in maintypes:
        value = str(maintype)
        number = maintype.number
        if value == str(model):
            value = value + '（问题大类）'
        nodes.append(opts.GraphNode(name=value, symbol_size=50, category=index,value=number))
        links.append(opts.GraphLink(source=str(model), target=value, value='下属大类'))

    return categories, nodes, links


def get_street_data(model_name, model):
    categories = [opts.GraphCategory(name='街道')]
    str_number = model.number
    nodes = [opts.GraphNode(name=str(model), symbol_size=80, category=0, value=str_number)]
    links = []

# 街道所属区域
    districts = District.objects.all()
    for district in districts:
        number_c = district.number
        name_c = district.name
        if name_c == 'name' or name_c == 'id':
            continue
        value_c = str(district)
        categories.append(opts.GraphCategory(name='区域'))
        index_c = len(categories)-1
        nodes.append(opts.GraphNode(name=value_c, symbol_size=60, category=index_c,value=number_c))
        links.append(opts.GraphLink(source=str(model), target=value_c, value='所属区域'))

# 街道下所有社区及其数量
    communities = Community.objects.filter(street=model)
    for community in communities:
        name_c = Community.name
        number_c = community.number
        # ratio_c = str((round(number_c*100/str_number,2)))+'%'
        if name_c == 'name' or name_c == 'id':
            continue
        value_c = str(community)
        categories.append(opts.GraphCategory(name='社区'))
        index_c = len(categories)-1
        nodes.append(opts.GraphNode(name=value_c, symbol_size=40, category=index_c,value=number_c))
        links.append(opts.GraphLink(source=str(model), target=value_c, value='下属社区'))

    return categories, nodes, links


def get_district_data(model_name, model):
    categories = [opts.GraphCategory(name='区域')]
    number_d = model.number
    nodes = [opts.GraphNode(name=str(model), symbol_size=80, category=0,value=number_d)]
    links = []

    streets = Street.objects.filter(district=model)
    for street in streets:
        name_s = Street.name
        number_s = street.number
        if name_s == 'name' or name_s == 'id':
            continue
        value_s = str(street)
        categories.append(opts.GraphCategory(name='街道'))
        index_s = len(categories)-1
        nodes.append(opts.GraphNode(name=value_s, symbol_size=60, category=index_s,value=number_s))
        links.append(opts.GraphLink(source=str(model), target=value_s, value='下属街道'))

    return categories, nodes, links


# 小类
def get_subtype_data(model_name, model):
    categories = [opts.GraphCategory(name='小类')]
    number = model.number
    nodes = [opts.GraphNode(name=str(model), symbol_size=100, category=0, value=number)]
    links = []

    id = SubType.objects.filter(name=str(model)).values("id")[0]['id']
    sub_model = SubType.objects.filter(id=id)[0]

    try:
        # 小类所属大类
        node_name = str(sub_model.main_type)
        # print(node_name)
        cate_name = '大类'
        link_name = '所属大类'
        source_node = str(model)
        maintype_number = sub_model.main_type.number

        create_node(source_node, categories, cate_name, nodes, node_name, links, link_name, node_value=maintype_number)

        # 小类发生最多的社区名
        coms = Event.objects.filter(sub_type_id=id).values('community').annotate(count=Count('community')).values(
            'community', 'count').order_by('-count')
        coms = list(coms)
        com = coms[0]
        com_name = Community.objects.get(id=com['community']).name
        print(com_name)

        node_name = com_name
        cate_name = '社区'
        link_name = '小类发生最多社区'
        source_node = str(model)

        create_node(source_node, categories, cate_name, nodes, node_name, links, link_name, node_value=str(com['count']))

        # 小类编号
        sub_model = SubType.objects.filter(id=id)[0]
        aid = sub_model.aID

        node_name = str(aid)
        cate_name = '编号'
        link_name = '小类编号'
        source_node = str(model)

        create_node(source_node, categories, cate_name, nodes, node_name, links, link_name)

        # 小类事件总数
        node_name = str(sub_model.number)
        print(node_name)
        cate_name = '数量'
        link_name = '事件总数'
        source_node = str(model)

        create_node(source_node, categories, cate_name, nodes, node_name, links, link_name, node_value=node_name)

    except Exception as e:
        print(e)

    return categories, nodes, links


def get_disposeunit_data(model_name, model):
    number_dis = str(model.number)
    categories = [opts.GraphCategory(name='执行部门')]
    nodes = [opts.GraphNode(name=str(model), symbol_size=100, category=0, value=number_dis)]
    links = []

    id = DisposeUnit.objects.filter(name=str(model)).values("id")[0]['id']
    dis_model = DisposeUnit.objects.filter(id=id)[0]

    try:
        # 事件总数
        node_name = str(dis_model.number)
        print(node_name)
        cate_name = '数量'
        link_name = '事件总数'
        source_node = str(dis_model)

        create_node(source_node, categories, cate_name, nodes, node_name, links, link_name)

        # 完成事件百分比
        is_achieve_count = Event.objects.filter(dispose_unit=id).values('achieve').annotate(count=Count('achieve')).values('achieve','count').order_by('-count')
        is_achieve_count = list(is_achieve_count)
        print(is_achieve_count)
        y = is_achieve_count[0]['count']
        n = is_achieve_count[1]['count']
        percent = round(y * 100 / (y + n), 2)

        node_name = str(percent) + '%'
        cate_name = '百分比'
        link_name = '完成事件百分比'

        create_node(source_node, categories, cate_name, nodes, node_name, links, link_name)

        # 部门编号
        aid = dis_model.aID

        node_name = str(aid)
        cate_name = '编号'
        link_name = '部门编号'

        create_node(source_node, categories, cate_name, nodes, node_name, links, link_name)

    except Exception as e:
        print(e)

    return categories, nodes, links


# 社区
def get_community_data(model_name, model):
    com_number = model.number
    categories = [opts.GraphCategory(name='社区')]
    nodes = [opts.GraphNode(name=str(model), symbol_size=100, category=0,value=com_number)]
    links = []

    id = Community.objects.filter(name=str(model)).values("id")[0]['id']
    com_model = Community.objects.filter(id=id)[0]

    try:
        # 社区所属街道
        str_number = com_model.street.number
        node_name = str(com_model.street)
        print(node_name)
        cate_name = '街道'
        link_name = '所属街道'
        source_node = str(com_model)

        create_node(source_node, categories, cate_name, nodes, node_name, links, link_name,node_value= str_number)

        # 编号
        aid = com_model.aID
        node_name = str(aid)
        cate_name = '编号'
        link_name = '社区编号'

        create_node(source_node, categories, cate_name, nodes, node_name, links, link_name)

        # 事件最多类型
        type_count = Event.objects.filter(community=id).values('type').annotate(count=Count('type')).values('type','count').order_by('-count')
        type_count = list(type_count)

        tid = type_count[0]['type']
        t = Type.objects.filter(id=tid)[0]
        c = type_count[0]['count']

        node_name = str(t)
        cate_name = '类型'
        link_name = '事件最多类型'

        create_node(source_node, categories, cate_name, nodes, node_name, links, link_name, node_value=str(c))

        # 社区事件总数
        node_name = str(com_model.number)
        # print(node_name)
        cate_name = '数量'
        link_name = '事件总数'

        create_node(source_node, categories, cate_name, nodes, node_name, links, link_name)

        # 事件占街道百分比
        strt = com_model.street

        x = com_model.number
        y = strt.number
        percentage = round(x*100/y, 2)

        cate_name = '百分比'
        node_name = str(percentage)+'%'
        link_name = '事件占街道百分比'

        create_node(source_node, categories, cate_name, nodes, node_name, links, link_name)
    except Exception as e:
        print(e)

    return categories, nodes, links


def wordcloud():
    data = []
    f = random.randint(0, 10)
    t = random.randint(20, 30)
    type_models = list(SubType.objects.order_by('?')[f:t])
    main_models = list(MainType.objects.order_by('?')[f:t])
    sub_models = list(SubType.objects.order_by('?')[f:t])
    dis_models = list(District.objects.order_by('?')[f:t])
    str_models = list(Street.objects.order_by('?')[f:t])
    com_models = list(Community.objects.order_by('?')[f:t])

    models = type_models + main_models + sub_models + dis_models + com_models + str_models

    for model in models:
        data.append((str(model.name),str(model.number)))

    print(data)

    c = (
        WordCloud()
        .add(series_name="wordcloud", data_pair=data, word_size_range=[20, 200])
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title='', title_textstyle_opts=opts.TextStyleOpts(font_size=23)
            ),
            tooltip_opts=opts.TooltipOpts(is_show=True),
        )
        .dump_options_with_quotes()
        # .render("basic_wordcloud.html")
    )
    return c


def random_get(array, num):
    ran_list = []
    length = len(array)
    for i in range(num):
        ran_num = random.randint(0, length-1)
        ran_data = array[ran_num]
        while ran_data in ran_list:
            ran_num = random.randint(0, length-1)
            ran_data = array[ran_num]
        ran_list.append(ran_data)
    return ran_list


def get_word():
    data = []
    for item in word_item:
        item_models = random_get(list(item.objects.order_by('?')), 3)
        for model in item_models:
            data.append(str(model.name))

    print(data)

    return data
