from django import forms
from people.models import RandomImage

class RandomForm(forms.ModelForm):
    class Meta:
        model = RandomImage
        fields = ('description', 'image', )
