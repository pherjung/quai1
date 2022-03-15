from django import forms


class AcceptDeclineForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.dates = kwargs.pop('user_dates')
        super(AcceptDeclineForm, self).__init__(*args, **kwargs)

        self.options = list()
        if isinstance(self.dates, str):
            self.options.append((self.dates, self.dates))
        else:
            for date in self.dates:
                self.options.append((date[0], date[1]))
            self.options.append(('À discuter', 'À discuter'))

        self.fields['accept_decline'].choices = self.options

    accept_decline = forms.ChoiceField(label="",
                                       required=False,
                                       choices=[])
