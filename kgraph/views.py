from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from pyecharts.charts import Graph
from pyecharts import options as opts


@login_required(login_url='/user/login/')
def get_kgraph(request):
    search = request.GET.get('search')
    kgraph = graph(search)
    context = {
        'graph': kgraph,
    }
    return render(request, 'kgraph/kgraph.html', context)


def graph(search) -> Graph:
    (categories, nodes, links) = get_data(search)

    c = (
        Graph(
            init_opts=opts.InitOpts(width="1600px", height="800px")
        )
        .add(
            "",
            nodes=nodes,
            links=links,
            categories=categories,
            repulsion=100,
            linestyle_opts=opts.LineStyleOpts(color="black", curve=0.2),
            label_opts=opts.LabelOpts(is_show=True, position='inside', font_size=20),
            is_draggable=True,
            is_rotate_label=True,
            edge_label=opts.LabelOpts(
                is_show=True,
                position="middle",
                font_size=15,
                formatter="{b}"
            )
        )
        .set_global_opts(
            legend_opts=opts.LegendOpts(is_show=True),
            title_opts=opts.TitleOpts(title="知识图谱示例"),
        )
        .dump_options_with_quotes()
    )

    return c


def get_data(search):

    categories = [
        opts.GraphCategory(name="Root"),
        opts.GraphCategory(name="first"),
        opts.GraphCategory(name="second"),
    ]

    nodes = [
        opts.GraphNode(name="坪山街道", symbol_size=50, category=0),
        opts.GraphNode(name="坪山区", symbol_size=40, category=1),
        opts.GraphNode(name="200", symbol_size=40, category=1),
        opts.GraphNode(name="诉求", symbol_size=40, category=1),
        opts.GraphNode(name="社区", symbol_size=40, category=1),
        opts.GraphNode(name="和平社区", symbol_size=30, category=2),
        opts.GraphNode(name="坪山社区", symbol_size=30, category=2),
        opts.GraphNode(name="六和社区", symbol_size=30, category=2),
        opts.GraphNode(name="六联社区", symbol_size=30, category=2),
    ]

    links = [
        opts.GraphLink(source="坪山街道", target="坪山区", value=50),
        opts.GraphLink(source="坪山街道", target="200", value=50),
        opts.GraphLink(source="坪山街道", target="诉求", value=50),
        opts.GraphLink(source="坪山街道", target="社区", value=50),
        opts.GraphLink(source="社区", target="和平社区", value=20),
        opts.GraphLink(source="社区", target="坪山社区", value=20),
        opts.GraphLink(source="社区", target="六和社区", value=20),
        opts.GraphLink(source="社区", target="六联社区", value=20),
    ]

    return categories, nodes, links
