from django.shortcuts import render
from .forms import ReadFileForm, IndividualForm
from django.shortcuts import get_object_or_404

from datetime import datetime
from django.db import models
from .models import Location, Individual, Relationship, Child
from django.contrib.auth.models import Group

from django.views import generic
import operator
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from functools import reduce
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
#from menu.middleware import get_current_user



pays_connus = ["FRANCE","POLOGNE","ALLEMAGNE","ALGERIE", "ITALIE","ESPAGNE","ROYAUNE-UNI", "ANGLETERRE"]

#global current_user

class IndividualListView(generic.ListView):
    model = Individual
    paginate_by = 50
    #context_object_name = 'Liste des noms'   # your own name for the list as a template variable
    #queryset = Individual.objects.exclude(last_name='?').exclude(first_name='?').order_by('last_name')
    template_name = 'menu/home.html' 
    #"#def listing(request):
	#"    individu_list = Individual.objects.all()
	#    paginator = Paginator(individu_list, 25) # Show 25 contacts per page
#
	  #  page = request.GET.get('page')
#	 #   individus = paginator.get_page(page)
#	    return render(request, 'home.html', {'Individus': individus})
#    def url_add_query(context, **kwargs):
#	    request = context.get('request')

#	    get = request.GET.copy()
#	    get.update(kwargs)

#	    path = '%s?' % request.path
#	    for query, val in get.items():
#	        path += '%s=%s&' % (query, val)
#
#	    return path[:-1]

    def get_queryset(self):
        query = self.request.GET.get('q')
        
        d=Individual.objects.all()
        current_user=self.request.user
        if not is_current_user_admin(current_user):
        	#print(user, " is admin")
        	d=d.exclude(private=True)

   

        if query:
        	query_element=query.split(" ")
        	#tag_qs = reduce(operator.or_, (Q(last_name__icontains=x) for x in query_element))
        	#tag_qs2 = reduce(operator.or_, (Q(first_name__icontains=x) for x in query_element))
        	
        	for element in query_element:
        		d=d.filter(Q(last_name__icontains=element)  | Q(first_name__icontains=element) )
        	#d=Individual.objects.filter(tag_qs2)
        	if '?' not in query:
        		d=d.exclude(last_name='?').exclude(first_name='?')

        	return d
        else:
            return Individual.objects.exclude(last_name='?').exclude(first_name='?')

class IndividualDetailView(generic.DetailView):
    model = Individual
   
#class IndividualUpdateView(generic.DetailView):
#    model = Individual
#    template_name = 'menu/individual_update.html' 

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

#def get_spouses(individu):
 #   try:
  #      
 #       spouses = Relationship.objects.filter(Q(parent1=individu) | Q(parent2=individu))
 #       if not is_current_user_admin(current_user):
 #       	spouses=spouses.exclude(private=True)
 #       return spouses
 #   except Relationship.DoesNotExist:
 #       #print("Pas de relations connues",self)
 #       return []


#def get_children(individu):
#    try:
#        
#        children = Child.objects.filter(Q(parent1=individu) | Q(parent2=individu))
#        if not is_current_user_admin(current_user):
#        	children=children.exclude(private=True)
#        return children
#    except Child.DoesNotExist:
#        #print("Pas de relations connues",self)
#        return []

#def get_parents(individu):
#    try:
#        
#        
#        line = Child.objects.filter(Q(child=individu))
#        if not is_current_user_admin(current_user):
 #       	line=line.exclude(private=True)
 #       return line
 #   except Child.DoesNotExist:
 #       #print("Pas de parent connu",self)
 #       return []
    
   
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
    """change members being in a special team"""

    #queryset = Individual.objects.filter(id=ind_id)

    #if request.POST:
    #####    form = IndividualForm(request.POST, instance=queryset)
    #####    if form.is_valid():
    ####        form.save()
    ###        return redirect('index')
    ##else:
    #    form = IndividualForm(instance=queryset)#

    #template = 'menu/#individual_update.html'
  #  kwvars = {
    #    'form': form#,
  #  }
    #return render_to_response(template, kwvars, RequestContext(request)#)
    instance=get_object_or_404(Individual,id=id)
    #instance=Individual.objects.filter(id=id)
    print(instance)
    print("bouh")
    form=IndividualForm(request.POST or None, instance=instance)
    #if request.POST:
    #    form = IndividualForm(request.POST)

    if form.is_valid():
        instance=form.save(commit=False)
        instance.save()
        return HttpResponseRedirect(instance.get_absolute_url())
    context={ 
                "form":form,}
    return render(request, 'menu/individual_detail_update.html', context )

    #    ind = Individual.objects.get(id=individual_id)
    #    form = IndividualForm(request.POST, instance = ind)
    #    form.save() #cleaned indenting, but would not save unless I added at least 6 characters.
    #    return redirect('/index/')
    #else:
    #    ind = Individual.objects.get(id = individual_id)       
    #    form = IndividualForm(instance=ind)

     #   return render_to_response('menu/individual_update.html',{ 'form':form }, context_instance=RequestContext(request))