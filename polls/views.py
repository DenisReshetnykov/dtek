from django.shortcuts import render
from django.http import HttpResponse
import random
from django.template import RequestContext, loader
from django.http import JsonResponse
from DTEK import get_train_FEdata
# Create your views here.



carig = {'5555':{'position':('123','258'),
                 'carriages':{'20333':4,
                              '20133':4},
                 'downtime':15,
                 'color':'red',
                 'type':'train'}}
get_train_FEdata()

def index(request):
    return render(request, r'/Users/denisreshetnykov/Desktop/djangoHokaton/Hokaton/dtek/polls/templates/polls/index.html', {'carig':carig})

def ajax(request):
    data = {}
    data['21'] = 'ajaxtrain'
    return JsonResponse(data)

