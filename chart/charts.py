import datetime
import random
import json
from datetime import timedelta, date

from pyecharts.charts import Sunburst, BMap, Line, WordCloud, Pie, Calendar
from pyecharts.faker import Faker
from pyecharts import options as opts
from pyecharts.globals import SymbolType, GeoType
from pyecharts.datasets import register_url

from event.models import Event, Street, Type, Property, Achieve, DisposeUnit, Community, EventSource


BAIDU_MAP_AK = 'X3ATCKQWRjRxLNLI1Wv9NiTMFAa5bh8W'


def get_date(days):
    day = (date.today() - timedelta(days=days))
    return day


def get_recent_date(num):
    date_list = []
    for i in range(num):
        day = get_date(num-i)
        date_info = [day.year, day.month, day.day]
        date_list.append(date_info)

    return date_list


class Charts:
    def __init__(self):
        self.event_list = Event.objects.all()
        self.street_list = Street.objects.all()
        self.type_list = Type.objects.all()
        self.property_list = Property.objects.all()
        self.unit_list = DisposeUnit.objects.all()
        self.community_list = Community.objects.all()
        self.src_list = EventSource.objects.all()
        self.pie = self.pie_base()
        self.wordcloud = self.wordcloud_base()
        self.sunburst = self.sunburst_base()
        self.calendar = self.calendar_base()
        self.map = self.map_base()

    def get_sunburst_data(self):
        sun_data = []
        statuses = Achieve.objects.all()
        for status in statuses:
            type_value = {}
            for v in self.type_list:
                type_value.update({v.name: 0})

            for event in self.event_list:
                if event.achieve == status:
                    type_value[event.sub_type.main_type.type.name] += 1

            time_list = []
            for key in type_value.keys():
                if type_value[key]:
                    single = opts.SunburstItem(name=key, value=type_value[key])
                    time_list.append(single)

            if len(time_list):
                name = status.name
                s_item = opts.SunburstItem(name=name, children=time_list)
                sun_data.append(s_item)

        return sun_data

    def sunburst_base(self) -> Sunburst:
        data = self.get_sunburst_data()
        c = (
            Sunburst()
            .add(series_name="", data_pair=data, radius=[0, "90%"])
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}"))
            .dump_options_with_quotes()
        )
        return c

    def get_word_data(self):
        words = []
        units = []
        properties = []
        communities = []
        sources = []

        for unit in self.unit_list:
            units.append((unit.name, unit.event.count()))
        for pro in self.property_list:
            properties.append((pro.name, pro.event.count()))
        for community in self.community_list:
            communities.append((community.name, community.event.count()))
        for src in self.src_list:
            sources.append((src.name, src.event.count()))

        def take_second(elem):
            return elem[1]

        units.sort(key=take_second)
        properties.sort(key=take_second)
        communities.sort(key=take_second)
        sources.sort(key=take_second)
        words.append(units[-1])
        words.append(properties[-1])
        words.append(communities[-1])
        words.append(sources[-1])

        return words

    def wordcloud_base(self) -> WordCloud:
        words = self.get_word_data()
        c = (
            WordCloud()
            .add("", words, word_size_range=[30, 80], shape=SymbolType.DIAMOND)
            # .render()
            .dump_options_with_quotes()
        )
        return c

    def get_pie_data(self, name_list, value_list):
        for event in self.event_list:
            value_list[name_list.index(event.property.name)] += 1

        return value_list

    def pie_base(self) -> Pie:
        data = []
        data_value = []
        for pro in self.property_list:
            data.append(pro.name)
            data_value.append(0)
        data_value = self.get_pie_data(data, data_value)

        c = (
            Pie()
            .add("", [list(z) for z in zip(data, data_value)])
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
            .dump_options_with_quotes()
        )
        return c

    def get_line_data(self, date_list, street, info):
        for event in self.event_list:
            event_time = event.create_time
            if event.community.street.name != street:
                continue
            for value in date_list:
                if value[2] == event_time.day and value[1] == event_time.month and value[0] == event_time.year:
                    info[event.property.name][date_list.index(value)] += 1
                    break
        return info

    def get_line_all(self, date_list, info):
        for event in self.event_list:
            event_time = event.create_time
            for value in date_list:
                if value[2] == event_time.day and value[1] == event_time.month and value[0] == event_time.year:
                    info[event.property.name][date_list.index(value)] += 1
                    break

        return info

    def line_base(self, street=None) -> Line:
        info = {}
        properties = Property.objects.all()
        for pro in properties:
            info.update({pro.name: [0, 0, 0, 0, 0, 0, 0]})
        date_list = get_recent_date(7)
        if street:
            info = self.get_line_data(date_list, street, info)
        else:
            info = self.get_line_all(date_list, info)
        week_list = []
        for value in date_list:
            day = str(value[1]) + '-' + str(value[-1])
            week_list.append(day)
        c = (
            Line()
            .add_xaxis(week_list)
        )
        for key in info.keys():
            c.add_yaxis(key, info[key], is_smooth=True)
        c.set_series_opts(
            # areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
            label_opts=opts.LabelOpts(is_show=False),
            linestyle_opts=opts.LineStyleOpts(width=2)
        )
        c.set_global_opts(
            xaxis_opts=opts.AxisOpts(
                axistick_opts=opts.AxisTickOpts(is_align_with_label=True),
                is_scale=False,
                boundary_gap=False,
            ),
        )
        c = c.dump_options_with_quotes()
        return c

    def get_line(self):
        line_info = {
            "all": self.line_base()
        }
        for street in self.street_list:
            line = self.line_base(street=street.name)
            line_info.update({street.name: line})

        return line_info

    def calendar_base(self) -> Calendar:
        begin = get_date(365)
        end = datetime.date.today()
        max_num = 0
        data = []
        for i in range((end-begin).days+1):
            cur_day = begin+timedelta(days=i)
            count = 0
            for event in self.event_list:
                if event.create_time == cur_day:
                    count += 1
            data.append((cur_day, count))
            if count > max_num:
                max_num = count

        c = (
            Calendar()
            .add("",
                 data,
                 calendar_opts=opts.CalendarOpts(range_=[begin, end])
                 )
            .set_global_opts(
                visualmap_opts=opts.VisualMapOpts(
                    max_=1001,
                    min_=1,
                    orient="horizontal",
                    is_piecewise=True,
                    pos_top="230px",
                    pos_left="100px",
                ),
            )
            .dump_options_with_quotes()
        )
        return c

    def map_base(self) -> BMap:
        location = []

        c = (
            BMap()
            .add_schema(baidu_ak=BAIDU_MAP_AK, center=[114.34632, 22.69084], zoom=13)
            .add(
                "bmap",
                location,
                type_='line',
                label_opts=opts.LabelOpts(formatter="{b}"),
            )
            .set_global_opts(
                visualmap_opts=opts.VisualMapOpts(),
            )
        )

        for community in self.community_list:
            count = community.event.count()
            if count:
                c.add_coordinate(community.name, community.long, community.lat)
                c.add(
                    "heat",
                    [(community.name, count)],
                    label_opts=opts.LabelOpts(formatter="{d}"),
                    color="red",
                )
        return c.dump_options_with_quotes()
