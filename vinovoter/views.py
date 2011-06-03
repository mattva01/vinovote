import logging
from django.shortcuts import render_to_response
from django.http import HttpResponse , HttpResponseRedirect
from django.core import serializers
from vinovoter.models import Taster,WineForm, RedVoteForm,WhiteVoteForm, TasterForm,  WineVariety, WineBottle , Vote, Country, State
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
            bottle.country = Country.objects.get(id=request.POST.get("country"))
            if request.POST.get("state") == u"":
                pass
            else:
                bottle.region = State.objects.get(id=request.POST.get("state"))
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
        if Taster.objects.filter(name__iexact=name).exists():
            taster = Taster.objects.get(name__iexact=name)
            return HttpResponseRedirect(reverse('vinovoter.views.vote', args=[taster.id]))
        else:
            HttpResponse("Fail >.<")
    else:
        form = TasterForm()
    return render_to_response('vote_lookup.html', {'form':form})


def vote(request,id):
    errors = False
    if Taster.objects.get(id=id).voted:
        return HttpResponseRedirect("/error/dupvote/")
    winelist = WineBottle.objects.all().order_by('winenum')
    redwinelist = WineBottle.objects.filter(type__color="Red").order_by('winenum')
    whitewinelist = WineBottle.objects.filter(type__color="White").order_by('winenum')
    if request.method == "POST":
        errors = False
        print request.POST
        #votes = [VoteForm(request.POST, prefix=str(x), instance=Vote()) for x in winelist]
        redvotes = [RedVoteForm(request.POST, prefix=str(x), instance=Vote()) for x in redwinelist]
        whitevotes = [WhiteVoteForm(request.POST, prefix=str(x), instance=Vote()) for x in whitewinelist]
        #zipped_list=zip(winelist,votes)
        redzipped_list=zip(redwinelist,redvotes)
        whitezipped_list=zip(whitewinelist,whitevotes)
        for object in redzipped_list:
            vote = object[1]
            wine = object[0]
            if request.POST.get("%s-rating"% wine) != u"":
               if vote.is_valid():
                   new_vote = vote.save(commit=False)
                   new_vote.voter = Taster.objects.get(pk=id)
                   new_vote.wine = wine
                   new_vote.save()
               else:
                   print vote.errors
                   errors = True
        for object in whitezipped_list:
            vote = object[1]
            wine = object[0]
            if request.POST.get("%s-rating"% wine) != u"":
               if vote.is_valid():
                   new_vote = vote.save(commit=False)
                   new_vote.voter = Taster.objects.get(pk=id)
                   new_vote.wine = wine
                   new_vote.save()
               else:
                   print vote.errors
                   errors = True
        if not errors:
            current_taster=Taster.objects.get(id=id)
            current_taster.voted = True
            current_taster.save()
            return HttpResponseRedirect('/thanks/')
    else:
        redvotes = [RedVoteForm(prefix=str(x), instance=Vote()) for x in redwinelist]
        whitevotes = [WhiteVoteForm(prefix=str(x), instance=Vote()) for x in whitewinelist]
        redzipped_list=zip(redwinelist,redvotes)
        whitezipped_list=zip(whitewinelist,whitevotes)
    return render_to_response('vote.html', {'white_list':whitezipped_list,'red_list':redzipped_list})
def results(request):
    winelist=[]
    redwinelist=[]
    whitewinelist=[]
    correctlist=[]
    redwinecount = WineBottle.objects.filter(type__color="Red").count()
    whitewinecount = WineBottle.objects.filter(type__color="White").count()
    winecount = WineBottle.objects.all().count()
    for  bottle in WineBottle.objects.filter(type__color="Red"):
        rating=bottle.vote_set.aggregate(Avg('rating'))
        winetup = (bottle, rating['rating__avg'])
        redwinelist.append(winetup)
    for  bottle in WineBottle.objects.filter(type__color="White"):
        rating=bottle.vote_set.aggregate(Avg('rating'))
        winetup = (bottle, rating['rating__avg'])
        whitewinelist.append(winetup)

    for taster in Taster.objects.all():
       rednumcorrect = 0
       whitenumcorrect = 0
       for vote in taster.vote_set.all():
           if vote.styleguess == vote.wine.type:
               if vote.wine.type.color == "Red":    
                   rednumcorrect += 1
               else:
                   whitenumcorrect += 1 
       correctlist.append((taster.name,rednumcorrect,whitenumcorrect))
    redsorted_wine_list = sorted(redwinelist,key = itemgetter(1),reverse=True)
    whitesorted_wine_list = sorted(whitewinelist,key = itemgetter(1),reverse=True)
    redsorted_correct_list = sorted(correctlist,key = itemgetter(1),reverse=True)
    whitesorted_correct_list = sorted(correctlist,key = itemgetter(2),reverse=True)
    redwinner=redsorted_wine_list[0][0]
    whitewinner=whitesorted_wine_list[0][0]
    redstylewinner=redsorted_correct_list[0][0]
    whitestylewinner=whitesorted_correct_list[0][0]
    redstylewinner_num=redsorted_correct_list[0][1]
    whitestylewinner_num=whitesorted_correct_list[0][2]
    return render_to_response('results.html',{'allreds':redsorted_wine_list,"allwhites":whitesorted_wine_list,'redtop3':redsorted_wine_list[0:3],'whitetop3':whitesorted_wine_list[0:3],'ratinglist':winelist,'redwinningwine':redwinner,'whitewinningwine':whitewinner,'redstyletop3':redsorted_correct_list[0:3],'whitestyleall':whitesorted_correct_list,'redstyleall':redsorted_correct_list,'whitestyletop3':whitesorted_correct_list[0:3],'redwinningtaster':redstylewinner,'redwinningtasternum':redstylewinner_num,'whitewinningtaster':whitestylewinner,'whitewinningtasternum':whitestylewinner_num,'redwinecount':redwinecount,'whitewinecount':whitewinecount})



