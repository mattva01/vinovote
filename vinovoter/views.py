import logging
from django.shortcuts import render_to_response
from django.http import HttpResponse , HttpResponseRedirect
from django.core import serializers
from vinovoter.models import Taster,WineForm, VoteForm, TasterForm,  WineVariety, WineBottle , Vote, Country, State
from django.core.urlresolvers import reverse
import json
from django.forms import ValidationError
from django.db.models import Avg
from operator import itemgetter
def personreg(request):
    if request.method == 'POST':
       firstform = TasterForm(request.POST,prefix="first")
       secondform = TasterForm(request.POST,prefix="second")
       print request.POST
       if firstform.is_valid():
           if request.POST.get('second-name') != u'':
               if secondform.is_valid():
                   print "yay"
                   mainperson=firstform.save()
                   extraperson=secondform.save()
                   return HttpResponseRedirect(reverse('vinovoter.views.winereg',args = [mainperson.id])+'?extra=%s'% extraperson.id)
           else:
               mainperson=firstform.save()
               return HttpResponseRedirect(reverse('vinovoter.views.winereg',args = [mainperson.id]))

       else:
           print "fail >.<"
    firstform = TasterForm(prefix="first")
    secondform = TasterForm(prefix="second")
    return render_to_response('personreg.html', {'firstform': firstform,'secondform':secondform})


def winereg(request,id):
    if request.method == 'POST':
        form = WineForm(request.POST)
        if form.is_valid():
            # This code is a massive hack, I'm sorry
            bottle = WineBottle()
            bottle.year = form.cleaned_data['year']
            bottle.vineyard = form.cleaned_data['vineyard']
            bottle.region = form.cleaned_data['region']
            bottle.type = WineVariety.objects.get(color=request.POST.get("color"),style=request.POST.get("style"))
            bottle_count =0
            for wine_type in WineVariety.objects.filter(color=request.POST.get("color")):
                bottle_count +=wine_type.winebottle_set.count()
            bottle.winenum=request.POST.get("color")[0].lower() + str(bottle_count + 1)
            try:
                bottle.full_clean()
            except ValidationError,e:
                print e
            bottle.save()
            print request.POST.get("extra")
            if request.POST.get("extra"):
                extra_id=request.POST.get("extra")
                extra_owner= Taster.objects.get(id=extra_id)
                extra_owner.wine_entry = bottle
                extra_owner.save()
            wine_owner = Taster.objects.get(id=id)
            wine_owner.wine_entry = bottle
            wine_owner.save()
            return HttpResponseRedirect(reverse('vinovoter.views.wineregcomplete', args=[wine_owner.id,bottle.winenum]))
        else:
            print form.errors

    else:
        form = WineForm() # An unbound form
        if request.GET.get("extra"):
            extraid = request.GET.get("extra")
            return render_to_response('winereg.html', {'form':form,'tasterid':id,'extra':extraid})

    return render_to_response('winereg.html', {
        'form': form,'tasterid':id,
    })


def wineregcomplete(request,id,winenum):
    winenum = winenum.upper()

    return render_to_response('wineregcomplete.html', {'winenum':winenum})
    
def regionjson(request):
   # if the jquery wants the types for a specific color, give it to them
   if request.GET.get("country"):
      data = serializers.serialize("json", State.objects.filter(f_country=request.GET.get("country")))
   # otherwise, give them a  list of countries
   else:
      data= serializers.serialize("json",Country.objects.all())
   return HttpResponse (data)

# This view returns JSON for jquery to` populate the color and style fields of the wine registration form
def winejson(request):
   # if the jquery wants the types for a specific color, give it to them
   if request.GET.get("color"):
      data = serializers.serialize("json", WineVariety.objects.filter(color=request.GET.get("color")))
   # otherwise, give them a  list of colors of wine
   else:
      known_colors= set()
      processed_results = []

      for item in WineVariety.objects.values('color'):
         color = item['color']
         if color in known_colors:
             continue
         else:
             processed_results.append(item)
             known_colors.add(color)

      data = json.dumps(processed_results)
   return HttpResponse(data)
def vote_lookup(request):
    if request.method == "POST":
        form = TasterForm(request.POST)
        name = request.POST.get('name')
        if Taster.objects.filter(name=name).exists():
            taster = Taster.objects.get(name=name)
            return HttpResponseRedirect(reverse('vinovoter.views.vote', args=[taster.id]))
        else:
            HttpResponse("Fail >.<")
    else:
        form = TasterForm()
    return render_to_response('vote_lookup.html', {'form':form})


def vote(request,id):
    winelist = WineBottle.objects.all().order_by('winenum')
    if request.method == "POST":
        votes = [VoteForm(request.POST, prefix=str(x), instance=Vote()) for x in winelist]
        zipped_list=zip(winelist,votes)
        if all([vote[1].is_valid() for vote in zipped_list]):
            for object in zipped_list:
                vote = object[1]
                wine = object[0]
                new_vote = vote.save(commit=False)
                new_vote.voter = Taster.objects.get(pk=id)
                new_vote.wine = wine
                new_vote.save()
            return HttpResponseRedirect('/thanks/')
    else:
        votes = [VoteForm(prefix=str(x), instance=Vote()) for x in winelist]
        zipped_list=zip(winelist,votes)
    return render_to_response('vote.html', {'zipped_list':zipped_list ,})
def results(request):
    winelist=[]
    correctlist=[]
    winecount = WineBottle.objects.all().count()
    for  bottle in WineBottle.objects.all():
        rating=bottle.vote_set.aggregate(Avg('rating'))
        winetup = (bottle.winenum.upper(), rating['rating__avg'])
        winelist.append(winetup)
    for taster in Taster.objects.all():
       numcorrect = 0
       for vote in taster.vote_set.all():
           if vote.styleguess == vote.wine.type:
               print "yay!"
               numcorrect +=1
       correctlist.append((taster.name,numcorrect))
    sorted_wine_list = sorted(winelist,key = itemgetter(1),reverse=True)
    sorted_correct_list = sorted(correctlist,key = itemgetter(1),reverse=True)
    winner=WineBottle.objects.get(winenum=sorted_wine_list[0][0].lower())
    stylewinner=sorted_correct_list[0][0]
    stylewinner_num=sorted_correct_list[0][1]
    return render_to_response('results.html',{'ratinglist':winelist,'winningwine':winner,'winningtaster':stylewinner,'winningtasternum':stylewinner_num,'winecount':winecount})



