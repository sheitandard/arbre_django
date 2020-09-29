# -*- coding: utf-8 -*-
from .models import  Individual, Relationship, Child
from django.http import HttpResponse
import datetime
from .views import is_current_user_admin
from django.db.models import Q
import io
import zipfile
import os


list_month=["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
def update_child(request):
    all_child=Child.objects.all()
    for child in all_child:
        try:
            relation=Relationship.objects.get(parent1=child.parent1, parent2=child.parent2)
            child.relation=relation
            child.save()
            try:
                print(child)
            except:
                print("not printable")
        except Relationship.DoesNotExist:
            print("pb does not exist")
            print(child)
    return 0

def export_gedcom(request, add_media=False):
    now = datetime.datetime.now()
    name_file="gedcom_"+now.strftime("%Y-%m-%d")+".ged"
    with io.open("gedcom/gedcom_tmp.ged", "w", encoding="utf-8") as file:
        file.write("0 HEAD\n")
        file.write("1 SOUR django_dard-dascot\n")
        file.write("1 DATE "+str(now.day)+" "+list_month[now.month]+" "+str(now.year)+"\n")
        file.write("1 GEDC\n")
        file.write("1 CHAR UTF-8\n")
        file.write("0 @U1@ SUBM\n")
        file.write("1 NAME "+request.user.first_name+" /"+request.user.last_name+"/\n")
        all_indi = Individual.objects.all().order_by('id')
        mariage_all = Relationship.objects.all().order_by('id')
        child_all=Child.objects.all()
        if not is_current_user_admin(request.user):
            all_indi=all_indi.exclude(private=True)
        for indi in all_indi:
            has_note=False
            file.write("0 @I"+str(indi.id)+"@ INDI\n")
            file.write("1 NAME "+indi.first_name+" /"+indi.last_name+"/\n")
            if indi.gender is not None:
                file.write("1 SEX "+indi.gender+"\n")
            if indi.date_of_birth or indi.place_of_birth:
                file.write("1 BIRT\n")
            if indi.date_of_birth:
                file.write("2 DATE "+indi.date_of_birth+"\n")
            if indi.place_of_birth:
                file.write("2 PLAC "+str(indi.place_of_birth)+"\n")
            if indi.date_of_death or indi.place_of_death:
                file.write("1 DEAT\n")
            if indi.date_of_death:
                file.write("2 DATE "+indi.date_of_death+"\n")
            if indi.place_of_death:
                file.write("2 PLAC "+str(indi.place_of_death)+"\n")
            his_marriages=mariage_all.filter(Q(parent1=indi) | Q(parent2=indi))
            his_family=child_all.filter(child=indi)
            for marriage in his_marriages:
                file.write("1 FAMS @F"+str(marriage.id)+"@\n")
            for family in his_family:
                file.write("1 FAMC @F"+str(family.relation.id)+"@\n")
            if indi.image:
                type_image=indi.image.url.split(".")[-1].lower()
                file.write("1 OBJE\n")
                file.write("2 TITL Image\n")
                file.write("2 FORM "+type_image+"\n")
                file.write("2 FILE "+indi.image.url+"\n")
                file.write("2 _PRIM Y\n")
            if indi.place_of_residence:
                file.write("1 RESI\n")
                file.write("2 ADDR "+str(indi.place_of_residence)+"\n")
            if indi.occupation:
                file.write("1 OCCU "+indi.occupation+"\n")
            if indi.comment:
                comment_lines=indi.comment.split("\n")
                has_note=True
                for i in range(0,len(comment_lines)):
                    if i==0:
                        file.write("1 NOTE "+comment_lines[i]+"\n")
                    else:
                        file.write("2 CONT " + comment_lines[i] + "\n")
            if indi.email and is_current_user_admin(request.user):
                if has_note:
                    file.write("2 CONT email: " + indi.email + "\n")
                else:
                    file.write("1 NOTE email: " + indi.email + "\n")
            if indi.birth_source:
                type_image=indi.birth_source.url.split(".")[-1].lower()
                file.write("1 OBJE\n")
                file.write("2 TITL Naissance\n")
                file.write("2 FORM "+type_image+"\n")
                file.write("2 FILE "+indi.birth_source.url+"\n")
            if indi.death_source:
                type_image=indi.death_source.url.split(".")[-1].lower()
                file.write("1 OBJE\n")
                file.write("2 TITL Décès\n")
                file.write("2 FORM "+type_image+"\n")
                file.write("2 FILE "+indi.death_source.url+"\n")
        for marriage in mariage_all:
            file.write("0 @F" + str(marriage.id) + "@ FAM\n")
            if marriage.parent1 is not None :
                if marriage.parent1.private and not is_current_user_admin(request.user):
                    break
                file.write("1 HUSB @I"+str(marriage.parent1.id)+"@\n")
            if marriage.parent2 is not None:
                if marriage.parent2.private and not is_current_user_admin(request.user):
                    break
                file.write("1 WIFE @I"+str(marriage.parent2.id)+"@\n")
            children = child_all.filter(relation=marriage)
            for kid in children:
                if is_current_user_admin(request.user) or not kid.private :
                    file.write("1 CHIL @I"+str(kid.child.id)+"@\n")
            if marriage.date_of_marriage or marriage.place_of_marriage:
                file.write("1 MARR\n")
            if marriage.date_of_marriage:
                file.write("2 DATE "+marriage.date_of_marriage+"\n")
            if  marriage.place_of_marriage:
                file.write("2 PLAC "+str( marriage.place_of_marriage)+"\n")
            if marriage.date_of_divorce:
                file.write("1 DIV\n")
                file.write("2 DATE "+marriage.date_of_divorce+"\n")
            if marriage.marriage_source:
                type_image = marriage.marriage_source.url.split(".")[-1].lower()
                file.write("1 OBJE\n")
                file.write("2 TITL Mariage\n")
                file.write("2 FORM " + type_image + "\n")
                file.write("2 FILE " + marriage.marriage_source.url + "\n")
            if marriage.divorce_source:
                type_image = marriage.divorce_source.url.split(".")[-1].lower()
                file.write("1 OBJE\n")
                file.write("2 TITL Divorce\n")
                file.write("2 FORM " + type_image + "\n")
                file.write("2 FILE " + marriage.divorce_source.url + "\n")
        file.write("0 TRLR\n")
    file.close()
    zip_subdir = "arbre_genealogique"
    zip_filename = "%s.zip" % zip_subdir
    s = io.BytesIO()
    zf = zipfile.ZipFile(s, "w")
    zf.write("gedcom/gedcom_tmp.ged",name_file)
    if add_media:
        images_path="media/uploads/img/"
        sources_path = "media/uploads/src/"
        image_files = [f for f in os.listdir(images_path) ]
        source_files = [f for f in os.listdir(sources_path) ]
        for img in image_files:
            path_img=images_path+img
            zf.write(path_img, path_img)
        for src in source_files:
            path_src=sources_path+src
            zf.write(path_src, path_src)
    zf.close()
    resp = HttpResponse(s.getvalue(), content_type='application/x-zip-compressed')
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    return resp

def export_gedcom_with_media(request):
    return export_gedcom(request, add_media=True)

