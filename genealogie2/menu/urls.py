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
    #url( '', views.index, name='index'),
    #url('', ListView.as_view( queryset=query,template_name="menu/home.html")),
    url('^individu/(?P<pk>\d+)$', views.IndividualDetailView.as_view(), name='Information') ,
	url('^$',views.IndividualListView.as_view(), name='Liste des individus'),
	
	#url('individu/<int:pk>', views.individual_detail_view(), name='Information'),

] 


