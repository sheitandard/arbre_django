from django import forms
from django.forms import ModelForm
from .models import Individual, Relationship, Child, Location


class ReadFileForm(forms.Form):
    fichier = forms.FileField()

class LocationForm(ModelForm):
    class Meta:
        model = Location
        fields = ["city",
                  "country",
                  "department",
                  "church",
                  "city_today",
                  "country_today",
                ]
        labels = {
                  "city":"Ville",
                  "country":"Pays",
                  "department":"Département",
                  "church":"Eglise",
                  "city_today":"Ville actuelle",
                  "country_today":"Pays actuel",}

    def clean(self):
        cleaned_data = super().clean()
        try:
            print( cleaned_data)
            p = Location.objects.get(city= cleaned_data.get("city"), country= cleaned_data.get("country"),
                                     church= cleaned_data.get("church"), department= cleaned_data.get("department"))
            self.add_error('city', "Le lieu existe déjà dans la base de données!")
        except Location.DoesNotExist:
            print("lieu n'existe pas")
            return cleaned_data



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
                "birth_source",
                "death_source",
                "occupation",
                "email",
                "comment"
        ]
        labels = {
                "first_name":"Prénom(s)",
                "last_name":"Nom",
                "gender":"Genre",
                "is_deceased":"Est décédé(e)",
                "image":"Image",
                "date_of_birth":"Date de naissance",
                "place_of_birth":"Lieu de naissance",
                "birth_source":"Certificat de naissance",
                 "death_source":"Certificat de décès",
                "date_of_death":"Date du décès",
                "place_of_death": "Lieu du décès",
                "place_of_residence":"Lieu de résidence",
                "occupation":"Métier",
                "email":"Email",
                "comment":"Commentaire"}

    def clean(self):
            cleaned_data = super().clean()
            first_name = cleaned_data.get("first_name")
            last_name = cleaned_data.get("last_name")

            if first_name=='':
                msg = "Le prénom ne peut pas être vide!"
                self.add_error('first_name', msg)

            if  last_name=='':
                msg = "Le nom ne peut pas être vide!"
                self.add_error('last_name', msg)

            return cleaned_data

class RelationshipForm(ModelForm):
    class Meta:
        model = Relationship
        fields = [  "parent1",
                    "parent2",
                    "status",
                    "date_of_marriage",
                    "place_of_marriage",
                    "date_of_divorce",
                    "marriage_source",
                    "divorce_source"]
        labels = {
            "parent1":"1ère personne",
            "parent2":"2e personne",
            "status":"Status",
            "date_of_marriage":"Date de mariage",
            "place_of_marriage":"lieu du mariage",
            "date_of_divorce":"date du divorce",
            "marriage_source":"Certificat de mariage",
            "divorce_source":"Certificat de divorce"
        }

class ChildForm(ModelForm):
    class Meta:
        model = Child
        fields = [
                  "child"
                ]
        labels = {
            "child":"Enfant",}

class ParentForm(ModelForm):
    class Meta:
        model = Child
        fields = ["relation",
                  "child"
                ]
        labels = {
            "relation":"Couple"}