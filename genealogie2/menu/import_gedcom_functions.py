from .models import Individual, Relationship


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


def get_individual(id_gedcom):
    try:
        ind = Individual.objects.get(gedcom_id=id_gedcom)
        return ind
    except Individual.DoesNotExist:
        print("Etrange, l'individu n'existe pas dans la base de données",id_gedcom)
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


def import_from_gedcom(request):
    content = request.FILES['fichier'].readline()
    print(content)
    gedcom_id = None
    id_fam = None
    commentaire = ""
    encodage = 'utf-8'
    while content:
        print(content)
        content_part = content.decode(encodage, 'ignore').split(" ")
        if len(content_part) > 2:
            if content_part[2].rstrip() == "INDI":
                if gedcom_id:
                    add_individual(gedcom_id, first_name, last_name, gender, date_of_birth, date_of_death,
                                   place_of_birth, place_of_death,
                                   occupation, commentaire)
                first_name = '?'
                last_name = '?'
                gender = "A"
                date_of_birth = None
                date_of_death = None
                place_of_birth = None
                place_of_death = None
                occupation = None
                path_image = None
                commentaire = ""
                gedcom_id = content_part[1]
            elif content_part[2].rstrip() == "FAM":
                if gedcom_id:
                    add_individual(gedcom_id, first_name, last_name, gender, date_of_birth, date_of_death,
                                   place_of_birth, place_of_death,
                                   occupation, commentaire)
                if id_fam:
                    add_relation(id_fam, husband_id, wife_id, date_marriage, place_marriage, date_divorce, status)
                husband_id = None
                gedcom_id = None
                wife_id = None
                date_marriage = None
                place_marriage = None
                date_divorce = None
                status = "concubinage"
                id_fam = content_part[1]
            elif content_part[1] == "GIVN":
                first_name = ' '.join(content_part[2:]).rstrip()
            elif content_part[1] == "SURN":
                last_name = ' '.join(content_part[2:]).rstrip()
            elif content_part[1] == "SEX":
                if content_part[2].rstrip() == "M":
                    gender = "M"
                else:
                    gender = "F"
            elif content_part[1] == "OCCU":
                occupation = ' '.join(content_part[2:]).rstrip()
            elif content_part[1] == "NOTE":
                commentaire = commentaire + " ".join(content_part[2:]).rstrip()
            elif content_part[1] == "FILE":
                path_image = content_part[2].rstrip()
            elif content_part[1] == "HUSB":
                husband_id = get_individual(content_part[2].rstrip())
            elif content_part[1] == "WIFE":
                wife_id = get_individual(content_part[2].rstrip())
            elif content_part[1] == "CHIL":
                child_id = get_individual(content_part[2].rstrip())
            content = request.FILES['fichier'].readline()
        elif len(content_part) == 2:
            type = content_part[1].rstrip()
            if type == "BIRT" or type == "DEAT" or type == "MARR" or type == "DIV":
                print("in birt")
                year = None
                month = None
                day = None
                ville = None
                pays = None
                paroisse = None
                departement = None
                content = request.FILES['fichier'].readline()
                while content and content.decode(encodage, 'ignore').split(" ")[0] == '2':
                    content_part = content.decode(encodage, 'ignore').split(" ")
                    if len(content_part) > 2:
                        if content_part[1] == "DATE":
                            if type == "BIRT":
                                date_of_birth = " ".join(content_part[2:]).rstrip()
                            elif type == "DEAT":
                                date_of_death = " ".join(content_part[2:]).rstrip()
                            elif type == "MARR":
                                date_marriage = " ".join(content_part[2:]).rstrip()
                                status = "mariage ou Pacs"
                            elif type == "DIV":
                                date_divorce = " ".join(content_part[2:]).rstrip()
                    content = request.FILES['fichier'].readline()
            else:
                content = request.FILES['fichier'].readline()
        else:
            content = request.FILES['fichier'].readline()
        if id_fam:
            add_relation(id_fam, husband_id, wife_id, date_marriage, place_marriage, date_divorce, status)
    return 0