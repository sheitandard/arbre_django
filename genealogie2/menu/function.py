
from .models import Location, Individual, Relationship, Child, month_list, Modification


def update_child(request):
    all_child=Child.objects.all()
    for child in all_child:
        try:
            relation=Relationship.objects.get(parent1=child.parent1, parent2=child.parent2)
            #print(relation.id)
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