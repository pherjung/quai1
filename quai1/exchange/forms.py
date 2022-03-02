from django import forms


class LeaveForms(forms.Form):
    # forms related to rest
    OPTIONS = [
        ('give_rest', 'Mettre le congé en concours'),
    ]
    date = forms.CharField(widget=forms.HiddenInput())
    give_rest = forms.ChoiceField(label='Souhait',
                                  choices=OPTIONS,
                                  required=True)


class AskLeaveForms(forms.Form):
    OPTIONS = [
        ('ask_rest', 'Demander un congé'),
    ]
    date = forms.CharField(widget=forms.HiddenInput())
    ask_rest = forms.ChoiceField(label='Souhait',
                                 choices=OPTIONS,
                                 required=True)
    note = forms.CharField(label='Remarque',
                           widget=forms.Textarea(attrs={
                               'cols': 20,
                               'rows': 10}))
