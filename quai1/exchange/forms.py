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
        ('horary', "Modifier l'horaire"),
    ]
    date = forms.CharField(widget=forms.HiddenInput())
    ask_rest = forms.ChoiceField(label='Souhait',
                                 choices=OPTIONS,
                                 required=True,
                                 widget=forms.Select(
                                     attrs={'onchange': 'hide()'})
                                 )
    start = forms.BooleanField(label="Entrée de service",
                               label_suffix="",
                               required=False,
                               widget=forms.CheckboxInput(
                                   attrs={'onchange': "start_now('start')"})
                               )
    start_hour_1 = forms.TimeField(label="",
                                   required=False,
                                   widget=forms.TimeInput(
                                       attrs={
                                           'type': 'time',
                                           'onchange': "from_between('start')",
                                       })
                                   )
    start_hour_2 = forms.TimeField(label="",
                                   required=False,
                                   widget=forms.TimeInput(
                                       attrs={
                                           'type': 'time',
                                           'onchange': "from_between('start')",
                                       })
                                   )
    tolerance_start = forms.DurationField(label="Tolérance +/-",
                                          initial='PT30M',
                                          required=False,
                                          )
    end = forms.BooleanField(label="Fin de service",
                             label_suffix="",
                             required=False,
                             widget=forms.CheckboxInput(
                                 attrs={'onchange': "start_now('end')"})
                             )
    end_hour_1 = forms.TimeField(label="",
                                 required=False,
                                 widget=forms.TimeInput(
                                     attrs={
                                         'type': 'time',
                                         'onchange': "from_between('end')",
                                       }),
                                 )
    end_hour_2 = forms.TimeField(label="",
                                 required=False,
                                 widget=forms.TimeInput(
                                     attrs={
                                         'type': 'time',
                                         'onchange': "from_between('end')",
                                     }),
                                 )
    tolerance_end = forms.DurationField(label="Tolérance +/-",
                                        initial='PT30M',
                                        required=False,
                                        )
    note = forms.CharField(label='Remarque',
                           required=False,
                           widget=forms.Textarea(attrs={
                               'cols': 20,
                               'rows': 2}))
