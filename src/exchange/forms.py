from django import forms


from django.core.exceptions import ValidationError


class LeaveForms(forms.Form):
    # forms related to leave
    OPTIONS = [
        ('give_leave', 'Mettre le congé en concours'),
    ]
    date = forms.CharField(widget=forms.HiddenInput())
    give_leave = forms.ChoiceField(label='Souhait',
                                   choices=OPTIONS,
                                   required=True)


class RequestLeaveForms(forms.Form):
    OPTIONS = [
        ('request_leave', 'Demander un congé'),
        ('schedule', "Modifier l'horaire"),
    ]
    date = forms.CharField(widget=forms.HiddenInput())
    request_leave = forms.ChoiceField(label='Souhait',
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

    def clean(self):
        cleaned_data = super().clean()
        start1 = cleaned_data['start_hour_1']
        start2 = cleaned_data['start_hour_2']
        end1 = cleaned_data['end_hour_1']
        end2 = cleaned_data['end_hour_2']
        if (start2 and start1) and start2 < start1:
            print('debug 1')
            raise ValidationError("L'heure ne suit pas", code='invalid')

        if (end2 and end1) and end2 < end1:
            print('debug 2')
            raise ValidationError("L'heure ne suit pas", code='invalid')
