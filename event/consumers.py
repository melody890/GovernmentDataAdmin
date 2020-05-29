from channels.generic.websocket import WebsocketConsumer
from django.db.models import Q
from django.contrib.auth.models import User
import json

from .models import MainType, Type, Street, Event, Achieve
from .views import my_filter
from user.models import DisposeRecord


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
        dispose_user = text_data_json['dispose_user']
        event = Event.objects.get(rec_id=rec_id)
        achieve = Achieve.objects.get(status=status)
        event.achieve = achieve
        event.save()
        print(event)
        user = User.objects.get(username=dispose_user)
        new_dispose_record = DisposeRecord.objects.create(disposer=user.username,eventID=event.rec_id)
        new_dispose_record.save()


        self.send(text_data=json.dumps({}))
