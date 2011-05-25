from django.db import models
from django import forms
import datetime
import CountryForm
class WineVariety(models.Model):
   COLOR_CHOICES = (
    ('Red', 'Red'),
    ('White', 'White'),
    ('Rose', 'Rose'),
    ('Blended', 'Blended'),
    )
   color = models.CharField(max_length=20, choices=(COLOR_CHOICES))
   style = models.CharField(max_length=20)
   def __unicode__(self):
       return self.style
class WineBottle(models.Model):
    type        = models.ForeignKey(WineVariety)
    vineyard    = models.CharField(max_length=60)
    region      = models.CharField(max_length=60)
    year        = models.IntegerField(max_length=4)
    winenum     = models.CharField(max_length=3)
    def __unicode__(self):
        return self.winenum.upper()
class Taster(models.Model):
    name        = models.CharField(max_length=60,unique=True)
    wine_entry  = models.ForeignKey(WineBottle,blank=True,null=True)
    def __unicode__(self):
        return self.name
class Vote(models.Model):
    rating      = models.IntegerField(max_length=2)
    voter       = models.ForeignKey(Taster)
    wine        = models.ForeignKey(WineBottle)
    styleguess  = models.ForeignKey(WineVariety)
    def __unicode__(self):
        return "Vote for %s by %s" % (self.wine.winenum.upper(),self.voter.name)


class WineForm(forms.Form):
    year        = forms.IntegerField(min_value=1000,max_value=datetime.date.today().year)
    vineyard  = forms.CharField(max_length=60)
    region = CountryForm.CountryField()
class TasterForm(forms.ModelForm):
    class Meta:
        model = Taster
        exclude = ('wine_entry',)

class VoteForm(forms.ModelForm):
    class Meta:
        model =  Vote
        exclude = ('wine','voter')
