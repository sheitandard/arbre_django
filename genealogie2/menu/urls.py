"""genealogie2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
#from django.urls import path
from django.conf.urls import url, include
from django.views.generic import ListView, DetailView
from menu.models import Individual
from . import views
from django.conf import settings
from django.conf.urls.static import static


#query=Individual.objects.exclude(last_name='?').exclude(first_name='?').order_by('last_name')

#print(query).order_by(last_name)

urlpatterns = [
	url('contact/', views.contact, name='contact'),
	url('import_gedcom/', views.import_gedcom, name='import_gedcom'),
	url('list_modification/',views.ModificationListView.as_view(), name='Liste des modifications'),
	url('list_places/$',views.PlaceListView.as_view(), name='Liste des lieux'),
    url('^individu/(?P<pk>\d+)$', views.IndividualDetailView.as_view(), name='Information') ,
    url('^individu/(?P<id>\d+)/update/$', views.update_individu, name = 'update_individu'),
	url('^individu/(?P<id>\d+)/update_parents/$', views.update_parents, name = 'update_parents'),
    url('^individu/(?P<id>\d+)/remove_parents/(?P<id2>\d+)$', views.remove_parents, name='remove_parents'),
	url('^individu/(?P<id>\d+)/add_parents/$', views.add_parents, name='add_parents'),
	url('^individu/(?P<pk>\d+)/delete/$', views.IndividuDelete.as_view(), name='delete_individu'),
	url('^lieu/(?P<pk>\d+)$', views.PlaceDetailView.as_view(), name='detail_lieu') ,
	url('^lieu/(?P<id>\d+)/update/$', views.update_place, name='update_lieu'),
	url('.*/add_location', views.add_location_html, name='add_location'),
	url('.*place_list',views.place_list, name="place_list"),
	url('^$',views.IndividualListView.as_view(), name='Liste des individus'),


	#url('individu/<int:pk>', views.individual_detail_view(), name='Information'),

]


