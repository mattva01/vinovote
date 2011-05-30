from django.db import models
from django import forms
import datetime
import CountryForm

NUMCHOICES=[]

for x in range(60,101):
    numtuple = (x,str(x))
    NUMCHOICES.append(numtuple)

class Country(models.Model):
    f_isonum = models.IntegerField(null=True, blank=True)
    f_iso2 = models.CharField(unique=True, max_length=512)
    f_iso3 = models.CharField(unique=True, max_length=512)
    f_name = models.CharField(unique=True, max_length=512)
    active = models.CharField(max_length=1, blank=True)
    created_on = models.CharField(max_length=30)
    modified_on = models.CharField(max_length=30)
    created_by = models.IntegerField(null=True, blank=True)
    modified_by = models.IntegerField(null=True, blank=True)
    def __unicode__(self):
      return self.f_name
    class Meta:
        db_table = u'vinovoter_countries'
class State(models.Model):
    f_country = models.ForeignKey(Country)
    f_usps = models.CharField(unique=True, max_length=512)
    f_name = models.CharField(unique=True, max_length=512)
    active = models.CharField(max_length=1, blank=True)
    created_on = models.CharField(max_length=30)
    modified_on = models.CharField(max_length=30)
    created_by = models.IntegerField(null=True, blank=True)
    modified_by = models.IntegerField(null=True, blank=True)
    def __unicode__(self):
        return self.f_name
    class Meta:
        db_table = u'vinovoter_states'


class WineVariety(models.Model):
   COLOR_CHOICES = (
    ('Red', 'Red'),
    ('White', 'White'),
    #('Rose', 'Rose'),
    #('Blended', 'Blended'),
    )
   color = models.CharField(max_length=20, choices=(COLOR_CHOICES))
   style = models.CharField(max_length=20)
   def __unicode__(self):
       return self.style
class WineBottle(models.Model):
    type        = models.ForeignKey(WineVariety)
    vineyard    = models.CharField(max_length=60)
    country     = models.ForeignKey(Country)
    region      = models.ForeignKey(State,blank=True,null=True)
    year        = models.IntegerField(max_length=4)
    winenum     = models.CharField(max_length=3)
    def __unicode__(self):
        return self.winenum.upper()

class Taster(models.Model):
    name        = models.CharField(max_length=60,unique=True)
    wine_entry  = models.ForeignKey(WineBottle,blank=True,null=True)
    voted       = models.BooleanField(default=False)
    def __unicode__(self):
        return self.name
class Vote(models.Model):
    rating      = models.IntegerField(max_length=2)
    voter       = models.ForeignKey(Taster)
    wine        = models.ForeignKey(WineBottle)
    styleguess  = models.ForeignKey(WineVariety,blank=True,null=True)
    def __unicode__(self):
        return "Vote for %s by %s" % (self.wine.winenum.upper(),self.voter.name)

    class Meta:
        unique_together = ("voter","wine")

class WineForm(forms.Form):
    year        = forms.IntegerField(min_value=1000,max_value=datetime.date.today().year)
    vineyard  = forms.CharField(max_length=60)
class TasterForm(forms.ModelForm):
    class Meta:
        model = Taster
        exclude = ('wine_entry',)

class VoteForm(forms.ModelForm):
    rating = forms.ChoiceField(choices=NUMCHOICES)
    class Meta:
        model =  Vote
        exclude = ('wine','voter')
