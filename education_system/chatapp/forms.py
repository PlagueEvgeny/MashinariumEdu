from django import forms

from chatapp.models import Room


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = (
            'name',
            'slug',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, item in self.fields.items():
            item.widget.attrs['class'] = 'room-form'