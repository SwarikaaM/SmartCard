from django import forms


class ModeForm(forms.Form):
    CHOICES = [
        ('reader', 'Reader'),
        ('writer', 'Writer'),
    ]
    mode = forms.ChoiceField(choices=CHOICES)
    aadharno = forms.CharField(widget=forms.NumberInput, max_length=12)
    panno = forms.CharField(widget=forms.TextInput, max_length=10)
