from django.shortcuts import render
from django.http import HttpResponse
import random
from django.template import RequestContext, loader
from django.http import JsonResponse

# Create your views here.

#def getting_carriages_from_base():
#    carriages_dict = {'42033':[42,33]}
#    return carriages_dict

carig = {'5555':{'position':('123','258'),'carriages':{'20333':4,'20133':4},'downtime':15,'color':'red','type':'train'},
        '5554':{'position':('350','800'),'carriages':{'20332':4,'20123':4},'downtime':15,'color':'red','type':'train'},
        '5553':{'position':('350','800'),'carriages':{'20312':4,'21123':4},'downtime':15,'color':'red','type':'train'}}
#

def index(request):
    return render(request, r'/Users/denisreshetnykov/Desktop/djangoHokaton/Hokaton/dtek/polls/templates/polls/index.html', {'carig':carig})

def ajax(request):
    data = {}
    data['21'] = 'ajaxtrain'
    return JsonResponse(data)

