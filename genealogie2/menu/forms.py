from django import forms
from django.forms import ModelForm

from .models import Individual


class ReadFileForm(forms.Form):
    fichier = forms.FileField()


class IndividualForm(ModelForm):
    class Meta:
        model = Individual
        fields = ["first_name",
        		"last_name",
        		"gender",
        		"is_deceased",
        		"image",
        		"date_of_birth",
        		"place_of_birth",
        		"date_of_death",
        		"place_of_death",
        		"place_of_residence",
        		"occupation",
        		"email",
        		"comment"
        ]