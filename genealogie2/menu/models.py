from django.db import models
from datetime import date
from django.db.models import Q
import svgwrite
from svgwrite.container import Hyperlink
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import fields
from django.utils import timezone


GENDER_CHOICES = (
        ('F', 'femme'),
        ('M', 'homme'),
        ('A', 'autre'),
    )

STATUS_CHOICES = (
        ('mariage ou Pacs', 'mariage ou Pacs'),
        ('concubinage', 'concubinage'),
        ('divorce', 'divorce'),
        ('autre', 'autre'),
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
def year_from_date(date):
    if date is None:
        return "?"
    year = date.split(" ")[-1]
    if len(year)==0:
        return "?"
    return year

def nice_date(date):
    if date is not None:
        for month in month_list:
            if month in date:
                return date.replace(month, month_list_french[month_list.index(month)])
    return date

def change_date_format(date):
    if date is not None and "/" in date:
        date_split=date.split("/")
        if len(date_split)==2:
            return month_list[int(date_split[0])-1] + " " + date_split[1]
        elif len(date_split)==3:
            return date_split[0] + " " + month_list[int(date_split[1]) - 1] + " " + date_split[2]
    return date

class Modification(models.Model):
    content_type = models.ForeignKey(ContentType,on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True)
    subject = fields.GenericForeignKey('content_type', 'object_id')
    user=models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date=models.DateTimeField()
    note= models.CharField(max_length=100,null=True, blank=True)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        self.date = timezone.now()
        return super(Modification, self).save(*args, **kwargs)

class Location(models.Model):
    city = models.CharField(max_length=40,null=True, blank=True)
    country = models.CharField(max_length=40)
    department = models.CharField(max_length=30,null=True, blank=True)
    church = models.CharField(max_length=30,null=True, blank=True)
    city_today = models.CharField(max_length=40,null=True, blank=True)
    country_today = models.CharField(max_length=40,null=True, blank=True)
    date_of_creation = models.DateTimeField(auto_now_add=True)
    date_of_last_update = models.DateTimeField(auto_now=True)
    user_who_created = models.ForeignKey(User, default=1, on_delete=models.SET("Deleted User"), related_name='user_who_created_location')
    user_who_last_updated = models.ForeignKey(User, default=1, on_delete=models.SET("Deleted User"), related_name='user_who_updated_location')
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
    image = models.ImageField("image",upload_to='uploads/img',null=True, blank=True)
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
    user_who_created =  models.ForeignKey(User, default=1, on_delete=models.SET("Deleted User"), related_name='user_who_created_individual')
    user_who_last_updated = models.ForeignKey(User, default=1, on_delete=models.SET("Deleted User"), related_name='user_who_updated_individual')
    birth_source=models.FileField(upload_to='uploads/src',null=True, blank=True)
    death_source = models.FileField(upload_to='uploads/src', null=True, blank=True)
    

    class Meta:
        ordering = ["last_name", "first_name", "date_of_birth"]
        verbose_name_plural = "Individu"

    def year_birth(self):
        return year_from_date(self.date_of_birth)

    def year_death(self):
        return year_from_date(self.date_of_death)

    def __str__(self):
        year_birth= year_from_date(self.date_of_birth)
        year_death = year_from_date(self.date_of_death)
        return self.get_first_name() + " " + self.get_last_name() + " (" + year_birth + "-" + year_death + ")"

    def get_absolute_url(self):
        return "/individu/%i" % self.id


    def get_first_name(self, is_admin=True):
        if not self.private or is_admin:
            return self.first_name
        else:
            return "?"


    def get_last_name(self,is_admin=True):
        if not self.private or is_admin:
            return self.last_name
        else:
            return "?"

    def nice_birthdate(self):
        return nice_date(self.date_of_birth)


    def nice_deathdate(self):
        return nice_date(self.date_of_death)



    def get_spouses(self):
        try:
            spouses = Relationship.objects.filter(Q(parent1=self) | Q(parent2=self))
            return spouses
        except Relationship.DoesNotExist:
            return []

    def get_children(self):
        children=Child.objects.none()
        try:
            mariage=Relationship.objects.filter(Q(parent1=self) | Q(parent2=self))
            for m in mariage:
                try:
                    children = children | Child.objects.filter(relation=m).order_by('child__date_of_birth')
                except Child.DoesNotExist:
                      pass

        except Relationship.DoesNotExist:
            pass
        return children

    def get_parents(self):
        try: 
            line = Child.objects.filter(Q(child=self))
            return line
        except Child.DoesNotExist:
            return []


    def get_tree(self,is_admin=True):
        size_font=5
        dwg = svgwrite.Drawing('test.svg', profile='full', text_anchor='middle')
        parents=self.get_parents()
        spouses=self.get_spouses()
        children=self.get_children()
        x_individu=50
        y_individu=60
        space_name=8
        space_between_x=50
        space_between_y=space_name+30
        max_width=max(2,100+50*children.count()+40*(spouses.count()))
        max_heigth=(x_individu+space_name)*3
        dwg.viewbox(width=max_width, height=max_heigth)
        link = Hyperlink(str(self.id), target='_top')
        link.add(dwg.text("".join(self.get_first_name(is_admin)), insert=(x_individu, y_individu), fill='black', text_anchor='middle', font_size=str(size_font-1) + "px"))
        link.add(dwg.text("".join(self.get_last_name(is_admin)), insert=(x_individu, y_individu+space_name), fill='black', text_anchor='middle', font_size=str(size_font) + "px"))
        dwg.add(link)
        
        for parent in parents:
            if parent.relation.parent1:
                link = Hyperlink(str(parent.relation.parent1.id), target='_top')
                link.add(dwg.text("".join(parent.relation.parent1.get_first_name(is_admin)), insert=(x_individu-(space_between_x/2), y_individu-space_between_y), fill='black', text_anchor='middle',font_size=str(size_font-1) + "px"))
                link.add(dwg.text("".join(parent.relation.parent1.get_last_name(is_admin)), insert=(x_individu-(space_between_x/2), y_individu-space_between_y+space_name), fill='black',text_anchor='middle', font_size=str(size_font) + "px"))
                dwg.add(link)
                dwg.add(dwg.line((x_individu-(space_between_x/2), y_individu-space_between_y+space_name+size_font), (x_individu-(space_between_x/2), y_individu-space_between_y+space_name+size_font+5), stroke='grey'))
            if parent.relation.parent2:
                link = Hyperlink(str(parent.relation.parent2.id), target='_top')
                link.add(dwg.text("".join(parent.relation.parent2.get_first_name(is_admin)), insert=(x_individu+(space_between_x/2), y_individu-space_between_y), fill='black', text_anchor='middle',font_size=str(size_font-1) + "px"))
                link.add(dwg.text("".join(parent.relation.parent2.get_last_name(is_admin)), insert=(x_individu+(space_between_x/2), y_individu-space_between_y+space_name), fill='black', text_anchor='middle',font_size=str(size_font) + "px"))
                dwg.add(link)
                dwg.add(dwg.line((x_individu+(space_between_x/2), y_individu-space_between_y+space_name+size_font), (x_individu+(space_between_x/2), y_individu-space_between_y+space_name+size_font+5), stroke='grey'))
            if parent.relation.parent1 and parent.relation.parent2:
                dwg.add(dwg.line((x_individu-(space_between_x/2), y_individu-space_between_y+space_name+size_font+5), (x_individu+(space_between_x/2), y_individu-space_between_y+space_name+size_font+5), stroke='grey'))
                dwg.add(dwg.line((x_individu, y_individu-space_between_y+space_name+size_font+5), (x_individu, y_individu-size_font), stroke='grey'))
            elif parent.relation.parent1:
                dwg.add(dwg.line((x_individu-(space_between_x/2), y_individu-space_between_y+space_name+size_font+5),
                                 (x_individu, y_individu - size_font), stroke='grey'))
            elif parent.relation.parent2:
                dwg.add(dwg.line(
                    (x_individu + (space_between_x / 2), y_individu - space_between_y + space_name + size_font + 5),
                    (x_individu, y_individu - size_font), stroke='grey'))
        nb_child = 0
        nb_spouse=0
        for spouse in spouses:
            if spouse.parent1!=self:
                real_spouse=spouse.parent1
            else:
                real_spouse=spouse.parent2
            if is_admin or real_spouse is None or not real_spouse.private:
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
                    if child.relation.parent1==real_spouse or child.relation.parent2==real_spouse and ( is_admin or not child.child.private):
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
        return dwg.tostring()


    def get_tree_hide(self):
        return self.get_tree(False)

    def age(self):
        if self.date_of_birth:

            self.date_of_birth= change_date_format(self.date_of_birth)
            self.save()
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
        if self.date_of_death:
            self.date_of_death= change_date_format(self.date_of_death)
            self.save()
            death = self.date_of_death.split(" ")
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
            if self.date_of_birth is not None and self.date_of_birth!="":
                num_years = int((death_datetime - birth_datetime).days / 365.2425)
            else:
                return "inconnu"
        elif not self.is_deceased and self.date_of_birth:
            today = date.today()
            num_years = int((today - birth_datetime).days / 365.2425)
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
    date_of_marriage  = models.CharField(max_length=12,null=True, blank=True)
    place_of_marriage = models.ForeignKey(Location, related_name='place_of_marriage',null=True, blank=True, on_delete=models.SET_NULL)
    date_of_divorce  = models.CharField(max_length=12,null=True, blank=True)
    status =  models.CharField( max_length=16, choices=STATUS_CHOICES)
    marriage_source = models.FileField(upload_to='uploads/src', null=True, blank=True)
    divorce_source = models.FileField(upload_to='uploads/src', null=True, blank=True)
    class Meta:
        ordering = ["parent1", "parent2"]
        verbose_name_plural = "Relation"

    def __str__(self):
        if self.parent1 and self.parent2:
            return  self.parent1.first_name + " " + self.parent1.last_name + " " + self.parent2.first_name + " " + self.parent2.last_name
        elif self.parent1:
            return   self.parent1.first_name + " " + self.parent1.last_name
        elif self.parent2:
            return  self.parent2.first_name + " " + self.parent2.last_name
        else:
            return "Vide"

    def year_marriage(self):
        return year_from_date(self.date_of_marriage)

    def year_divorce(self):
        return year_from_date(self.date_of_divorce)


    def nice_marriage_date(self):
        self.date_of_marriage = change_date_format(self.date_of_marriage)
        self.save()
        return  nice_date(self.date_of_marriage)

    def nice_divorce_date(self):
        self.date_of_divorce = change_date_format(self.date_of_divorce)
        self.save()
        return  nice_date(self.date_of_divorce)



class Child(models.Model):
    child = models.ForeignKey('Individual',null=True,related_name='child',on_delete=models.CASCADE)
    relation=models.ForeignKey('Relationship',null=False,related_name='relation', blank=False, on_delete=models.CASCADE)
    class Meta:
        ordering = ["child"]
        verbose_name_plural = "Enfant"

    def __str__(self):
        return self.child.first_name + " " + self.child.last_name