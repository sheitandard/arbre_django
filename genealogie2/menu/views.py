from django.shortcuts import render, get_object_or_404
from .forms import ReadFileForm, IndividualForm, RelationshipForm, ChildForm, ParentForm, LocationForm
from django.urls import reverse_lazy
from .models import Location, Individual, Relationship, Child, month_list, Modification
from django.contrib.auth.models import Group
from django.views import generic
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect,HttpResponse, JsonResponse
from django.views.generic.edit import UpdateView, FormView, DeleteView
from .import_gedcom_functions import import_from_gedcom


pays_connus = ["FRANCE","POLOGNE","ALLEMAGNE","ALGERIE", "ITALIE","ESPAGNE","ROYAUNE-UNI", "ANGLETERRE"]

def create_modification(subject, user, note):
    m = Modification(subject=subject, user=user, note=note)
    m.save()
    return 0

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

class LocationDelete(DeleteView):
    model = Location
    success_url = reverse_lazy('Liste des modifications')
    template_name = 'menu/delete_location.html'

class IndividuDelete(DeleteView):
    model = Individual
    success_url = reverse_lazy('Liste des modifications')
    template_name = 'menu/delete_individu.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        try:
            instance_child = Child.objects.get( child=self.object)
            create_modification(subject=self.object, user=request.user,
                              note="Suppression de la relation parent-enfant de " + self.object.first_name + " " + self.object.last_name
                                   + " avec "+ instance_child.relation.parent1.first_name + " " + instance_child.relation.parent1.last_name + " et "
                                   +instance_child.relation.parent2.first_name + " " + instance_child.relation.parent2.last_name)
            instance_child.delete()
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
                                create_modification(subject=enfant, user=request.user,
                                                  note="Suppression des parents de " + enfant.child.first_name + " " + enfant.child.last_name )
                                enfant.delete()

                                create_modification(subject=self.object, user=request.user,
                                              note="Suppression de la relation entre " + str(marriage.parent1 or "None") +" et " + str(marriage.parent2 or "None"))
                            marriage.delete()

                    except Child.DoesNotExist:
                        create_modification(subject=self.object, user=request.user,
                                          note="Suppression de la relation entre " + str( marriage.parent1 or "None") + " et " + str(marriage.parent2 or "None"))
                        marriage.delete()
                    if marriage.parent1 is not None:
                        marriage.parent1.user_who_last_updated = request.user
                        marriage.parent1.save()
                    if marriage.parent2 is not None:
                        marriage.parent2.user_who_last_updated = request.user
                        marriage.parent2.save()

        except Relationship.DoesNotExist:
            pass

        create_modification(subject=self.object, user=request.user,
                         note="Suppression de l'individu " + self.object.first_name + " " + self.object.last_name)
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
    template_name = 'menu/location_detail.html'

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


def is_current_user_admin(user=None):
    query_group = Group.objects.filter(user = user)
    if 'tree_admin' in query_group[0].name:
        return True
    return False

def import_gedcom(request):
    form = ReadFileForm()
    if request.method == 'POST':
        form = ReadFileForm(request.POST, request.FILES)
        if form.is_valid():
            if not request.FILES['fichier'].name.endswith(".ged"):
                return render(request, 'menu/read_file.html',{'content':[' Veuillez entrez un fichier de type GEDCOM (et finissant par .ged).', form]})
            else:
                print("else")
                import_from_gedcom(request)
                return render(request, 'menu/home.html')
    return render(request, 'menu/read_file.html', locals())


def update_individu(request, id=None):
    instance=get_object_or_404(Individual,id=id)
    form=IndividualForm(request.POST or None, request.FILES or None,instance=instance)

    if form.is_valid():
        instance=form.save(commit=False)
        instance.user_who_last_updated = request.user
        instance.save()
        create_modification(subject=instance, user=request.user, note="modification des données personnelles de "+ instance.first_name + " " +instance.last_name)
        return HttpResponseRedirect(instance.get_absolute_url())
    context={
                "form":form,}
    return render(request, 'menu/update_from_form.html', context )

def remove_parents(request, id):
    relation = get_object_or_404(Relationship, id=id)
    try:
        instance_child=Child.objects.get(relation=relation)
    except Child.DoesNotExist:
        pass
    context = {"child": instance_child}
    if request.method == "POST":
        try:
            if instance_child.relation.parent1 is not None:
                instance_child.relation.parent1.user_who_last_updated = request.user
                instance_child.relation.parent1.save()
            if instance_child.relation.parent2 is not None:
                instance_child.relation.parent2.user_who_last_updated = request.user
                instance_child.relation.parent2.save()
            if instance_child.child is not None:
                subject_modif = instance_child.child
                subject_modif.user_who_last_updated = request.user
                subject_modif.save()
            create_modification(subject=subject_modif, user=request.user,
                              note="Suppression de la relation parent - enfant avec " + str(instance_child.relation.parent1 or "None") + " et " + str(instance_child.relation.parent2 or "None"))
        except Child.DoesNotExist:
            pass

        instance_child.delete()
        return HttpResponseRedirect(subject_modif.get_absolute_url())
    return render(request, "menu/delete_child.html", context)


def update_place(request, id=None):
    instance=get_object_or_404(Location,id=id)
    form=LocationForm(request.POST or None, instance=instance)

    if form.is_valid():
        instance=form.save(commit=False)
        instance.user_who_last_updated = request.user
        instance.save()
        create_modification(subject=instance, user=request.user, note="modification d'un lieu" )
        return HttpResponseRedirect(instance.get_absolute_url())
    context={"form":form,}
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
            try:
                relation = Relationship.objects.get(parent1=relation.parent1, parent2=relation.parent2)
            except Relationship.DoesNotExist:
                try:
                    relation = Relationship.objects.get(parent1=relation.parent2, parent2=relation.parent1)
                except Relationship.DoesNotExist:
                    relation.save()

            create_modification(subject=relation.parent1, user=request.user,
                             note="ajout d'une relation avec " + relation.parent2.first_name + " " +  relation.parent2.last_name)
            instance_child.relation = relation
            instance_child.save()
            create_modification(subject=instance, user=request.user, note="ajout ou modification d'une relation parent-enfant")
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
            request_post=get_first_query(request.POST)
            if instance.gender == 'M':
                request_post["parent1"]=id
            else:
                request_post["parent2"] = id
            form = RelationshipForm(request_post or None)
            if form.is_valid():
                form.clean()
                relation = form.save(commit=False)
                instance.user_who_last_updated = request.user
                instance.save()
                relation.save()
                create_modification(subject=instance, user=request.user, note="ajout d'un(e) partenaire existant pour "+instance.first_name + " "+instance.last_name)
            return HttpResponseRedirect(instance.get_absolute_url())
    context={"form":form}
    return render(request, 'menu/relation_add.html', context )

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
                create_modification(subject=relation.parent1, user=request.user,
                                 note="modification d'un(e) relation pour " + relation.parent1.first_name + " " + relation.parent1.last_name)
            if relation.parent2 is not None:
                relation.parent2.user_who_last_updated = request.user
                relation.parent2.save()
                create_modification(subject=relation.parent2, user=request.user,
                                 note="modification d'un(e) relation pour " + relation.parent2.first_name + " " + relation.parent2.last_name)
        return HttpResponseRedirect(relation.parent1.get_absolute_url())
    context = {"form": form}
    return render(request, 'menu/relation_update.html', context)

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
            create_modification(subject=subject_modif, user=request.user,
                              note="Suppression de la relation entre " + str(self.object.parent1 or "None") + " et " + str(self.object.parent2 or "None"))
        except Relationship.DoesNotExist:
            pass

        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())

def add_children(request, id=None):
    print("add_children")
    relation = get_object_or_404(Relationship, id=id)
    child_relation = Child(relation=relation)
    form = ChildForm(request.POST or None, instance = child_relation)
    instance = get_object_or_404(Individual, id=relation.parent1.id)
    if 'save' in request.POST:
        if form.is_valid():
            form.clean()
            child_relation = form.save(commit=False)
            try:
                check_child = Child.objects.get(child=child_relation.child)
                message_error=str(child_relation.child or "None") + " a déjà des parents!"
                context = {
                    "message_error" : message_error,
                    "form": form
                }
                return render(request, 'menu/individual_add_children.html', context)
            except  Child.DoesNotExist:
                print(child_relation)
                print(child_relation.child)
                create_modification(subject=instance, user=request.user,
                                 note="ajout d'une nouvelle relation enfant-parent " + str(child_relation.child or "None"))
                instance.user_who_last_updated = request.user
                instance.save()
                child_relation.relation=relation
                child_relation.save()
                return HttpResponseRedirect(instance.get_absolute_url())
    context = {"form": form}
    return render(request, 'menu/individual_add_children.html', context)


def add_location_html(request):
    form = LocationForm(None)
    if 'save_location' in request.POST:
            print("yes there is a save_location")
            form = LocationForm(request.POST or None)
            if form.is_valid() :
                form.clean()
                loc = form.save(commit=False)
                loc.save()
                create_modification(subject=loc, user=request.user, note="ajout d'un lieu")
                parameters_as_string = 'id=' + str(loc.id)
                return HttpResponse('<script type="text/javascript">window.opener.reload_places('+parameters_as_string+');window.close();</script>')
    context={"form":form,}
    return render(request, 'menu/location_add.html', context )

def add_individual_html(request):
    form = IndividualForm(None)
    if 'save_individual' in request.POST:
            form = IndividualForm(request.POST or None)
            if form.is_valid() :
                form.clean()
                ind = form.save(commit=False)
                if ind.gender is None:
                    ind.gender='A'
                ind.save()
                create_modification(subject=ind, user=request.user, note="ajout d'un nouvelle individu : "+ ind.first_name + " " + ind.last_name)
                parameters_as_string = 'id=' + str(ind.id)
                return HttpResponse('<script type="text/javascript">window.opener.reload_individuals('+parameters_as_string+');window.close();</script>')

    context={"form":form,}
    return render(request, 'menu/individual_add.html', context )

def place_list(request):
    p = Location.objects.all()
    p2=list(p.values('id','city','department','country','church'))
    return JsonResponse({"places":p2})

def individual_list(request):
    p = Individual.objects.all()
    p2=list(p.values('id','first_name','last_name','date_of_birth','date_of_death'))
    for individu in p2 :
        for date in ['date_of_birth','date_of_death']:
            if individu[date] is None or individu[date] == '':
                individu[date]='?'
            else:
                individu[date] = individu[date].split()[-1]
    return JsonResponse({"individuals":p2})

def check_tree(request):
    results = []
    age_limite_de_vie = 100
    age_minimum_pour_mariage = 15
    age_minimum_pour_enfant = 15
    age_maximum_homme_pour_enfant = 70
    age_maximum_femme_pour_enfant = 50
    if 'check' in request.POST:
        all_individuals = Individual.objects.all()
        for indiv in all_individuals:
            year_birth = indiv.year_birth()
            year_death = indiv.year_death()
            age = indiv.age()
            if age == "inconnu":
                pass
            elif int(age) > age_limite_de_vie and not indiv.is_deceased:
                results+=[indiv.first_name+" "+indiv.last_name+" est âgé(e) de "+str(age)+" ans, êtes-vous sûr qu'il ou elle est encore en vie?\n"]
            elif int(age) < 0:
                results+=[indiv.first_name+" "+indiv.last_name+" est né(e) en "+year_death+" mais est mort en "+year_death+"!\n"]

            all_marriages = Relationship.objects.filter( Q(parent1=indiv) | Q(parent2 =indiv) )
            for marriage in all_marriages:
                marriage.nice_marriage_date()
                marriage.nice_divorce_date()
                dates_event={ marriage.year_marriage():"mariage",
                              marriage.year_divorce():"divorce"}
                for year in dates_event:
                    if year=='?':
                        pass
                    elif year_birth!='?' and int(year)<int(year_birth)+age_minimum_pour_mariage:
                        if dates_event[year]=="mariage":
                            results += [indiv.first_name + " " + indiv.last_name + " est né(e) en "+
                                        year_birth + " mais s'est marié(e) en " + year + "!\n"]
                        else:
                            results += [indiv.first_name + " " + indiv.last_name + " est né(e) en "+
                                        year_birth + " mais a divorcé en " + year + "!\n"]
                    elif year_death!='?' and int(year)>int(year_death):
                        if dates_event[year]=="mariage":
                            results += [indiv.first_name + " " + indiv.last_name + " est mort(e) en "+
                                    year_death + " mais s'est marié(e) en " + year + "!\n"]
                        else:
                            results += [indiv.first_name + " " + indiv.last_name + " est mort(e) en "+
                                        year_death + " mais a divorcé en " + year + "!\n"]
            child_relation = Child.objects.filter( Q(child=indiv))
            for relation in child_relation:
                list_parent = [relation.relation.parent1, relation.relation.parent2]
                list_parent = [i for i in list_parent if i]
                for parent in list_parent:
                    year_birth_parent = parent.year_birth()
                    year_death_parent = parent.year_death()
                    gender = parent.gender
                    if year_birth=='?':
                        pass
                    elif year_birth_parent!='?':
                        age_parent=int(year_birth)-int(year_birth_parent)
                        if int(year_birth_parent)>int(year_birth)+age_minimum_pour_enfant:
                            results += [indiv.first_name + " " + indiv.last_name + " est né(e) en "+ year_birth + " mais son parent " + parent.first_name + " "+ parent.last_name+" n'avais que "
                            +(year_birth-year_birth_parent)+"!\n"]
                        if int(year_birth_parent)+age_maximum_femme_pour_enfant<int(year_birth) and gender=='F':
                            results += [indiv.first_name + " " + indiv.last_name + " est né(e) en "+year_birth + " mais sa mère " + parent.first_name + " "+ parent.last_name+" avais déjà "+str(age_parent)+"!\n"]
                        if int(year_birth_parent)+age_maximum_homme_pour_enfant<int(year_birth) and gender!='F':
                            results += [indiv.first_name + " " + indiv.last_name + " est né(e) en "+year_birth + " mais son père " + parent.first_name + " "+ parent.last_name+" avais déjà "
                            +str(age_parent)+"!\n"]
                    elif year_death_parent!='?' and int(year_death_parent)<int(year_birth):
                        results += [indiv.first_name + " " + indiv.last_name + " est né(e) en "+ year_birth + " mais son parent " + parent.first_name + " " + parent.last_name + " est mort(e) avavnt en " + year_death_parent + "!\n"]
    context={"results": results,}
    return render(request, 'menu/checking_tree.html', context)

