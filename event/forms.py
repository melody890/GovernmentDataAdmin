from django import forms


class EventForm(forms.Form):
    event_src = forms.CharField()
    property = forms.CharField()
    sub_type = forms.CharField()
    community = forms.CharField()
    dispose_unit = forms.CharField()
