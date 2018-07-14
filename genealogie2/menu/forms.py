from django import forms


class ReadFileForm(forms.Form):
    fichier = forms.FileField()