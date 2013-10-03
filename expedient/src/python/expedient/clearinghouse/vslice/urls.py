'''
Created on Jul 23, 2013

@author: atty
'''
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('expedient.clearinghouse.vslice.views',
    url(r'^getRes/(?P<vslice_id>\d+)/$', 'getRes', name='getRes'),
    url(r'^freeRes/(?P<vslice_id>\d+)/$', 'freeRes', name='freeRes'),
    url(r'^checkAv/(?P<vslice_id>\d+)/$', 'checkAv', name='checkAv'),
    url(r'^contact/(?P<vslice_id>\d+)/$', 'contact', name='contact'),
    url(r'^detail/(?P<vslice_id>\d+)/$', 'detail', name='vslice_detail'),
    url(r'^create/(?P<proj_id>\d+)/$', 'create', name='vslice_create'),
    url(r'^update/(?P<vslice_id>\d+)/$', 'update', name='vslice_update'),
    url(r'^delete/(?P<vslice_id>\d+)/$', 'delete', name="vslice_delete"),
    url(r'^start/(?P<vslice_id>\d+)/$', 'start', name="vslice_start"),
    url(r'^stop/(?P<vslice_id>\d+)/$', 'stop', name="vslice_stop"),
    url(r'^aggregates/add/(?P<vslice_id>\d+)/$', 'add_aggregate', name="vslice_add_agg"),
    url(r'^aggregates/add_aggregate_vtam/(?P<vslice_id>\d+)/(?P<vtam_id>\d+)/$', 'add_aggregate_vtam', name="add_aggregate_vtam"),
    url(r'^aggregates/update/(?P<vslice_id>\d+)/(?P<agg_id>\d+)/$', 'update_aggregate', name="vslice_update_agg"),
    url(r'^aggregates/remove/(?P<vslice_id>\d+)/(?P<agg_id>\d+)/$', 'remove_aggregate', name="vslice_remove_agg"),
    url(r'^resources/(?P<vslice_id>\d+)/$', 'select_ui_plugin', name="vslice_manage_resources"),    
)

