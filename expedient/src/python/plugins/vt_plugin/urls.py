from django.conf.urls.defaults import *
from expedient.common.rpc4django.utils import rpc_url
from expedient.common.rpc4django import rpcmethod

urlpatterns = patterns('vt_plugin.controller.vtAggregateController.vtAggregateController',
    url(r'^aggregate/create/$', 'aggregate_crud', name='vt_plugin_aggregate_create'),
    url(r'^aggregate/(?P<agg_id>\d+)/edit/$', 'aggregate_crud', name='vt_plugin_aggregate_edit'),
)


urlpatterns = urlpatterns + patterns('vt_plugin.controller.dispatchers.GUIdispatcher',
    url(r'^goto_create_vm/(?P<slice_id>\d+)/(?P<agg_id>\d+)/$', 'goto_create_vm', name='goto_create_vm'),
    url(r'^manage_vm/(?P<slice_id>\d+)/(?P<vm_id>\d+)/(?P<action_type>\w+)/$', 'manage_vm', name='manage_vm'),
    url(r'^manage_vm_vslice/(?P<vslice_id>\d+)/(?P<vm_name>[-\w]+)/(?P<action_type>\w+)/$', 'manage_vm_vslice', name='manage_vm_vslice'),
    url(r'^virtualmachine_crud/(?P<slice_id>\d+)/(?P<server_id>\d+)/$', 'virtualmachine_crud', name='virtualmachine_crud'),
    url(r'^virtualmachine_crud_vslice/(?P<vslice_id>\d+)/(?P<server_id>\d+)/$', 'virtualmachine_crud_vslice', name='virtualmachine_crud_vslice'),
    url(r'^vms_status/(?P<slice_id>\d+)/$', 'check_vms_status', name='check_vms_status'),
    url(r'^vms_status_vslice/(?P<vslice_id>\d+)/$', 'check_vms_status_vslice', name='check_vms_status_vslice'),
    url(r'^update_messages/$', 'update_messages', name='update_messages'),
)




urlpatterns = urlpatterns + patterns('',
     rpc_url(r'^xmlrpc/vt_am/$', name='vt_am'),
)
