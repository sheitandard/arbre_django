from django import forms
from django.forms import ModelForm

from .models import Individual, Relationship, Child
from django.forms import inlineformset_factory


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
        labels = {
        		"first_name":"Prénom(s)",
        		"last_name":"Nom",
        		"gender":"Genre",
        		"is_deceased":"Est décédé(e)",
        		"image":"Image",
        		"date_of_birth":"Date de naissance",
        		"place_of_birth":"Lieu de naissance",
        		"date_of_death":"Date du décès",
        		"place_of_death": "Lieu du décès",
        		"place_of_residence":"Lieu de résidance",
        		"occupation":"Métier",
        		"email":"Email",
        		"comment":"Commentaire"}


class RelationshipForm(ModelForm):
	class Meta:
		model = Relationship
		fields = ["parent1",
				"parent2",
				"status",
				"date_of_marriage",
				"date_of_divorce"]
		labels = {
			"parent1":"1ère personne",
			"parent2":"2e personne",
			"status":"Status",
			"date_of_marriage":"Date de mariage",
			"place_of_marriage":"lieu du mariage",
			"date_of_divorce":"date du divorce"}


class ChildForm(ModelForm):
	class Meta:
		model = Child
		fields = ["parent1",
				  "parent2",
				  "child"
				]
		labels = {
			"child":"Enfant",
			"parent1":"Parent 1",
			"parent2":"Parent 2"}

class ParentForm(ModelForm):
	class Meta:
		model = Child
		fields = ["parent1",
				  "parent2",
				]
		labels = {
			"parent1":"Parent 1",
			"parent2":"Parent 2"}

#IndividualFormSet = inlineformset_factory(Individual,Relationship ,form=RelationshipForm, fk_name='parent1')