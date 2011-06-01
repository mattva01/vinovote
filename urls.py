from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.views.generic.simple import direct_to_template
from django.views.generic.list_detail import object_list
from django.views.generic.list_detail import object_detail
from vinovoter.models import WineBottle
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'vinovote.views.home', name='home'),
    # url(r'^vinovote/', include('vinovote.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
   url(r'^admin/', include(admin.site.urls)),
   url(r'^vote/$','vinovoter.views.vote_lookup'),
   url(r'^taster/register/$','vinovoter.views.personreg'),
   url(r'^taster/(?P<id>\d+)/winereg/$','vinovoter.views.winereg'),
   url(r'^taster/(?P<id>\d+)/winereg/(?P<winenum>\w+)/$','vinovoter.views.wineregcomplete'),
   url(r'^taster/(?P<id>\d+)/vote/$','vinovoter.views.vote'),
   #url(r'^taster/\d+/winereg/$','vinovoter.views.winereg'),
   url(r'^json/wineinfo/','vinovoter.views.winejson'),
   url(r'^json/regioninfo/','vinovoter.views.regionjson'),
   url(r'^$',direct_to_template, {'template': 'index.html'}),
   url(r'^thanks/$',direct_to_template, {'template': 'thanks.html'}),
   url(r'^error/dupvote/$',direct_to_template, {'template': 'dupvote.html'}),
   url(r'^results/$','vinovoter.views.results' ),
   url(r'^results/all/$',object_list,{'queryset':WineBottle.objects.all().order_by('winenum'),'template_name':'winebottle_list.html'} ),
   url(r'^results/(?P<object_id>\d+)/$',object_detail,{'queryset': WineBottle.objects.all(),'template_name':'winebottle_object.html'} ),
)
