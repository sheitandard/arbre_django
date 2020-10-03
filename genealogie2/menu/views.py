from django.shortcuts import render
from .forms import ReadFileForm, IndividualForm, RelationshipForm, ChildForm, ParentForm, LocationForm
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from .models import Location, Individual, Relationship, Child, month_list, Modification
from django.contrib.auth.models import Group
from django.views import generic
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect,HttpResponse, JsonResponse
from django.views.generic.edit import UpdateView, FormView, DeleteView


pays_connus = ["FRANCE","POLOGNE","ALLEMAGNE","ALGERIE", "ITALIE","ESPAGNE","ROYAUNE-UNI", "ANGLETERRE"]


class IndividualListView(generic.ListView):
    model = Individual
    paginate_by = 50
    template_name = 'menu/home.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        d=Individual.objects.all()
        current_user=self.request.user
        if not current_user.is_authenticated:
            index(query)

        elif not is_current_user_admin(current_user):
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

class IndividuDelete(DeleteView):
    model = Individual
    success_url = reverse_lazy('Liste des modifications')
    template_name = 'menu/delete_individu.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        try:
            instance_child = Child.objects.get( child=self.object)

            m2 = Modification(subject=self.object, user=request.user,
                              note="Suppression de la relation parent-enfant de " + self.object.first_name + " " + self.object.last_name
                                   + " avec "+ instance_child.relation.parent1.first_name + " " + instance_child.relation.parent1.last_name + " et "
                                   +instance_child.relation.parent2.first_name + " " + instance_child.relation.parent2.last_name)
            instance_child.delete()
            m2.save()

        except Child.DoesNotExist:
            pass

        try:
            marriages = Relationship.objects.filter( Q(parent1=self.object) | Q(parent2 =self.object) )
            print(marriages)

            for marriage in marriages:
                    print("parent1",marriage.parent1 )
                    print("parent2", marriage.parent2)
                    try:
                        instance_parent = Child.objects.filter(relation=marriage)
                        if marriage.parent1 is None or marriage.parent2 is None:
                            for enfant in instance_parent:

                                m2 = Modification(subject=enfant, user=request.user,
                                                  note="Suppression des parents de " + enfant.child.first_name + " " + enfant.child.last_name )
                                enfant.delete()
                                m2.save()

                            m2 = Modification(subject=self.object, user=request.user,
                                              note="Suppression de la relation entre " + str(marriage.parent1 or "None") +" et " + str(marriage.parent2 or "None"))
                            marriage.delete()
                            m2.save()

                    except Child.DoesNotExist:
                        m2 = Modification(subject=self.object, user=request.user,
                                          note="Suppression de la relation entre " + str( marriage.parent1 or "None") + " et " + str(marriage.parent2 or "None"))
                        marriage.delete()
                        m2.save()
                    if marriage.parent1 is not None:
                        marriage.parent1.user_who_last_updated = request.user
                        marriage.parent1.save()
                    if marriage.parent2 is not None:
                        marriage.parent2.user_who_last_updated = request.user
                        marriage.parent2.save()

        except Relationship.DoesNotExist:
            pass

        m = Modification(subject=self.object, user=request.user,
                         note="Suppression de l'individu " + self.object.first_name + " " + self.object.last_name)
        m.save()
        self.object.delete()

        return HttpResponseRedirect(self.get_success_url())

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

def add_child(relation_id,child_id):
    try:
        p = Child.objects.get(child=child_id, relation=relation_id)
    except Child.DoesNotExist:
        p = Child(child=child_id,relation=relation_id)
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

def is_current_user_admin(user=None):
    query_group = Group.objects.filter(user = user)
    if 'tree_admin' in query_group[0].name:
        return True
    return False



def import_gedcom(request):
    form = ReadFileForm()
    encodage='utf-8'
    if request.method == 'POST':
        form = ReadFileForm(request.POST, request.FILES)
        if form.is_valid():
            if not request.FILES['fichier'].name.endswith(".ged"):
                return render(request, 'menu/read_file.html',{'content':[' Veuillez entrez un fichier de type GEDCOM (et finissant par .ged).', form]})
            else:
                print("else")
                content = request.FILES['fichier'].readline()
                print(content)
                gedcom_id=None
                id_fam=None
                commentaire=""
                while content:
                    print(content)
                    content_part= content.decode(encodage,'ignore').split(" ")
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
                                content_part= content.decode(encodage,'ignore').split(" ")
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
                                content = request.FILES['fichier'].readline()
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
    form=IndividualForm(request.POST or None, request.FILES or None,instance=instance)

    if form.is_valid():
        instance=form.save(commit=False)
        instance.user_who_last_updated = request.user
        instance.save()
        m = Modification(subject=instance, user=request.user, note="modification des données personnelles de "+ instance.first_name + " " +instance.last_name)
        m.save()
        return HttpResponseRedirect(instance.get_absolute_url())
    context={
                "form":form,}
    return render(request, 'menu/update_from_form.html', context )

def remove_parents(request, id=None, id2=None):
    instance = get_object_or_404(Individual, id=id)
    link = Child.objects.get(Q(child=id))
    instance.user_who_last_updated = request.user
    instance.save()

    if link.relation.parent1 is not None and link.relation.parent1.id==int(id2):
        m = Modification(subject=instance, user=request.user, note="Suppression d'un lien de parenté avec " +link.relation.parent1.first_name+" "+link.relation.parent1.last_name)
        link.relation.parent1=None
        m.save()
    elif link.relation.parent2 is not None and link.relation.parent2.id==int(id2):
        m = Modification(subject=instance, user=request.user, note="Suppression d'un lien de parenté avec " + link.relation.parent2.first_name+" "+link.relation.parent2.last_name)
        link.relation.parent2 = None
        m.save()


    if link.relation.parent1 is None and link.relation.parent2 is None:
        m = Modification(subject=instance, user=request.user, note="Suppression des parents ")
        m.save()
        link.delete()
    else:
        link.save()
    try :
        instance_child=Child.objects.get(child=instance)
        form = ParentForm(request.POST or None, instance=instance_child)
        if form.is_valid():
            instance_child = form.save(commit=False)
            instance_child.save()
            m = Modification(subject=instance, user=request.user, note="parents modifiés")
            m.save()
            return HttpResponseRedirect(instance.get_absolute_url())

    except  Child.DoesNotExist:
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "form": form, }
    return render(request, 'menu/individual_add_parent.html', context)



def update_place(request, id=None):
    instance=get_object_or_404(Location,id=id)

    form=LocationForm(request.POST or None, instance=instance)

    if form.is_valid():# and rform.is_valid() and cform.is_valid():
        instance=form.save(commit=False)
        instance.save()
        print("new lieu")
        print(instance)
        m = Modification(subject=instance, user=request.user, note="modification d'un lieu" )
        m.save()
        return HttpResponseRedirect(instance.get_absolute_url())
    context={
                "form":form,}
    return render(request, 'menu/update_from_form.html', context )

def get_first_query(myDict):
    outDict={}
    for key in myDict:
        outDict[key]=myDict.getlist(key)[0]
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
    instance = get_object_or_404(Individual, id=id)
    try:
        instance_child=Child.objects.get(child=instance)
        print("enfant trouvé")
    except Child.DoesNotExist:
        instance_child=Child(child=instance, relation=Relationship(parent1=None, parent2=None))

    relation = instance_child.relation
    form = ParentForm(request.POST or None, instance=relation)
    errors = []
    if 'save' in request.POST:
        form = ParentForm(request.POST or None)
        if  form.is_valid():
            form.clean()
            relation = form.save(commit=False)
            relation.save()
            m = Modification(subject=relation.parent1, user=request.user,
                             note="ajout d'une relation avec " + relation.parent2.first_name + " " +  relation.parent2.last_name)
            m.save()
            instance_child.relation = relation
            instance_child.save()
            m = Modification(subject=instance, user=request.user, note="ajout ou modification d'une relation parent-enfant")
            m.save()
            return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "form": form,
        "errors": errors,
    }
    return render(request, 'menu/individual_add_parent.html', context)


def add_relationship(request, id=None):
    print("add_relation")
    instance=get_object_or_404(Individual,id=id)
    if instance.gender == 'M':
        relation=Relationship(parent1=instance)
    else:
        relation = Relationship(parent2=instance)

    form = RelationshipForm(None, instance=relation)
    if 'save' in request.POST:
            print(request.POST)
            request_post=get_first_query(request.POST)
            if instance.gender == 'M':
                request_post["parent1"]=id
            else:
                request_post["parent2"] = id
            print(request_post)
            form = RelationshipForm(request_post or None)
            if form.is_valid():
                print("form is valid")
                form.clean()
                relation = form.save(commit=False)
                instance.user_who_last_updated = request.user
                instance.save()
                relation.save()
                m = Modification(subject=instance, user=request.user, note="ajout d'un(e) partenaire existant pour "+instance.first_name + " "+instance.last_name)
                m.save()
            return HttpResponseRedirect(instance.get_absolute_url())
    context={
                "form":form
                }
    return render(request, 'menu/individual_relation_add.html', context )


def add_partner(request, id=None):
    print("add_partner")
    print(request.POST)
    instance = get_object_or_404(Individual, id=id)
    form = IndividualForm(request.POST or None)
    if 'save' in request.POST:
            if form.is_valid() :
                form.clean()
                new_partner = form.save(commit=False)
                new_partner.user_who_last_updated = request.user
                new_partner.user_who_created = request.user
                new_partner.save()
                m = Modification(subject=new_partner, user=request.user,
                                 note="ajout d'un nouvel individu " + new_partner.first_name + " " + new_partner.last_name)
                m.save()
                instance.user_who_last_updated = request.user
                instance.save()
                if instance.gender=='M':
                    relation = Relationship(parent1=instance, parent2=new_partner)
                else:
                    relation = Relationship(parent2=instance, parent1=new_partner)
                m = Modification(subject=instance, user=request.user, note="ajout d'un(e) partenaire pour "+instance.first_name + " "+instance.last_name)
                m.save()
            return HttpResponseRedirect(instance.get_absolute_url()+"/add_relation")
    context={
                "form":form
                }
    return render(request, 'menu/individual_add.html', context )

def update_relation(request, id=None):
    print("update_relation")
    relation = get_object_or_404(Relationship, id=id)
    form = RelationshipForm(request.POST or None, request.FILES or None,instance=relation)
    if 'save' in request.POST:
        print(request.POST)
        if form.is_valid():
            print("form is valid")
            form.clean()
            relation = form.save(commit=False)
            relation.save()
            if relation.parent1 is not None:

                relation.parent1.user_who_last_updated = request.user
                relation.parent1.save()
                m = Modification(subject=relation.parent1, user=request.user,
                                 note="modification d'un(e) relation pour " + relation.parent1.first_name + " " + relation.parent1.last_name)
                m.save()
            if relation.parent2 is not None:
                relation.parent2.user_who_last_updated = request.user
                relation.parent2.save()
                m = Modification(subject=relation.parent2, user=request.user,
                                 note="modification d'un(e) relation pour " + relation.parent2.first_name + " " + relation.parent2.last_name)
                m.save()
        return HttpResponseRedirect(relation.parent1.get_absolute_url())
    context = {
        "form": form
    }
    return render(request, 'menu/individual_relation_update.html', context)

class RelationDelete(DeleteView):
    model = Relationship
    success_url = reverse_lazy('Liste des modifications')
    template_name = 'menu/delete_relation.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        print("deleting following object:")
        print(self.object)

        try:
            if self.object.parent1 is not None:
                subject_modif=self.object.parent1
                self.object.parent1.user_who_last_updated = request.user
                self.object.parent1.save()
            if self.object.parent2 is not None:
                subject_modif = self.object.parent2
                self.object.parent2.user_who_last_updated = request.user
                self.object.parent2.save()
            m2 = Modification(subject=subject_modif, user=request.user,
                              note="Suppression de la relation entre " + str(self.object.parent1 or "None") + " et " + str(self.object.parent2 or "None"))
            m2.save()
        except Relationship.DoesNotExist:
            pass

        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())

def add_children(request, id=None):
    print("add_childen")
    relation = get_object_or_404(Relationship, id=id)
    form = IndividualForm(request.POST or None)
    instance = get_object_or_404(Individual, id=relation.parent1.id)
    if 'save' in request.POST:
        if form.is_valid():
            form.clean()
            new_children = form.save(commit=False)
            new_children.user_who_last_updated = request.user
            new_children.user_who_created = request.user
            new_children.save()
            m = Modification(subject=new_children, user=request.user,
                             note="ajout d'un nouvel individu " + new_children.first_name + " " + new_children.last_name)
            m.save()
            instance.user_who_last_updated = request.user
            instance.save()
            relation_child = Child(relation=relation, child=new_children)
            relation_child.save()
            m = Modification(subject=instance, user=request.user,
                             note="ajout d'un(e) enfant pour " + instance.first_name + " " + instance.last_name)
            m.save()

        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        "form": form
    }
    return render(request, 'menu/individual_add.html', context)

def add_existing_children(request, id=None):
    print("add_existing_children")
    relation = get_object_or_404(Relationship, id=id)
    child_relation = Child(relation=relation)
    form = ChildForm(request.POST or None, instance = child_relation)
    instance = get_object_or_404(Individual, id=relation.parent1.id)
    if 'save' in request.POST:
        print(request.POST)
        if form.is_valid():
            form.clean()
            child_relation = form.save(commit=False)
            try:
                check_child = Child.objects.get(child=child_relation.child)
                message_error=str(child_relation.child or "None") + " a déjà des parents!"
                print("check_child",check_child)
                print(check_child)
                context = {
                    "message_error" : message_error,
                    "form": form
                }
                return render(request, 'menu/individual_existing_children_add.html', context)
            except  Child.DoesNotExist:
                print(child_relation)
                print(child_relation.child)
                m = Modification(subject=instance, user=request.user,
                                 note="ajout d'une nouvelle relation enfant-parent " + str(child_relation.child or "None"))
                m.save()
                instance.user_who_last_updated = request.user
                instance.save()
                child_relation.relation=relation

                print(child_relation)
                child_relation.save()

                return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        "form": form
    }
    return render(request, 'menu/individual_existing_children_add.html', context)


def add_location_html(request):
    form = LocationForm(None)
    if 'save_location' in request.POST:
            print("yes there is a save_location")
            form = LocationForm(request.POST or None)
            if form.is_valid() :
                form.clean()
                loc = form.save(commit=False)
                loc.save()
                m = Modification(subject=loc, user=request.user, note="ajout d'un lieu")
                m.save()
                return HttpResponse('<script type="text/javascript">window.opener.reload_places();window.close();</script>')

    context={
                "form":form,
                }
    return render(request, 'menu/location_add.html', context )

def add_individual_html(request):
    form = IndividualForm(None)
    print(request.POST)
    if 'save_individual' in request.POST:
            form = IndividualForm(request.POST or None)
            if form.is_valid() :
                print("form is valid")
                form.clean()
                ind = form.save(commit=False)
                if ind.gender is None:
                    ind.gender='A'
                ind.save()
                m = Modification(subject=ind, user=request.user, note="ajout d'un nouvelle individu : "+ ind.first_name + " " + ind.last_name)
                m.save()
                #parameters_as_string='id='+str(ind.id)+',gender='+ind.gender
                parameters_as_string = 'id=' + str(ind.id)
                print(parameters_as_string)
                return HttpResponse('<script type="text/javascript">window.opener.reload_individuals('+parameters_as_string+');window.close();</script>')

    context={
                "form":form,
                }
    return render(request, 'menu/individual_add.html', context )

def place_list(request):
    p = Location.objects.all()
    p2=list(p.values('id','city','department','country','church'))
    return JsonResponse({"places":p2})

def individual_list(request):
    p = Individual.objects.all()
    p2=list(p.values('id','first_name','last_name','date_of_birth','date_of_death'))
    return JsonResponse({"individuals":p2})