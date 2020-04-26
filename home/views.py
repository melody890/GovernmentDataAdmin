from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from pyecharts.charts import Pie, Line
from pyecharts.faker import Faker
from pyecharts import options as opts

from event.models import Property, Street
from chart.charts import Charts


@login_required(login_url='/user/login/')
def dashboard(request):
    pie = index_pie()
    post_chart = post_line()
    dispose_chart = dispose_line()
    charts = Charts()
    streets = Street.objects.all()
    context = {
        'streets': streets,
        'cur_page': "dashboard",
        'pie_chart': pie,
        'line_charts': charts.get_line(),#最近事件曲线图
        'post_line': post_chart,
        'dispose_line': dispose_chart,
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
