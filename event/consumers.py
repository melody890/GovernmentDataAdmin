from channels.generic.websocket import WebsocketConsumer
from django.db.models import Q
import json

from .models import MainType, Type, Street, Event, Achieve
from .views import my_filter


class PostDataConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        src = text_data_json['src']
        if src == 'sub':
            main_name = text_data_json['main_type']
            main_type = MainType.objects.get(name=main_name)
            sub_list = main_type.sub_type.all()
            sub_types = []
            for sub in sub_list:
                sub_types.append(sub.name)
            self.send(text_data=json.dumps({
                "sub_types": sub_types,
            }))
        elif src == 'main':
            type_name = text_data_json['type']
            event_type = Type.objects.get(name=type_name)
            main_list = event_type.main_type.all()
            main_types = []
            for sub in main_list:
                main_types.append(sub.name)
            self.send(text_data=json.dumps({
                "main_types": main_types,
            }))
        elif src == 'community':
            street_name = text_data_json['street']
            street = Street.objects.get(name=street_name)
            community_list = street.community.all()
            communities = []
            for sub in community_list:
                communities.append(sub.name)
            self.send(text_data=json.dumps({
                "communities": communities,
            }))


class ListDataConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        method = text_data_json['method']
        search = text_data_json['search']
        event_type = text_data_json['event_type']
        status = text_data_json['status']
        property_name = text_data_json['property']

        if method != 'filter':
            rec_id = int(text_data_json['rec_id'])
            event = Event.objects.get(rec_id=rec_id)
            achieve = Achieve.objects.get(status=method)
            event.achieve = achieve
            event.save()

        event_list = Event.objects.all()
        length = len(event_list)

        if search:
            event_list = my_filter(search, event_list)

        if event_type:
            event_list = event_list.filter(
                Q(sub_type__main_type__type__name=event_type)
            )

        if property_name:
            event_list = event_list.filter(
                Q(property__name=property_name)
            )

        if status:
            if status == "处理中":
                event_list = event_list.filter(
                    Q(achieve=2)
                )
            elif status == "按期结办":
                event_list = event_list.filter(
                    Q(achieve=1)
                )
            elif status == "逾期结办":
                event_list = event_list.filter(
                    Q(achieve=3)
                )

        dis_list = []
        hide_list = []
        for event in event_list:
            dis_list.append(str(event.rec_id))

        for i in range(length):
            if str(i+1) not in dis_list:
                hide_list.append(str(i+1))

        self.send(text_data=json.dumps({
            'hide_list': hide_list,
            'dis_list': dis_list,
        }))
