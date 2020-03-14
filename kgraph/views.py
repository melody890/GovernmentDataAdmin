from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from pyecharts.charts import Graph
from pyecharts import options as opts

from event.views import filter_model


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
        else:
            kgraph = ""
            print("None")
    else:
        kgraph = ""

    context = {
        'graph': kgraph,
        'kg_search': search
    }
    return render(request, 'kgraph/kgraph.html', context)


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
            gravity=0.1,
            repulsion=200,
            linestyle_opts=opts.LineStyleOpts(color="black", curve=0.2),
            label_opts=opts.LabelOpts(is_show=True, position='inside', font_size=20),
            is_draggable=True,
            is_rotate_label=True,
            edge_length=200,
            edge_label=opts.LabelOpts(
                is_show=True,
                position="middle",
                font_size=15,
                formatter="{b}"
            )
        )
        .set_global_opts(
            legend_opts=opts.LegendOpts(is_show=True),
            title_opts=opts.TitleOpts(title=str(model)),
        )
        .dump_options_with_quotes()
    )

    return c


def get_data(model_name, model):
    field_data = model._meta.fields
    categories = [opts.GraphCategory(name=model_name)]
    nodes = [opts.GraphNode(name=str(model), symbol_size=80, category=0)]
    links = []
    for data in field_data:
        name = data.attname
        if name == 'name' or name == 'id':
            continue
        value = str(getattr(model, data.attname))
        categories.append(opts.GraphCategory(name=name))
        index = len(categories)-1
        nodes.append(opts.GraphNode(name=value, symbol_size=50, category=index))
        links.append(opts.GraphLink(source=str(model), target=value, value=50))

    return categories, nodes, links
