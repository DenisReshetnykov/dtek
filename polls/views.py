from django.shortcuts import render
from django.http import HttpResponse
import random
from django.template import RequestContext, loader
# Create your views here.

#def getting_carriages_from_base():
#    carriages_dict = {'42033':[42,33]}
#    return carriages_dict

carig = [{'coords':['180','350'],
         'train_index':'45510+0+91900',
         'color':'green',
         'train_condition': True,
         'cariage_number':'61179032',
         'count_of_carriages':'33',
         'all_points':['ДРУЖКОВКА','БОГУСЛАВСКИЙ','ДРУЖКОВКА','БОГУСЛАВСКИЙ'],
         'listofcarriages':[['5355',False],['222',True],['33232',False]],
         'priznak': True,
         'OTPRred': False,
         'middletimeof_AFK':'15',
         'type':'train'
         },{'coords':['180','350'],
            'stationname':'Drushkuva',
            'listofcarriagesonstation':[['555',True,'Киев-Одесса'],['333',False,'Запорожье-Николаев'],['3434',False,'Львов-Черкасы']],
            'countofcarriageAFK':'5',
            'type':'station'}]

def index(request):
    return render(request, '/Users/denisreshetnykov/Desktop/djangoHokaton/Hokaton/polls/templates/polls/index.html', {'carig':carig})
