from django.db import models
from datetime import date,datetime
from django.db.models import Q
import svgwrite
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from django.template import RequestContext, Template
from svgwrite.container import Hyperlink
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import fields
from django.contrib.contenttypes.fields import GenericRelation


GENDER_CHOICES = (
        ('F', 'femme'),
        ('M', 'homme'),
        ('A', 'autre'),
    )

STATUS_CHOICES = (
        ('mariage ou Pacs', 'mariage ou Pacs'),
        ('concubinage', 'concubinage'),
        ('divorce', 'divorce'),
    )

MONTH_CHOICES = (
        ('JAN', 'janvier'),
        ('FEB', 'février'),
        ('MAR', 'mars'),
        ('APR', 'avril'),
        ('MAY', 'mai'),
        ('JUN', 'juin'),
        ('JUL', 'juillet'),
        ('AUG', 'août'),
        ('SEP', 'septembre'),
        ('OCT', 'octobre'),
        ('NOV', 'novembre'),
        ('DEC', 'décembre'),
    )

month_list=["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
month_list_french=["janvier","février","mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre"]
# Create your models here

class Modification(models.Model):
    #subject = models.ForeignKey(Individual,on_delete=models.CASCADE)
    #subject_place = models.ForeignKey(Location)
    #subject = fields.GenericForeignKey('subject_ind', 'subject_place')
    content_type = models.ForeignKey(ContentType,on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True)
    subject = fields.GenericForeignKey('content_type', 'object_id')
    user=models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date=models.DateTimeField()
    test=models.DateTimeField(null=True)
    note= models.CharField(max_length=100,null=True, blank=True)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        self.date = datetime.now()
        return super(Modification, self).save(*args, **kwargs)

class Location(models.Model):
    city = models.CharField(max_length=40,null=True, blank=True)
    country = models.CharField(max_length=40)
    department = models.CharField(max_length=30,null=True, blank=True)
    church = models.CharField(max_length=30,null=True, blank=True)
    city_today = models.CharField(max_length=40,null=True, blank=True)
    country_today = models.CharField(max_length=40,null=True, blank=True)
    #modif = GenericRelation(Modification)
    class Meta:
        ordering = ["country", "city", "church"]
        verbose_name_plural = "Place"

    def __str__(self) :

        city="Inconnu"
        department="Inconnu"
        church=""
        if self.city is not None:
            city=self.city
        if self.department is not None:
            department=self.department
        if self.church is not None:
            church=self.church

        return city  + ", " + department + ", " + self.country + ", " + church

    def get_absolute_url(self):
        return "/lieu/%i" % self.id

class Individual(models.Model):
    private =  models.BooleanField(default=False)
    gedcom_id = models.CharField(max_length=10, null=True)
    first_name = models.CharField(max_length=70,null=False, blank=True,default="?")
    last_name = models.CharField(max_length=30,null=False, blank=True,default="?")
    gender = models.CharField( max_length=1, choices=GENDER_CHOICES,null=True, blank=True)
    is_deceased=models.BooleanField(default=False)
    image = models.ImageField("image",
                              upload_to='uploads/img',
                              null=True, blank=True)
    date_of_birth  =  models.CharField(max_length=12,null=True, blank=True)
    date_of_death  =  models.CharField(max_length=12,null=True, blank=True)
    place_of_birth = models.ForeignKey(Location,null=True, related_name='place_of_birth', blank=True, on_delete=models.SET_NULL)
    place_of_death = models.ForeignKey(Location,null=True, related_name='place_of_death', blank=True, on_delete=models.SET_NULL)
    place_of_residence = models.ForeignKey(Location,null=True, blank=True, on_delete=models.SET_NULL)
    occupation = models.CharField(max_length=100,null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    email = models.CharField(max_length=30,null=True, blank=True)
    date_of_creation = models.DateTimeField(auto_now_add=True)
    date_of_last_update = models.DateTimeField(auto_now=True)
    user_who_created =  models.ForeignKey(User, default=1, related_name='user_who_created')
    user_who_last_updated = models.ForeignKey(User, default=1, related_name='user_who_last_updated')
    #modif = GenericRelation(Modification)
    #family_as_parent = models.ForeignKey('Family', on_delete=models.PROTECT,null=True, related_name='family_as_parent')
    #family_as_child = models.ForeignKey('Family', on_delete=models.PROTECT,null=True, related_name='family_as_child')
    

    class Meta:
        ordering = ["last_name", "first_name", "date_of_birth"]
        verbose_name_plural = "Individu"
    def __str__(self):
        #from .views import is_current_user_admin
        #if self.date_of_birth:
        #    return self.first_name + " " + self.last_name + " " +  self.date_of_birth
        return self.get_first_name() + " " + self.get_last_name()

    def get_absolute_url(self):
        return "/individu/%i" % self.id
        #return reverse("posts:detail", kwargs={"id":self.id})


    def get_first_name(self, is_admin=True):
        #from .views import is_current_user_admin
        if not self.private or is_admin:
            return self.first_name
        else:
            return "?"


    def get_last_name(self,is_admin=True):
        #from .views import is_current_user_admin
        if not self.private or is_admin:
            return self.last_name
        else:
            return "?"

    def nice_birthdate(self):
            for month in month_list:
                if month in self.date_of_birth:
                    return self.date_of_birth.replace(month, month_list_french[month_list.index(month)])
            return self.date_of_birth

    def nice_deathdate(self):
            for month in month_list:
                if month in self.date_of_death:
                    return self.date_of_death.replace(month, month_list_french[month_list.index(month)])
            return self.date_of_death


    def get_spouses(self):
        #from .views import is_current_user_admin
        try:
            spouses = Relationship.objects.filter(Q(parent1=self) | Q(parent2=self))
            #if not is_current_user_admin():
            #     spouses=spouses.exclude(parent1__private='t').exclude(parent2__private='t')

            return spouses
        except Relationship.DoesNotExist:
            #print("Pas de relations connues",self)
            return []

    def get_children(self):
        #from .views import is_current_user_admin
        try:
            children = Child.objects.filter(Q(parent1=self) | Q(parent2=self))
            #if not is_current_user_admin():
            #     children=children.exclude(parent1__private='t').exclude(parent2__private='t')
            return children
        except Child.DoesNotExist:
            #print("Pas de relations connues",self)
            return []

    def get_parents(self):
        try: 
            line = Child.objects.filter(Q(child=self))

            return line
        except Child.DoesNotExist:
            #print("Pas de parent connu",self)
            return []


    def get_tree(self,is_admin=True):
        #print("hey you pony pony")
        #print(self.first_name)
        #print(self.id)
        size_font=5
        #svg_tag = format_html('<svg viewBox="0 0 512 512" class="icon">' '<use xlink:href="#{id}" class="sym"></use>'  '</svg>', name=self.first_name, id=self.id)
        #print(svg_tag)
        #return mark_safe(svg_tag)
        dwg = svgwrite.Drawing('test.svg', profile='full', text_anchor='middle')
        parents=self.get_parents()
        print(parents.count())
        spouses=self.get_spouses()
        print(spouses.count())
        children=self.get_children()
        print(children.count())
        x_individu=50
        y_individu=60
        space_name=8
        space_between_x=50
        space_between_y=space_name+30

        max_width=max(2,100+50*children.count()+40*(spouses.count()))
        max_heigth=(x_individu+space_name)*3
        dwg.viewbox(width=max_width, height=max_heigth)
        #dwg.fit(scale='slice')
        #dwg.stretch()
        #dwg.scale(2)
        print(max_width,max_heigth)
        
        
        link = Hyperlink(str(self.id), target='_top')
        #link = dwg.add(svgwrite.container.Hyperlink('http://stackoverflow.com'))
        link.add(dwg.text("".join(self.get_first_name(is_admin)), insert=(x_individu, y_individu), fill='black', text_anchor='middle', font_size=str(size_font-1) + "px"))
        link.add(dwg.text("".join(self.get_last_name(is_admin)), insert=(x_individu, y_individu+space_name), fill='black', text_anchor='middle', font_size=str(size_font) + "px"))
        dwg.add(link)
        
        for parent in parents:
            #print(parent.parent1)
            #print(parent.parent2.last_name)
            if parent.parent1:
                link = Hyperlink(str(parent.parent1.id), target='_top')

                link.add(dwg.text("".join(parent.parent1.get_first_name(is_admin)), insert=(x_individu-(space_between_x/2), y_individu-space_between_y), fill='black', text_anchor='middle',font_size=str(size_font-1) + "px"))
                link.add(dwg.text("".join(parent.parent1.get_last_name(is_admin)), insert=(x_individu-(space_between_x/2), y_individu-space_between_y+space_name), fill='black',text_anchor='middle', font_size=str(size_font) + "px"))
                dwg.add(link)

                dwg.add(dwg.line((x_individu-(space_between_x/2), y_individu-space_between_y+space_name+size_font), (x_individu-(space_between_x/2), y_individu-space_between_y+space_name+size_font+5), stroke='grey'))

            #dwg.add(dwg.line((x_individu-20, y_individu-20+size_font), (x_individu, y_individu-size_font), stroke='grey'))
            if parent.parent2:
                link = Hyperlink(str(parent.parent2.id), target='_top')
                link.add(dwg.text("".join(parent.parent2.get_first_name(is_admin)), insert=(x_individu+(space_between_x/2), y_individu-space_between_y), fill='black', text_anchor='middle',font_size=str(size_font-1) + "px"))
                link.add(dwg.text("".join(parent.parent2.get_last_name(is_admin)), insert=(x_individu+(space_between_x/2), y_individu-space_between_y+space_name), fill='black', text_anchor='middle',font_size=str(size_font) + "px"))
                dwg.add(link)
                dwg.add(dwg.line((x_individu+(space_between_x/2), y_individu-space_between_y+space_name+size_font), (x_individu+(space_between_x/2), y_individu-space_between_y+space_name+size_font+5), stroke='grey'))
            if parent.parent1 and parent.parent2:
                dwg.add(dwg.line((x_individu-(space_between_x/2), y_individu-space_between_y+space_name+size_font+5), (x_individu+(space_between_x/2), y_individu-space_between_y+space_name+size_font+5), stroke='grey'))
                dwg.add(dwg.line((x_individu, y_individu-space_between_y+space_name+size_font+5), (x_individu, y_individu-size_font), stroke='grey'))
            elif parent.parent1:
                dwg.add(dwg.line((x_individu-(space_between_x/2), y_individu-space_between_y+space_name+size_font+5),
                                 (x_individu, y_individu - size_font), stroke='grey'))
            elif parent.parent2:
                dwg.add(dwg.line(
                    (x_individu + (space_between_x / 2), y_individu - space_between_y + space_name + size_font + 5),
                    (x_individu, y_individu - size_font), stroke='grey'))



        #dwg = svgwrite.Drawing('test.svg')
        nb_child = 0
        nb_spouse=0
        for spouse in spouses:
            if spouse.parent1!=self:
                real_spouse=spouse.parent1
            else:
                real_spouse=spouse.parent2
            if is_admin or not real_spouse.private:
                nb_spouse+=1
                nb_child_for_spouse = 0
                
                x_spouse=x_individu+50*nb_spouse+50*nb_child
                y_spouse=y_individu
                if real_spouse:
                    link = Hyperlink(str(real_spouse.id), target='_top')
                    link.add(dwg.text("".join(real_spouse.get_first_name(is_admin)), insert=(x_spouse, y_spouse), fill='black',text_anchor='middle',font_size=str(size_font-1)+"px"))
                    link.add(dwg.text("".join(real_spouse.get_last_name(is_admin)), insert=(x_spouse, y_spouse+space_name), fill='black',text_anchor='middle', font_size=str(size_font) + "px"))
                    dwg.add(link)
                    dwg.add(dwg.line((x_individu, y_individu+space_name+size_font), (x_individu,  y_individu+space_name+2*nb_spouse+size_font), stroke='grey'))
                    dwg.add(dwg.line((x_spouse, y_spouse+space_name+size_font), (x_spouse,  y_spouse+space_name+2*nb_spouse+size_font), stroke='grey'))
                    dwg.add(dwg.line((x_individu,  y_individu+space_name+2*nb_spouse+size_font), (x_spouse,  y_spouse+space_name+2*nb_spouse+size_font), stroke='grey'))
                for child in children:
                    
                    if child.parent1==real_spouse or child.parent2==real_spouse and ( is_admin or not child.child.private):
                        nb_child += 1

                        link = Hyperlink(str(child.child.id), target='_top')
                        link.add(dwg.text("".join(child.child.get_first_name(is_admin)), insert=(space_between_x*nb_child+space_between_x*(nb_spouse-1), y_individu+space_between_y), fill='black', text_anchor='middle',font_size=str(size_font-1) + "px"))
                        link.add(dwg.text("".join(child.child.get_last_name(is_admin)), insert=(space_between_x*nb_child+space_between_x*(nb_spouse-1),  y_individu+space_between_y+space_name), fill='black', text_anchor='middle', font_size=str(size_font) + "px"))
                        dwg.add(link)
                        dwg.add(dwg.line((space_between_x*nb_child+space_between_x*(nb_spouse-1),  y_individu+space_between_y-size_font), (space_between_x*nb_child+space_between_x*(nb_spouse-1),  y_individu+space_between_y-2-size_font), stroke='grey'))
                        if nb_child_for_spouse>0:

                            dwg.add(dwg.line((space_between_x*nb_child+space_between_x*(nb_spouse-1),  y_individu+space_between_y-2-size_font), (space_between_x*(nb_child-1)+space_between_x*(nb_spouse-1),  y_individu+space_between_y-2-size_font), stroke='grey'))

                        nb_child_for_spouse+=1
                if nb_child_for_spouse>0:
                    if real_spouse:
                        dwg.add(dwg.line( ((x_spouse+x_individu)/2,  y_spouse+space_name+2*nb_spouse+size_font), (space_between_x*(nb_child-(nb_child_for_spouse-1)/2)+space_between_x*(nb_spouse-1),  y_individu+space_between_y-2-size_font), stroke='grey'))
                    else:
                        dwg.add(
                            dwg.line((x_individu,  y_individu+space_name+2*nb_spouse+size_font), (space_between_x * (nb_child - (nb_child_for_spouse - 1) / 2) + space_between_x * (nb_spouse - 1), y_individu + space_between_y - 2 - size_font), stroke='grey'))

                        #dwg.add(dwg.line((x_individu, y_individu+10+size_font), (50*nb_child+40*(nb_spouse-1),  y_individu+30-size_font), stroke='blue'))
                        #dwg.add(dwg.line((x_spouse, y_spouse+10+size_font), (50*nb_child+40*(nb_spouse-1),  y_individu+30-size_font), stroke='red'))
        #dwg.add(dwg.line(start=(0, 0), end=(450, 400), stroke='blue'))
        #print(dwg)
        #dwg.save()
        #print(dwg.tostring())
        #print(dwg.get_id())
        #template = Template(dwg.tostring())
        #print(template)
        #svg_data = generate_some_svg_data()

        return dwg.tostring()


    def get_tree_hide(self):
        return self.get_tree(False)

    def age(self):
        if self.date_of_birth:
            birth=self.date_of_birth.split(" ")
            if len(birth)==1:
                birth_day=1
                birth_month=1
                birth_year=int(birth[0])
            elif len(birth)==2:
                birth_day=1
                birth_month=month_list.index(birth[0])+1
                birth_year=int(birth[1])
            else:
                birth_day=int(birth[0])
                birth_month=month_list.index(birth[1])+1
                birth_year=int(birth[2])
            birth_datetime=date(birth_year,birth_month,birth_day)
            #print(birth_datetime)
        if self.date_of_death:
            death=self.date_of_death.split(" ")
            if not self.is_deceased:
                self.is_deceased=True
                self.save()
            if len(death)==1:
                death_day=1
                death_month=1
                death_year=int(death[0])
            elif len(death)==2:
                death_day=1
                death_month=month_list.index(death[0])+1
                death_year=int(death[1])
            else:
                death_day=int(death[0])
                death_month=month_list.index(death[1])+1
                death_year=int(death[2])
            death_datetime=date(death_year,death_month,death_day)
            #print(death_datetime)

            if self.date_of_birth is not None:
                num_years = int((death_datetime - birth_datetime).days / 365.2425)
                #print(num_years)
        elif not self.is_deceased and self.date_of_birth:
            today = date.today()
            num_years = int((today - birth_datetime).days / 365.2425)
            #print(num_years)
            if num_years>130:
                if not self.is_deceased:
                    self.is_deceased=True
                    self.save()
                return "inconnu"
        else:
            return "inconnu"
        
        return num_years




class Relationship(models.Model):
    gedcom_id = models.CharField(max_length=10,null=True)
    parent1 = models.ForeignKey('Individual',null=True,related_name='person1',on_delete=models.SET_NULL)
    parent2 = models.ForeignKey('Individual',null=True,related_name='person2',on_delete=models.SET_NULL)
    #children = models.ManyToManyField(Individual, related_name='children_set')
    date_of_marriage  = models.CharField(max_length=12,null=True, blank=True)
    place_of_marriage = models.ForeignKey(Location, related_name='place_of_marriage',null=True, blank=True, on_delete=models.SET_NULL)
    date_of_divorce  = models.CharField(max_length=12,null=True, blank=True)
    #place_of_divorce = models.ForeignKey(Location, related_name='place_of_divorce')
    status =  models.CharField( max_length=16, choices=STATUS_CHOICES)
    class Meta:
        ordering = ["parent1", "parent2"]
        #ordering = ["gedcom_id"]
        #ordering = ["id"]
        verbose_name_plural = "Relation"

    def __str__(self):
        if self.parent1 and self.parent2:
            return  self.parent1.first_name + " " + self.parent1.last_name + " " + self.parent2.first_name + " " + self.parent2.last_name
        elif self.parent1:
            return   self.parent1.first_name + " " + self.parent1.last_name
        elif self.parent2:
            return  self.parent2.first_name + " " + self.parent2.last_name

    def nice_marriagedate(self):
            if self.date_of_marriage is not None:
                for month in month_list:
                    if month in self.date_of_marriage:
                        return self.date_of_marriage.replace(month, month_list_french[month_list.index(month)])
            return self.date_of_marriage


class Child(models.Model):
    child = models.ForeignKey('Individual',null=True,related_name='child',on_delete=models.CASCADE)
    parent1 = models.ForeignKey('Individual',null=True,related_name='father', blank=True, on_delete=models.SET_NULL)
    parent2 = models.ForeignKey('Individual',null=True,related_name='mother', blank=True, on_delete=models.SET_NULL)
    class Meta:
        ordering = ["child"]
        verbose_name_plural = "Enfant"

    def __str__(self):
        return self.child.first_name + " " + self.child.last_name





