from django import forms


class AcceptDeclineForm(forms.Form):
    def __init__(self, dates, *args, **kwargs):
        self.dates = dates
        super(AcceptDeclineForm, self).__init__(*args, **kwargs)

        self.options = list()
        for date in self.dates:
            self.options.append((date[0], date[0]))

        self.fields['accept_decline'] = forms.ChoiceField(label="",
                                                          choices=self.options)
