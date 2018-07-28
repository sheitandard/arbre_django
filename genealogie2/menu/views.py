from django.shortcuts import render
from .forms import ReadFileForm, IndividualForm, RelationshipForm, ChildForm, ParentForm, LocationForm
from django.shortcuts import get_object_or_404
from django.forms import inlineformset_factory

from datetime import datetime
from django.db import models
from .models import Location, Individual, Relationship, Child, month_list, Modification
from django.contrib.auth.models import Group

from django.views import generic
import operator
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from functools import reduce
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect,HttpResponse, JsonResponse
from django.views.generic.edit import UpdateView, FormView
from django.views.generic import TemplateView
from django.contrib import messages




pays_connus = ["FRANCE","POLOGNE","ALLEMAGNE","ALGERIE", "ITALIE","ESPAGNE","ROYAUNE-UNI", "ANGLETERRE"]


class IndividualListView(generic.ListView):
    model = Individual
    paginate_by = 50
    template_name = 'menu/home.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        d=Individual.objects.all()
        current_user=self.request.user
        if not is_current_user_admin(current_user):
            d=d.exclude(private=True)

        if query:
            query_element=query.split(" ")

            for element in query_element:
                d=d.filter(Q(last_name__icontains=element)  | Q(first_name__icontains=element) )
            if '?' not in query:
                d=d.exclude(last_name='?').exclude(first_name='?')
            return d
        else:
            return Individual.objects.exclude(last_name='?').exclude(first_name='?')

class IndividualDetailView(generic.DetailView):
    model = Individual

class ModificationListView(generic.ListView):
    model = Modification
    paginate_by = 30
    template_name = 'menu/list_modif.html'

    def get_queryset(self):

        return Modification.objects.order_by('-date')

class PlaceListView(generic.ListView):
    model = Location
    paginate_by = 30
    template_name = 'menu/list_location.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        d=Location.objects.all()

        if query:
            query_element=query.split(" ")

            for element in query_element:
                d=d.filter(Q(country__icontains=element)  | Q(city__icontains=element) | Q(department__icontains=element) | Q(church__icontains=element) )

        return d

class PlaceDetailView(generic.DetailView):
    model = Location
    template_name = 'menu/detail_place.html'


def index(request):
    #current_user=request.user
    #print("index user", current_user)
    return render(request, 'menu/home.html')



def contact(request):
    return render(request, 'menu/basic.html',{'content':['Pour signaler tout problème ou pour avoir un compte, écrivez-moi à cette adresse: ','sheitandard@hotmail.fr']})


def add_location(content_part):
    pays="France"
    ville=None
    paroisse=None
    departement=None
    if content_part[-1].strip().upper() in pays_connus:
        pays=content_part[-1].strip()
    else:
        departement=content_part[-1]
    if len(content_part[2:])>1:
        ville=content_part[2].replace(",","")
    if len(content_part[2:])>3 and "(" in content_part[3]:
        paroisse=" ".join(content_part[3:5]).replace(",","")
    try:
        p = Location.objects.get(city=ville, country=pays, church=paroisse, department=departement)
        print("try search location")
    except Location.DoesNotExist:
        print("try put location")
        place=Location(city=ville, country=pays, church=paroisse, department=departement)
        place.save()

    else:
        try:
            print("Cet endroit est déjà dans la base de données",ville, departement, pays, paroisse)
        except:
            print("Cet endroit est déjà dans la base de données et écrire son nom génère des erreurs")

    try:
        loc = Location.objects.get(city=ville, country=pays, church=paroisse, department=departement)
        return loc
    except Location.DoesNotExist:
        print("Etrange, l'endroit n'existe pas dans la base de données",ville, departement, pays, paroisse)
        return 0

def add_individual(gedcom_id, first_name, last_name,gender, date_of_birth, date_of_death, place_of_birth, place_of_death,occupation, commentaire):
    try:
        p = Individual.objects.get(gedcom_id=gedcom_id,first_name=first_name, last_name=last_name, date_of_birth = date_of_birth)
    except Individual.DoesNotExist:
        p = Individual(private=False, gedcom_id=gedcom_id, first_name=first_name, last_name=last_name,gender=gender,
                            date_of_birth = date_of_birth, date_of_death=date_of_death, place_of_birth=place_of_birth, place_of_death=place_of_death,
                            occupation=occupation, comment=commentaire)
        p.save()
    else:
        try:
            print("Cet individu est déjà dans la base de données",first_name, last_name,date_of_birth)
        except:
            print("Cet individu est déjà dans la base de données et écrire son nom génère des erreurs")

def get_individual(id_gedcom):
    try:
        ind = Individual.objects.get(gedcom_id=id_gedcom)
        return ind
    except Individual.DoesNotExist:
        print("Etrange, l'individu n'existe pas dans la base de données",id_gedcom)
        return 0

def add_child(husband_id,wife_id,child_id):
    try:
        p = Child.objects.get(child=child_id, parent1=husband_id, parent2=wife_id)
    except Child.DoesNotExist:
        p = Child(child=child_id, parent1=husband_id, parent2=wife_id)
        p.save()
    else:
        try:
            print("Cet enfant est déjà dans la base de données",child_id, husband_id,wife_id)
        except:
            print("Cet enfant est déjà dans la base de données et écrire son nom génère des erreurs")

def add_relation(id_fam,husband_id,wife_id,date_marriage,place_marriage,date_divorce,status ):
    try:
        p = Relationship.objects.get(gedcom_id=id_fam,parent1=husband_id, parent2=wife_id)
    except Relationship.DoesNotExist:
        p = Relationship(gedcom_id=id_fam,parent1=husband_id,parent2=wife_id,date_of_marriage=date_marriage,place_of_marriage=place_marriage,
            date_of_divorce=date_divorce,status=status)
        p.save()
    else:
        try:
            print("Cette relation est déjà dans la base de données",husband_id, wife_id)
        except:
            print("Cette relation est déjà dans la base de données")

#def get_current_user():
#	return current_user

def is_current_user_admin(user=None):
    query_group = Group.objects.filter(user = user)
    #print("current user",user)
    #print(query_group)
    if 'tree_admin' in query_group[0].name:
        return True
    return False



def import_gedcom(request):
    form = ReadFileForm()
    encodage='utf-8'
    #encodage="ascii"
    if request.method == 'POST':
        form = ReadFileForm(request.POST, request.FILES)
        if form.is_valid():
            if not request.FILES['fichier'].name.endswith(".ged"):
                return render(request, 'menu/read_file.html',{'content':[' Veuillez entrez un fichier de type GEDCOM (et finissant par .ged).', form]})
            else:
                print("else")
                # Do something with content
                content = request.FILES['fichier'].readline()
                print(content)
                gedcom_id=None
                id_fam=None
                commentaire=""

                while content:
                    print(content)
                    content_part= content.decode(encodage,'ignore').split(" ")
                    #print(content_part)
                    if len(content_part)>2 :

                        if content_part[2].rstrip()=="INDI":
                            if gedcom_id:
                                add_individual(gedcom_id, first_name, last_name,gender, date_of_birth, date_of_death, place_of_birth, place_of_death,
                            occupation, commentaire)

                            first_name = '?'
                            last_name = '?'
                            gender = "A"
                            date_of_birth=None
                            date_of_death=None
                            place_of_birth=None
                            place_of_death=None
                            occupation=None
                            path_image=None
                            commentaire=""
                            gedcom_id=content_part[1]
                        elif content_part[2].rstrip()=="FAM":
                            if gedcom_id:
                                add_individual(gedcom_id, first_name, last_name,gender, date_of_birth, date_of_death, place_of_birth, place_of_death,
                            occupation, commentaire)
                            if id_fam :
                                add_relation(id_fam,husband_id,wife_id,date_marriage,place_marriage,date_divorce,status )
                            husband_id=None
                            gedcom_id=None
                            wife_id=None
                            date_marriage=None
                            place_marriage=None
                            date_divorce=None
                            status="concubinage"
                            id_fam=content_part[1]
                        elif content_part[1]=="GIVN":
                            first_name = ' '.join(content_part[2:]).rstrip()
                        elif content_part[1]=="SURN":
                            last_name = ' '.join(content_part[2:]).rstrip()
                        elif content_part[1]=="SEX":
                            if content_part[2].rstrip()=="M":
                                gender = "M"
                            else:
                                gender = "F"
                        elif content_part[1]=="OCCU":
                            occupation = ' '.join(content_part[2:]).rstrip()
                        elif content_part[1]=="NOTE":
                            commentaire = commentaire + " ".join(content_part[2:]).rstrip()
                        elif content_part[1]=="FILE":
                            path_image = content_part[2].rstrip()
                        elif content_part[1]=="HUSB":
                            husband_id = get_individual(content_part[2].rstrip())
                        elif content_part[1]=="WIFE":
                            wife_id = get_individual(content_part[2].rstrip())
                        elif content_part[1]=="CHIL":
                            child_id = get_individual(content_part[2].rstrip())
                            #add_child(husband_id,wife_id,child_id)
                        content = request.FILES['fichier'].readline()
                    elif len(content_part)==2:
                        #print(content_part)
                        type=content_part[1].rstrip()
                        print(type)
                        if type=="BIRT" or type=="DEAT" or type=="MARR" or type=="DIV":
                            print("in birt")
                            year=None
                            month=None
                            day=None
                            ville=None
                            pays=None
                            paroisse=None
                            departement=None
                            content = request.FILES['fichier'].readline()
                            while content and content.decode(encodage,'ignore').split(" ")[0]=='2':
                                print(content)
                                #print("here")
                                content_part= content.decode(encodage,'ignore').split(" ")
                                #print(content_part)
                                if len(content_part)>2 :
                                    if content_part[1]=="DATE":
                                        if type=="BIRT":
                                            date_of_birth=" ".join(content_part[2:]).rstrip()
                                        elif type=="DEAT":
                                            date_of_death=" ".join(content_part[2:]).rstrip()
                                        elif type=="MARR":
                                            date_marriage=" ".join(content_part[2:]).rstrip()
                                            status="mariage ou Pacs"
                                        elif type=="DIV":
                                            date_divorce=" ".join(content_part[2:]).rstrip()
                                    #elif content_part[1]=="PLAC":
                                    ###	if add_location(content_part)!=0:
                                    ###		if type=="BIRT":
                                    ###			place_of_birth=add_location(content_part)
                                    ###		elif type=="DEAT":
                                    ##			place_of_death=add_location(content_part)
                                    #		elif type=="MARR":
                                    #			place_marriage=add_location(content_part)
                                    #			status="mariage ou Pacs"
                                content = request.FILES['fichier'].readline()
                                #print("there")
                        else:
                            content = request.FILES['fichier'].readline()
                    else:
                        content = request.FILES['fichier'].readline()
                    if id_fam:
                        add_relation(id_fam,husband_id,wife_id,date_marriage,place_marriage,date_divorce,status )

                return render(request, 'menu/home.html')
    return render(request, 'menu/read_file.html', locals())


def update_individu(request, id=None):
    instance=get_object_or_404(Individual,id=id)
    print(instance)
    form=IndividualForm(request.POST or None, instance=instance)

    if form.is_valid():# and rform.is_valid() and cform.is_valid():
        instance=form.save(commit=False)
        instance.save()
        m = Modification(subject=instance, user=request.user, note="modification des données personnelles" )
        m.save()
        return HttpResponseRedirect(instance.get_absolute_url())
    context={
                "form":form,}
    return render(request, 'menu/individual_detail_update.html', context )



def update_parents(request, id=None):
    instance=get_object_or_404(Individual,id=id)
    instance_child=get_object_or_404(Child,child=instance)
    print(instance)
    form=ParentForm(request.POST or None, instance=instance_child)
    if form.is_valid():
        instance_child=form.save(commit=False)
        instance_child.save()
        m = Modification(subject=instance, user=request.user, note="parents modifiés")
        m.save()
        return HttpResponseRedirect(instance.get_absolute_url())
    context={
                "form":form,}
    return render(request, 'menu/individual_parent_update.html', context )


def update_place(request, id=None):
    instance=get_object_or_404(Location,id=id)

    form=LocationForm(request.POST or None, instance=instance)

    if form.is_valid():# and rform.is_valid() and cform.is_valid():
        instance=form.save(commit=False)
        instance.save()
        m = Modification(subject=instance, user=request.user, note="modification d'un lieu" )
        m.save()
        return HttpResponseRedirect(instance.get_absolute_url())
    context={
                "form":form,}
    return render(request, 'menu/place_detail_update.html', context )

def get_first_query(myDict):
    outDict={}
    for key in myDict:
        outDict[key]=myDict.getlist(key)[0]
    print(outDict)
    return outDict

def transform_date(str_date):
    element_date=str_date.split("/")
    if len(element_date)==3:
        return " ".join([element_date[0], month_list[int(element_date[1]) - 1], element_date[2]])
    elif len(element_date)==2 and int(element_date[0])<13:
        return " ".join([month_list[int(element_date[0]) - 1], element_date[1]])
    else:
        return str_date


def add_parents(request, id=None):
    print("add_parent")
    print(request.POST)
    instance=get_object_or_404(Individual,id=id)
    try:
        instance_child=Child.objects.get(child=instance)
    except Child.DoesNotExist:
        instance_child = Child(child=instance, parent1=None, parent2=None)

    form1 = IndividualForm(None, instance=instance_child.parent1)
    form2 = IndividualForm(None,instance=instance_child.parent2)

    father=None
    mother=None
    errors = []


    if 'save' in request.POST:
            print(request.POST)
            print(get_first_query(request.POST))
            form1 = IndividualForm(get_first_query(request.POST) or None)
            form2 = IndividualForm(request.POST or None)
            if form2.is_valid() and form1.is_valid():
                form2.clean()
                form1.clean()

                if instance_child.parent2 is None:
                    mother = form2.save(commit=False)

                    mother.date_of_birth=transform_date(mother.date_of_birth)
                    mother.date_of_death = transform_date(mother.date_of_death)
                    print(mother.date_of_birth)
                    mother.save()
                    m = Modification(subject=instance, user=request.user, note="ajout d'un parent (mère)")
                    m.save()
                    print("mother", mother.id, mother.first_name)
                    instance_child.parent2=mother
                    #instance_child.save()
                else:
                    mother=instance_child.parent2
                if instance_child.parent1 is None:
                    father = form1.save(commit=False)
                    father.date_of_birth = transform_date(father.date_of_birth)
                    father.date_of_death = transform_date(father.date_of_death)
                    father.save()
                    m = Modification(subject=instance, user=request.user, note="ajout d'un parent (père)")
                    m.save()
                    print("father", father.id, father.first_name)
                    instance_child.parent1=father
                    instance_child.save()
                    m = Modification(subject=instance, user=request.user, note="ajout d'une relation parent-enfant")
                    m.save()
                else:
                    father=instance_child.parent1
                p = Relationship(parent1=father, parent2=mother, status='mariage ou Pacs')
                p.save()
                m = Modification(subject=father, user=request.user, note="ajout d'une relation")
                m.save()

    elif 'Ajouter un lieu' in request.POST.values():
        add_location_html(request, old_request=request)
    print("errors",errors)
    if instance_child.parent1 is not None and instance_child.parent2 is not None:
        return HttpResponseRedirect(instance.get_absolute_url())

    context={
                "form1":form1,
                "form2":form2,
                "errors":errors,
                }
    return render(request, 'menu/individual_parent_add.html', context )




def add_location_html(request):
    form = LocationForm(None)
    if 'save_location' in request.POST:
            print("yes there is a save_location")
            form = LocationForm(request.POST or None)
            if form.is_valid() :
                form.clean()
                location = form.save(commit=False)
                location.save()
                m = Modification(subject=location, user=request.user, note="ajout d'un lieu")
                m.save()
                return HttpResponse('<script type="text/javascript">window.opener.reload_places();window.close();</script>')

    context={
                "form":form,
                }
    return render(request, 'menu/location_add.html', context )

def place_list(request):
    p = Location.objects.all()
    p2=list(p.values('id','city','department','country','church'))
    return JsonResponse({"places":p2})
