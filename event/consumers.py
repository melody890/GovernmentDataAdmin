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
        status = text_data_json['status']
        rec_id = int(text_data_json['rec_id'])
        event = Event.objects.get(rec_id=rec_id)
        achieve = Achieve.objects.get(status=status)
        event.achieve = achieve
        event.save()

        self.send(text_data=json.dumps({}))
