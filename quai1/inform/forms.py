from django import forms


class AcceptDeclineDateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.dates = kwargs.pop('user_dates')
        super(AcceptDeclineDateForm, self).__init__(*args, **kwargs)

        self.options = list()
        if isinstance(self.dates, str):
            # Needed when verificate
            self.options.append((self.dates, self.dates))
        else:
            for date in self.dates:
                self.options.append((date[0], date[1]))
            self.options.append(('À discuter', 'À discuter'))

        self.fields['accept_decline_date'].choices = self.options

    accept_decline_date = forms.ChoiceField(label="",
                                            required=False,
                                            choices=[])


class DeleteForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.leave_id = kwargs.pop('leave_id')
        super(DeleteForm, self).__init__(*args, **kwargs)
        self.fields['leave'].initial = self.leave_id

    leave = forms.CharField(label="",
                            widget=forms.HiddenInput())


class AcceptDeclineForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.shift_id = kwargs.pop('shift_id')
        super(AcceptDeclineForm, self).__init__(*args, **kwargs)
        self.fields['shift'].initial = self.shift_id

    shift = forms.CharField(label="",
                            widget=forms.HiddenInput())
