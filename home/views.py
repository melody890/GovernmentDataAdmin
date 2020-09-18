from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from pyecharts.charts import Pie, Line, Gauge, Bar, WordCloud
from pyecharts.faker import Faker
from pyecharts import options as opts

from event.models import Property, Street,Event
from chart.charts import Charts,get_recent_date

from django.db.models import Count

from datetime import timedelta, date

@login_required(login_url='/user/login/')
def dashboard(request):
    pie = index_pie()
    gauge = index_gauge()
    post_chart = post_line()
    dispose_chart = dispose_line()
    street_chart = street_bar()
    wordcloud_chart = word_cloud()
    charts = Charts()
    streets = Street.objects.all()
    context = {
        'streets': streets,
        'cur_page': "dashboard",
        'pie_chart': pie,
        'gauge_chart': gauge,
        'line_charts': charts.get_line(),#最近事件曲线图
        'post_line': post_chart,
        'dispose_line': dispose_chart,
        'street_bar':street_chart,
        'word_cloud':wordcloud_chart,
    }
    return render(request, "home/dashboard.html", context)


def error_page(request, info):
    context = {
        "info": info,
    }
    return render(request, "home/error.html", context)


def index_pie() -> Pie:
    data = []
    properties = Property.objects.all()
    for pro in properties:
        data.append(pro.name)
    c = (
        Pie()
        .add(
            "",
            [list(z) for z in zip(data, Faker.values())],
            label_opts=opts.LabelOpts(is_show=False),
            radius="60%"
        )
        .set_global_opts(legend_opts=opts.LegendOpts(is_show=False))
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}"))
        .dump_options_with_quotes()
    )
    return c


def index_gauge() -> Gauge:
    # date_list = get_recent_date(7)
    # #分别记录全部事件数目和完成事件数目
    # all_event_count = 0
    # done_event_count = 0
    # for date in date_list:
    #     format_date = date.strftime('%Y-%m-%d')
    #     sql = Event.objects.filter(create_time=format_date).values('achieve').annotate(count=Count('achieve')).values('achieve','count').order_by('achieve')
    #     achieve = list(sql)
    #     # print(achieve[0]['count'])
    # all_event_count = all_event_count + achieve[0]['count'] + achieve[1]['count']
    # done_event_count = done_event_count + achieve[0]['count']

    # done_percent = (done_event_count/all_event_count)
    done_percent = 0
    done_percent = round(done_percent*100,1)

    c = (
        Gauge()
        .add("",
             [("", done_percent)],
             radius="100%",
             # title_label_opts=opts.LabelOpts(
             #     font_size=10, font_family="Microsoft YaHei"
             # ),
        )

        .dump_options_with_quotes()
    )
    return c


def post_line() -> Line:
    x_data = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    y_data = [820, 932, 901, 934, 1290, 1330, 1320]

    c = (
        Line()
        .add_xaxis(x_data)
        .add_yaxis(
            series_name="",
            y_axis=y_data,
            is_symbol_show=False,
            label_opts=opts.LabelOpts(is_show=False),
            areastyle_opts=opts.AreaStyleOpts(opacity=1, color="#C67570")
        )
        .set_global_opts(
            yaxis_opts=opts.AxisOpts(is_show=False),
            xaxis_opts=opts.AxisOpts(is_show=False, type_="category", boundary_gap=False)
        )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}"))
        .dump_options_with_quotes()
    )
    return c


def dispose_line() -> Line:
    x_data = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    y_data = [82, 932, 901, 934, 1290, 1330, 1320]

    c = (
        Line()
        .add_xaxis(x_data)
        .add_yaxis(
            series_name="",
            y_axis=y_data,
            is_symbol_show=False,
            label_opts=opts.LabelOpts(is_show=False),
            areastyle_opts=opts.AreaStyleOpts(opacity=1, color="#40a0c0")
        )
        .set_global_opts(
            yaxis_opts=opts.AxisOpts(is_show=False),
            xaxis_opts=opts.AxisOpts(is_show=False, type_="category", boundary_gap=False)
        )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}"))
        .dump_options_with_quotes()
    )
    return c


def street_bar() -> Bar:
    x_data = ["坪山街道", "坑梓街道", "碧岭街道", "龙田街道", "马峦街道", "石井街道"]
    y_data = [82, 51, 93, 90, 30, 20]

    c = (
        Bar()
            .add_xaxis(
            x_data,
        )
            .add_yaxis(
            "",
            y_data,
        )
            .set_global_opts(
            yaxis_opts=opts.AxisOpts(is_show=False),
            xaxis_opts=opts.AxisOpts(is_show=False, type_="category", boundary_gap=False)
        )
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .dump_options_with_quotes()
    )
    return c


def word_cloud() -> WordCloud:
    words = [('坪山街道','13'),("社区建设",'24'),("房地产",'2'),("乱摆卖",'10'),("沙坣社区",'19'),("市容城管",'18'),("树木养护",'14')]
    c = (
        WordCloud()
            .add(
            "",
            words,
            word_size_range=[10, 30],
            # rotate_step=0,
            textstyle_opts=opts.TextStyleOpts(font_size=20,font_weight='bold')
        )
            .dump_options_with_quotes()
    )
    return c