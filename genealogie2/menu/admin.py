from django.contrib import admin
from .models import Individual, Relationship, Location, Child, Modification
admin.site.register(Individual)
admin.site.register(Relationship)
admin.site.register(Location)
admin.site.register(Child)
admin.site.register(Modification)
# Register your models here.
