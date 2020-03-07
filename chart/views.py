from django.shortcuts import render
from rest_framework.views import APIView

from event.models import Street
from .charts import Charts


BAIDU_MAP_AK = 'X3ATCKQWRjRxLNLI1Wv9NiTMFAa5bh8W'


class IndexView(APIView):
    def get(self, request, *args, **kwargs):
        streets = Street.objects.all()
        charts = Charts()
        context = {
            'streets': streets,
            'pie_chart': charts.pie,
            'line_charts': charts.get_line(),
            'sunburst_chart': charts.sunburst,
            'map_chart': charts.map,
            'calendar_chart': charts.calendar,
            'wordcloud_chart': charts.wordcloud,
        }
        return render(request, 'chart/charts.html', context)
