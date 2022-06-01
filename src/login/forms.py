from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from .models import CustomUser, Depot


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ('username',
                  'first_name',
                  'last_name',
                  'email',
                  'depot',
                  'phone_nb',
                  'url',)
        depot = forms.ModelMultipleChoiceField(
            queryset=Depot.objects.all(),
            widget=forms.CheckboxSelectMultiple,
        )


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('username',
                  'first_name',
                  'last_name',
                  'email',
                  'phone_nb',
                  'url',)
        depot = forms.ModelMultipleChoiceField(
            queryset=Depot.objects.all(),
            widget=forms.CheckboxSelectMultiple(),
        )
