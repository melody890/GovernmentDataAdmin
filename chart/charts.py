import datetime
import random
import json
from datetime import timedelta, date

from pyecharts.charts import Sunburst, BMap, Line, WordCloud, Pie, Calendar
from pyecharts.faker import Faker
from pyecharts import options as opts
from pyecharts.globals import SymbolType, GeoType, ThemeType

from event.models import Event, Street, Type, Property, Achieve, DisposeUnit, Community, EventSource, MainType

BAIDU_MAP_AK = 'X3ATCKQWRjRxLNLI1Wv9NiTMFAa5bh8W'


def get_date(days):
    day = (date.today() - timedelta(days=495) - timedelta(days=days))
    return day


def get_recent_date(num):
    date_list = []
    for i in range(num):
        day = get_date(num - i + 20)

        date_list.append(day)

    return date_list


class Charts:
    def __init__(self):
        self.event_list = Event.objects.all()
        self.street_list = Street.objects.all()
        self.type_list = Type.objects.all()
        self.main_type_list = MainType.objects.all()
        self.property_list = Property.objects.all()
        self.unit_list = DisposeUnit.objects.all()
        self.community_list = Community.objects.all()
        self.src_list = EventSource.objects.all()
        self.pie = self.pie_base()
        self.wordcloud = self.wordcloud_base()
        self.sunburst = self.sunburst_base()
        self.calendar = self.calendar_base()
        self.map = self.map_base()
        # self.all()

    def all(self):
        start = datetime.datetime.now()
        for event in self.event_list:
            event.type = event.sub_type.main_type.type
            event.save()

        end = datetime.datetime.now()
        print("all: " + str(end - start))

    def get_sunburst_data(self):
        sun_data = []
        statuses = Achieve.objects.all()
        for status in statuses:
            type_value = {}
            for v in self.type_list:
                type_value.update({v.name: 0})

            events = status.event.get_queryset()

            for event in events:
                type_value[event.type.name] += 1

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
        start = datetime.datetime.now()
        data = self.get_sunburst_data()
        c = (
            Sunburst()
                .add(series_name="", data_pair=data, radius=[0, "90%"])
                .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}"))
                .dump_options_with_quotes()
        )
        end = datetime.datetime.now()
        print("Sunburst: " + str(end - start))
        return c

    def get_word_data(self):
        words = []

        def append_data(data_list):
            value_list = []
            for data in data_list:
                value_list.append((data.name, data.number))

            def take_second(elem):
                return elem[1]

            value_list.sort(key=take_second)
            words.append(value_list[-1])

        append_data(self.unit_list)
        append_data(self.property_list)
        append_data(self.community_list)
        append_data(self.src_list)
        append_data(self.type_list)
        append_data(self.main_type_list)

        return words

    def wordcloud_base(self) -> WordCloud:
        start = datetime.datetime.now()
        words = self.get_word_data()
        c = (
            WordCloud()
                .add("", words, word_size_range=[20, 80], shape=SymbolType.DIAMOND)
                .dump_options_with_quotes()
        )
        end = datetime.datetime.now()
        print("Wordcloud: " + str(end - start))
        return c

    def get_pie_data(self, name_list, value_list):
        for event in self.event_list:
            value_list[name_list.index(event.property.name)] += 1

        return value_list

    def pie_base(self) -> Pie:
        start = datetime.datetime.now()
        data = []
        data_value = []
        for pro in self.property_list:
            data.append(pro.name)
            data_value.append(pro.number)

        c = (
            Pie(init_opts=opts.InitOpts(theme=ThemeType.WESTEROS))
            .add("", [list(z) for z in zip(data, data_value)])
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
            .dump_options_with_quotes()
        )
        end = datetime.datetime.now()
        print("Pie: " + str(end - start))
        return c

    def get_line_data(self, date_list, street_name, info):

        for event in self.event_list:
            event_time = event.create_time
            if event_time < date_list[0]:
                break

            if event.community.street.name != street_name:
                continue

            for value in date_list:
                if value == event_time:
                    info[event.property.name][date_list.index(value)] += 1
                    break
        return info

    def get_line_all(self, date_list, info):
        for event in self.event_list:
            event_time = event.create_time

            if event_time < date_list[0]:
                break

            for value in date_list:
                if value == event_time:
                    info[event.property.name][date_list.index(value)] += 1

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
        c = (
            Line()
            .add_xaxis(date_list)
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
        start = datetime.datetime.now()
        line_info = {
            "all": self.line_base()
        }
        for street in self.street_list:
            line = self.line_base(street=street.name)
            line_info.update({street.name: line})
        end = datetime.datetime.now()
        print("Line: " + str(end - start))
        return line_info

    def calendar_base(self) -> Calendar:
        start = datetime.datetime.now()

        begin = get_date(365)
        end = datetime.date.today() - timedelta(days=465)
        data = []
        cur_day = end
        count = 0
        for event in self.event_list:
            if event.create_time < cur_day:
                data.insert(0, (cur_day, count))
                count = 0
                cur_day -= timedelta(days=1)

            if cur_day < begin:
                break

            if event.create_time == cur_day:
                count += 1

        c = (
            Calendar()
            .add("",
                 data,
                 calendar_opts=opts.CalendarOpts(
                     range_=[begin, end],
                     daylabel_opts=opts.CalendarDayLabelOpts(name_map="cn"),
                     monthlabel_opts=opts.CalendarMonthLabelOpts(name_map="cn"),
                     pos_right="20px"
                 ),
                 )
            .set_global_opts(
                visualmap_opts=opts.VisualMapOpts(
                    max_=501,
                    min_=1,
                    orient="horizontal",
                    is_piecewise=True,
                    pos_left="40px"
                ),
            )
            .dump_options_with_quotes()
        )

        end = datetime.datetime.now()
        print("Calendar: " + str(end - start))
        return c

    def map_base(self) -> BMap:
        start = datetime.datetime.now()

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
            if community.number:
                c.add_coordinate(community.name, community.long, community.lat)
                c.add(
                    "heat",
                    [(community.name, community.number)],
                    label_opts=opts.LabelOpts(formatter="{d}"),
                    color="red",
                )
        end = datetime.datetime.now()
        print("Map: " + str(end - start))
        return c.dump_options_with_quotes()
