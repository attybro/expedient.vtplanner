'''
Created on Jul 23, 2013

@author: atty
'''
from django.views.generic import list_detail, simple
from django.core.urlresolvers import reverse, get_callable
from django.core.exceptions import MultipleObjectsReturned
from django.shortcuts import get_object_or_404, render_to_response
from django.http import Http404, HttpResponseRedirect, HttpResponseNotAllowed,\
    HttpResponse
from expedient.common.utils.views import generic_crud
from expedient.common.messaging.models import DatedMessage
from expedient.clearinghouse.project.models import Project
from expedient.clearinghouse.aggregate.models import Aggregate
from models import Vslice
from forms import VsliceCrudForm
from forms import ContactForm
#from django.views.generic.edit import FormView
from django.conf import settings
import logging
from expedient.common.permissions.shortcuts import must_have_permission, give_permission_to
logger = logging.getLogger("VsliceViews")
import uuid
from expedient.clearinghouse.vslice.utils import parseFVexception
from expedient.clearinghouse.urls import PLUGIN_LOADER, TOPOLOGY_GENERATOR
import xmlrpclib
import sys #it can be removed
import os.path
from datetime import datetime
from dateutil import parser as dateparser
import xml.etree.ElementTree as ET
import json
from vtplanner.models.VtPlannerAggregate import VtPlannerAggregate as VtPlannerAggregateModel
from django.db import models


cred=[{'geni_value': '<?xml version="1.0"?>\n<signed-credential xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://www.planet-lab.org/resources/sfa/credential.xsd" xsi:schemaLocation="http://www.planet-lab.org/resources/sfa/ext/policy/1 http://www.planet-lab.org/resources/sfa/ext/policy/1/policy.xsd"><credential xml:id="ref0"><type>privilege</type><serial>8</serial><owner_gid>-----BEGIN CERTIFICATE-----\nMIICNDCCAZ2gAwIBAgIBAzANBgkqhkiG9w0BAQQFADAmMSQwIgYDVQQDExtnZW5p\nLy9ncG8vL2djZi5hdXRob3JpdHkuc2EwHhcNMTMwNjE4MDc1NDQ1WhcNMTgwNjE3\nMDc1NDQ1WjAkMSIwIAYDVQQDExlnZW5pLy9ncG8vL2djZi51c2VyLmFsaWNlMIGf\nMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCmS8GZ6qy4TKh7CTSKvMIAlLqCG0uG\nbZEqfLZdSqhe21c+mxQ+V3dgmCSwi6noWg2pJkkcFn1YKvIy9XUZ3IwNfE9QIVlK\n0Eh453+jqOAc9jc6KrXpPMTkicmGVpAac4X/Ao6fuZMHZ81tjVgeJ8xxYpU6Qjz0\npKjTr8D9lCR2IQIDAQABo3QwcjAMBgNVHRMBAf8EAjAAMGIGA1UdEQRbMFmGKHVy\nbjpwdWJsaWNpZDpJRE4rZ2VuaTpncG86Z2NmK3VzZXIrYWxpY2WGLXVybjp1dWlk\nOjViYzNiZWY3LTM4NDktNDEzMS1iNDczLTU2MzNiMzA1MzQ3MTANBgkqhkiG9w0B\nAQQFAAOBgQBkMVA+I6oEpU4afFY0xE3cwi93Cyt6dt/p8B2zZ9dzs5vAXx6PaGMb\n5k5+LjtoUGQ/XMOPdX0TuPhhJLOV9mYP5Xm+4dr8RYTGO3bVdnh60XHWBqZtsdOj\nIOvLkSVYqouUyyEeEPNm4dukk4BHGzisTqwrglkcYQtDWPmglxKs+A==\n-----END CERTIFICATE-----\n</owner_gid><owner_urn>urn:publicid:IDN+geni:gpo:gcf+user+alice</owner_urn><target_gid>-----BEGIN CERTIFICATE-----\nMIICNjCCAZ+gAwIBAgIBAzANBgkqhkiG9w0BAQQFADAmMSQwIgYDVQQDExtnZW5p\nLy9ncG8vL2djZi5hdXRob3JpdHkuc2EwHhcNMTMwODA3MTI0MzUwWhcNMTgwODA2\nMTI0MzUwWjAlMSMwIQYDVQQDExpnZW5pLy9ncG8vL2djZi5zbGljZS5QVVBQQTCB\nnzANBgkqhkiG9w0BAQEFAAOBjQAwgYkCgYEAz74QBE2TSKPNa5PxCOUPw4ZuhLXR\nsxwEb47ZEx11WsH0qWfOP7MuYMfHOfOnG9wmLZzA8KkH68tqq0QmxCW/EzOvvYAs\nN5iY6Lu6UPXtbqed/gWbbEx8dLGZPLkwpmqEltlbBW1fitj/lqQkrdnc63AOlzNR\nZ8SC/II6RhAOGpkCAwEAAaN1MHMwDAYDVR0TAQH/BAIwADBjBgNVHREEXDBahil1\ncm46cHVibGljaWQ6SUROK2dlbmk6Z3BvOmdjZitzbGljZStQVVBQQYYtdXJuOnV1\naWQ6OTNjNzhjMmUtNGZkZC00OWZmLWFkODMtN2MzNTk3ZWI3ODFkMA0GCSqGSIb3\nDQEBBAUAA4GBAMCbP/9YMEvanpjSatmDJzcg0gcRDNFo7UpKNWVBVTPCY22V5Him\nKr/lpZKmKLaUTkhJW7Vqbgs8DyWYlja1oXoO7Y9CSg6AQXeaClrfoSYZf4st4ctg\nG2nebqIo3M+RpO2ZdWN8NX4b3FGpuREyQaBey8nFfCEFBBbRli8OWsPq\n-----END CERTIFICATE-----\n-----BEGIN CERTIFICATE-----\nMIICOzCCAaSgAwIBAgIBAzANBgkqhkiG9w0BAQQFADAmMSQwIgYDVQQDExtnZW5p\nLy9ncG8vL2djZi5hdXRob3JpdHkuc2EwHhcNMTMwNjE4MDc1NDQ0WhcNMTgwNjE3\nMDc1NDQ0WjAmMSQwIgYDVQQDExtnZW5pLy9ncG8vL2djZi5hdXRob3JpdHkuc2Ew\ngZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBAN2D/6XFhkK6NwYg0nF60AU380ej\n35LmzVYJuJDyh0qlusvSaJkuv3LLHtzZ/sG6ZyitwqPyiHwPL9KgsfBvqYs/5hsi\n7qzV8M6YbcOwpNAWiSqbtmnEkzbkvzG+dwWwsS37dC6rp5cj9v7k5bj+FwdgIWNy\nhN5JhC1ROJg5w89ZAgMBAAGjeTB3MA8GA1UdEwEB/wQFMAMBAf8wZAYDVR0RBF0w\nW4YqdXJuOnB1YmxpY2lkOklETitnZW5pOmdwbzpnY2YrYXV0aG9yaXR5K3Nhhi11\ncm46dXVpZDpkMDc2MWQ1OS0zNzA2LTQxMWItOTRkMy02YTUxZjZiZGI5ODUwDQYJ\nKoZIhvcNAQEEBQADgYEALQqBOipQncjxdCrsc/WZzjgjgs1htCOCi0BiwJfXE/44\naW6P/a93zpzgOkD6YXkaFLjjTJ/RZ+mVM+MIH3R4xw+8lUXMKfsj549WKa4H90N7\nQTKOBN7oVhHQOfd9E2llVzt326OtbXapnReASuKVNvzM3Dlxe4IkD1n9H91s1+M=\n-----END CERTIFICATE-----\n</target_gid><target_urn>urn:publicid:IDN+geni:gpo:gcf+slice+PUPPA</target_urn><uuid/><expires>2013-08-07T14:43:50</expires><privileges><privilege><name>refresh</name><can_delegate>true</can_delegate></privilege><privilege><name>embed</name><can_delegate>true</can_delegate></privilege><privilege><name>bind</name><can_delegate>true</can_delegate></privilege><privilege><name>control</name><can_delegate>true</can_delegate></privilege><privilege><name>info</name><can_delegate>true</can_delegate></privilege></privileges></credential><signatures><Signature xmlns="http://www.w3.org/2000/09/xmldsig#" xml:id="Sig_ref0">\n  <SignedInfo>\n    <CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"/>\n    <SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"/>\n    <Reference URI="#ref0">\n      <Transforms>\n        <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>\n      </Transforms>\n      <DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>\n      <DigestValue>5ZW7cQZNvZCU+Ki8TZWXk3U8p4Q=</DigestValue>\n    </Reference>\n  </SignedInfo>\n  <SignatureValue>qJvRhl/3qY2pf7ubDgXHlWA3mKC6DdxYEIYFZD373nHaVcbIzqdMgK8oNWAPPjrd\nR7jjk0ZbasK1/TXmXvZLjWe1d0xzw6tTImNry8NRd/cPW5OjnLDtFXzVgWh8dSaG\nKpbteedQ791kwQXLLSAq5jJpXwSf9EMkXJatQZ71mGI=</SignatureValue>\n  <KeyInfo>\n    <X509Data>\n      \n      \n      \n    <X509Certificate>MIICOzCCAaSgAwIBAgIBAzANBgkqhkiG9w0BAQQFADAmMSQwIgYDVQQDExtnZW5p\nLy9ncG8vL2djZi5hdXRob3JpdHkuc2EwHhcNMTMwNjE4MDc1NDQ0WhcNMTgwNjE3\nMDc1NDQ0WjAmMSQwIgYDVQQDExtnZW5pLy9ncG8vL2djZi5hdXRob3JpdHkuc2Ew\ngZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBAN2D/6XFhkK6NwYg0nF60AU380ej\n35LmzVYJuJDyh0qlusvSaJkuv3LLHtzZ/sG6ZyitwqPyiHwPL9KgsfBvqYs/5hsi\n7qzV8M6YbcOwpNAWiSqbtmnEkzbkvzG+dwWwsS37dC6rp5cj9v7k5bj+FwdgIWNy\nhN5JhC1ROJg5w89ZAgMBAAGjeTB3MA8GA1UdEwEB/wQFMAMBAf8wZAYDVR0RBF0w\nW4YqdXJuOnB1YmxpY2lkOklETitnZW5pOmdwbzpnY2YrYXV0aG9yaXR5K3Nhhi11\ncm46dXVpZDpkMDc2MWQ1OS0zNzA2LTQxMWItOTRkMy02YTUxZjZiZGI5ODUwDQYJ\nKoZIhvcNAQEEBQADgYEALQqBOipQncjxdCrsc/WZzjgjgs1htCOCi0BiwJfXE/44\naW6P/a93zpzgOkD6YXkaFLjjTJ/RZ+mVM+MIH3R4xw+8lUXMKfsj549WKa4H90N7\nQTKOBN7oVhHQOfd9E2llVzt326OtbXapnReASuKVNvzM3Dlxe4IkD1n9H91s1+M=</X509Certificate>\n<X509SubjectName>CN=geni//gpo//gcf.authority.sa</X509SubjectName>\n<X509IssuerSerial>\n<X509IssuerName>CN=geni//gpo//gcf.authority.sa</X509IssuerName>\n<X509SerialNumber>3</X509SerialNumber>\n</X509IssuerSerial>\n</X509Data>\n    <KeyValue>\n<RSAKeyValue>\n<Modulus>\n3YP/pcWGQro3BiDScXrQBTfzR6PfkubNVgm4kPKHSqW6y9JomS6/csse3Nn+wbpn\nKK3Co/KIfA8v0qCx8G+piz/mGyLurNXwzphtw7Ck0BaJKpu2acSTNuS/Mb53BbCx\nLft0LqunlyP2/uTluP4XB2AhY3KE3kmELVE4mDnDz1k=\n</Modulus>\n<Exponent>\nAQAB\n</Exponent>\n</RSAKeyValue>\n</KeyValue>\n  </KeyInfo>\n</Signature></signatures></signed-credential>\n', 'geni_version': '3', 'geni_type': 'geni_sfa'}]


class SafeTransportWithCert(xmlrpclib.SafeTransport): 
    """Helper class to foist the right certificate for the transport class."""
    def __init__(self, key_path, cert_path):
        xmlrpclib.SafeTransport.__init__(self) # no super, because old style class
        self._key_path = key_path
        self._cert_path = cert_path
        
    def make_connection(self, host):
        """This method will automatically be called by the ServerProxy class when a transport channel is needed."""
        host_with_cert = (host, {'key_file' : self._key_path, 'cert_file' : self._cert_path})
        return xmlrpclib.SafeTransport.make_connection(self, host_with_cert) # no super, because old style class

class GENI3ClientError(Exception):
    def __init__(self, message, code):
        self._message = message
        self._code = code

    def __str__(self):
        return "%s (code: %s)" % (self._message, self._code)

class GENI3Client(object):
    """This class encapsulates a connection to a GENI AM API v3 server.
    It implements all methods of the API and manages the interaction regarding the client certificate.
    For all the client methods (e.g. listResources, describe) the given options (e.g. compress) have the default value None.
    This means if the caller does not change the value the client will not send this option and hence force the server to use the default.
    If true or false are given the options are set accordingly.
    If a time is given (e.g. end_time), please provide the method call with a Python datetime object, the RPC-conversion will then be done for you.
    
    Please also see the helper methods below.
    """
    
    RFC3339_FORMAT_STRING = '%Y-%m-%d %H:%M:%S.%fZ'
    
    def __init__(self, host, port, key_path, cert_path):
        """
        Establishes a connection proxy with the client certificate given.
        {host} e.g. 127.0.0.1
        {port} e.g. 8001
        {key_path} The file path to the client's private key.
        {cert_path} The file path to the client's certificate.
        """
        transport = SafeTransportWithCert(key_path, cert_path)
        self._proxy = xmlrpclib.ServerProxy("https://%s:%s/RPC2" % (host, str(port)), transport=transport)
    
    def getVersion(self):
        """Calls the GENI GetVersion method and returns a dict. See [geniv3rpc] GENIv3DelegateBase for more information."""
        return self._proxy.GetVersion()
        

    def listResources(self, credentials, available=None, compress=None):
        """See class description above and the [geniv3rpc] GENIv3DelegateBase for more information."""
        options = self._default_options()
        if available != None:
            options["geni_available"] = available
        if compress != None:
            options["geni_compress"] = compress
        return self._proxy.ListResources(credentials, options)
    
    def describe(self, urns, credentials, compress=None):
        """See class description above and the [geniv3rpc] GENIv3DelegateBase for more information."""
        options = self._default_options()
        if compress != None:
            options["geni_compress"] = compress
        return self._proxy.ListResources(credentials, options)
            
    def allocate(self, slice_urn, credentials, rspec, end_time=None):
        """See class description above and the [geniv3rpc] GENIv3DelegateBase for more information."""
        options = self._default_options()
        if end_time != None:
            options["geni_end_time"] = self.datetime2str(end_time)
        return self._proxy.Allocate(slice_urn, credentials, rspec, options)
    
    def renew(self, urns, credentials, expiration_time, best_effort=None):
        """See class description above and the [geniv3rpc] GENIv3DelegateBase for more information."""
        options = self._default_options()
        if best_effort != None:
            options["geni_best_effort"] = best_effort
        return self._proxy.Renew(urns, credentials, self.datetime2str(expiration_time), options)
        
    def provision(self, urns, credentials, best_effort=None, end_time=None, users=None):
        """See class description above and the [geniv3rpc] GENIv3DelegateBase for more information."""
        options = self._default_options()
        if best_effort != None:
            options["geni_best_effort"] = best_effort
        if end_time != None:
            options["geni_end_time"] = self.datetime2str(end_time)
        if users != None:
            options["geni_users"] = users
        return self._proxy.Provision(urns, credentials, options)

    def status(self, urns, credentials):
        """See class description above and the [geniv3rpc] GENIv3DelegateBase for more information."""
        options = self._default_options()
        return self._proxy.Status(urns, credentials, options)
        
    def performOperationalAction(self, urns, credentials, action, best_effort=None):
        """See class description above and the [geniv3rpc] GENIv3DelegateBase for more information."""
        options = self._default_options()
        if best_effort != None:
            options["geni_best_effort"] = best_effort
        return self._proxy.PerformOperationalAction(urns, credentials, action, options)
        
    def delete(self, urns, credentials, best_effort=None):
        """See class description above and the [geniv3rpc] GENIv3DelegateBase for more information."""
        options = self._default_options()
        if best_effort != None:
            options["geni_best_effort"] = best_effort
        return self._proxy.Delete(urns, credentials, options)

    def shutdown(self, slice_urn, credentials):
        """See class description above and the [geniv3rpc] GENIv3DelegateBase for more information."""
        options = self._default_options()
        return self._proxy.Shutdown(slice_urn, credentials, options)

    def _default_options(self):
        """Private method for generating the default option hash, which is parsed on the server."""
        return {"geni_rspec_version" : {"version" : 3, "type" : "geni"}}

    # helper methods
    def datetime2str(self, dt):
        """Convers a datetime to a string which can be parsed by the GENI AM API server."""
        return dt.strftime(self.RFC3339_FORMAT_STRING)
    def str2datetime(self, strval):
        """Coverts a date string given by the GENI AM API server to a python datetime object.
        It parses the given date string and converts the timestamp to utc and the date unaware of timezones."""
        result = dateparser.parse(strval)
        if result:
            result = result - result.utcoffset()
            result = result.replace(tzinfo=None)
        return result

    def raiseIfError(self, response):
        """Raises an GENI3ClientError if the server response contained an error."""
        if self.isError(response):
            raise GENI3ClientError(self.errorMessage(response), self.errorCode(response))
        return

    def errorMessage(self, response):
        return response['output']
    def errorCode(self, response):
        return int(response['code']['geni_code'])
    def isError(self, response):
        return self.errorCode(response) != 0
"""end of all the method for the client"""


class tempInfo(models.Model):
    id=models.IntegerField()
    url=models.CharField(max_length=100)
    username=models.CharField(max_length=100)
    password=models.CharField(max_length=100)

class tempVtam(models.Model):
    id=models.IntegerField()
    name=models.CharField(max_length=100)
    vtamID=models.IntegerField()

TEMPLATE_PATH = "expedient/clearinghouse/vslice"

def create(request, proj_id):
    '''Create a vslice'''
    project = get_object_or_404(Project, id=proj_id)
    
    must_have_permission(request.user, project, "can_create_vslices")
    
    def pre_save(instance, created):
        instance.project = project
        instance.owner = request.user
	#Generate UUID: fixes caching problem on model default value
	instance.uuid = uuid.uuid4()
	instance.save()
        
        instance.reserved = False
    
    #use to give the can_delete_vslices over the vslice to the creator and the owners of the project 
    def post_save(instance, created):
	give_permission_to("can_delete_vslices", instance, instance.owner, giver=None, can_delegate=False)
#	for projectOwner in instance.project._get_owners():
#		give_permission_to("can_delete_vslices", instance, projectOwner, giver=None, can_delegate=False)	

 
    return generic_crud(
        request, None, Vslice,
        TEMPLATE_PATH+"/create_update.html",
        redirect=lambda instance:reverse("vslice_detail", args=[instance.id]),
        form_class=VsliceCrudForm,
        extra_context={
            "project": project,
            "title": "Create vslice",
            "cancel_url": reverse("project_detail", args=[proj_id]),
        },
        pre_save=pre_save,
        post_save=post_save,
        success_msg = lambda instance: "Successfully created vslice %s." % instance.name,
    )

def update(request, vslice_id):
    '''Update a vslice's information'''
    
    project = get_object_or_404(Project, vslice__pk=vslice_id)
    must_have_permission(request.user, project, "can_edit_vslices")

    return generic_crud(
        request, vslice_id, Vslice,
        TEMPLATE_PATH+"/create_update.html",
        redirect=lambda instance:reverse("vslice_detail", args=[instance.id]),
        extra_context={
            "title": "Create vslice",
            "cancel_url": reverse("vslice_detail", args=[vslice_id]),
        },
        form_class=VsliceCrudForm,
        success_msg = lambda instance: "Successfully updated vslice %s." % instance.name,
    )

def delete(request, vslice_id):
    '''Delete the vslice'''
    vslice = get_object_or_404(Vslice, id=vslice_id)
    project = vslice.project
    
    #VSlice can edited and used by anyone in the project, but only the owner of the vslice
    #or the project's owner can delete it
    try:
        must_have_permission(request.user, vslice, "can_delete_vslices")
    except Exception,e:
        must_have_permission(request.user, project, "can_delete_vslices")

    if request.method == "POST":
        stop(request, vslice_id)
        vslice.delete()
        DatedMessage.objects.post_message_to_user(
            "Successfully deleted vslice %s" % vslice.name,
            request.user, msg_type=DatedMessage.TYPE_SUCCESS)
        return HttpResponseRedirect(
            reverse('project_detail', args=[project.id]))

    else:
        from vt_plugin.models.VM import VM
        if VM.objects.filter(vsliceId = vslice.uuid):
            DatedMessage.objects.post_message_to_user(
            "Please delete all VMs inside vslice '%s' before deleting it" % vslice.name,
            request.user, msg_type=DatedMessage.TYPE_ERROR)
            return detail(request, vslice_id)
        return simple.direct_to_template(
            request,
            template=TEMPLATE_PATH+"/confirm_delete.html",
            extra_context={"object": vslice},
        )

def detail(request, vslice_id):
    '''Show information about the vslice'''
    vslice = get_object_or_404(Vslice, id=vslice_id)

    must_have_permission(request.user, vslice.project, "can_view_project")   
    resource_list  = []
    
    aggregate_list = vslice.project.aggregates.filter(
        id__in=vslice.aggregates.values_list("id", flat=True)).filter(leaf_name="VtPlannerAggregate")
    aggregate_on=aggregate_list.count();
    '''resource_list = [rsc.as_leaf_class() for rsc in vslice.resource_set.all()]'''

    template_list_computation = []
    template_list_network = []
    for plugin in PLUGIN_LOADER.plugin_settings:
        try:
            plugin_dict = PLUGIN_LOADER.plugin_settings.get(plugin)
            # Get templates according to the plugin category ('computation' or 'network')
            # instead of directly using "TEMPLATE_RESOURCES" settings
            if plugin_dict.get("general").get("resource_type") == "computation":
                template_list_computation.append(plugin_dict.get("paths").get("template_resources"))
            elif plugin_dict.get("general").get("resource_type") == "network":
                template_list_network.append(plugin_dict.get("paths").get("template_resources"))
        except Exception as e:
            print "[WARNING] Could not obtain template to add resources to slides in plugin '%s'. Details: %s" % (str(plugin), str(e))

    plugin_context = TOPOLOGY_GENERATOR.load_ui_data(vslice)
    logger.debug("##############################################################")
    logger.debug("##############################################################")
    logger.debug("##############################################################")
    vtplanner_url=""
    vtplanner_username=""
    vtplanner_password=""
    if (len(aggregate_list)>0):
      logger.debug("################ %s" % (aggregate_list[0].name) )
      #vtam=tempVtam.objects.raw('SELECT id, name FROM aggregate_aggregate WHERE leaf_name =  "vtPlugin"')[0]
      vtam=tempVtam.objects.raw('SELECT id, name, t2.vtamID  FROM aggregate_aggregate AS t1 INNER JOIN (SELECT vtamID FROM vt_plugin_resourceshash WHERE sliceUUID = "'+vslice.uuid+'")  AS t2 ON t1.id = t2.vtamID')[0]
      prova=tempInfo.objects.raw('SELECT tab1.id,  tab1.url, tab1.username, tab1.password FROM vtplanner_xmlrpcserverproxy AS tab1 INNER JOIN (SELECT id FROM aggregate_aggregate WHERE name = "'+aggregate_list[0].name+'") AS tab2 ON tab1.id = tab2.id')[0]
    #agg_form = VtPlannerAggregateForm(instance=aggregate_list[0])
    #name_=aggregate_list[0].split(' ');
    #cheese_blog = Blog.objects.get(name="Cheddar Talk")
    #logger.debug("################ %s" % (name_[1]) )
      print(vtam.id)
      print(vtam.name)
      print(vtam.vtamID)
      logger.debug("################ID   %s" % vtam.id)
      logger.debug("################NAME %s" % vtam.name)
      vtplanner_id=prova.id
      vtplanner_url=prova.url
      vtplanner_username=prova.username
      vtplanner_password=prova.password
      vtamId=vtam.id
    logger.debug("##############################################################")
    logger.debug("##############################################################")
#    if not plugin_context['d3_nodes'] or not plugin_context['d3_links']:
#        template_list_computation = []
#        template_list_network = []
    if (len(aggregate_list)>0):
        unique_aggregate=aggregate_list[0]
    extra_context={
            "breadcrumbs": (
                ("Home", reverse("home")),
                ("Project %s" % vslice.project.name, reverse("project_detail", args=[vslice.project.id])),
                ("Vslice %s" % vslice.name, reverse("vslice_detail", args=[vslice_id])),
            ),
            "resource_list": resource_list,
            "plugin_template_list_network": template_list_network,
            "plugin_template_list_computation": template_list_computation,
            "plugins_path": PLUGIN_LOADER.plugins_path,
            "vtplanner_aggregate": aggregate_list,
            "aggregate_on": aggregate_on,
            "vtplanner_url":vtplanner_url,
            "vtplanner_username" :vtplanner_username,
            "vtplanner_password": vtplanner_password,
            "vtamid":vtam.vtamID
            
    }

    return list_detail.object_detail(
        request,
        Vslice.objects.all(),
        object_id=vslice_id,
        template_name=TEMPLATE_PATH+"/detail.html",
        template_object_name="vslice",
	extra_context=dict(extra_context.items()+plugin_context.items())
    )
    
def start(request, vslice_id):
    '''Start the vslice on POST'''
    vslice = get_object_or_404(Vslice, id=vslice_id)
    
    must_have_permission(request.user, vslice.project, "can_start_vslices")
    
    if request.method == "POST":

        if False in vslice._get_aggregates().values_list("available",flat=True):
            DatedMessage.objects.post_message_to_user(
                "Vslice %s can not be started because some of its AMs is not available" % vslice.name,
                request.user, msg_type=DatedMessage.TYPE_ERROR)
            return HttpResponseRedirect(reverse("vslice_detail", args=[vslice_id]))


        try:
            excs = vslice.start(request.user)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print e
            DatedMessage.objects.post_message_to_user(
                "Error starting vslice %s: %s" % (
                    vslice.name, parseFVexception(e)),
                user=request.user, msg_type=DatedMessage.TYPE_ERROR)
        else:
            if not excs:
                DatedMessage.objects.post_message_to_user(
                    "Successfully started vslice %s" % vslice.name,
                     request.user, msg_type=DatedMessage.TYPE_SUCCESS)
            else:
                DatedMessage.objects.post_message_to_user(
                    "Vslice %s was started, but some AMs could not be started. Double check your VMs status" % vslice.name,
                     request.user, msg_type=DatedMessage.TYPE_SUCCESS)
        return HttpResponseRedirect(reverse("vslice_detail", args=[vslice_id]))
    else:
        return HttpResponseNotAllowed(["POST"])
    
def stop(request, vslice_id):
    '''Stop the vslice on POST'''
    vslice = get_object_or_404(Vslice, id=vslice_id)
    
    must_have_permission(request.user, vslice.project, "can_stop_vslices")
    
    if request.method == "POST":
        try:
            vslice.stop(request.user)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print e
            DatedMessage.objects.post_message_to_user(
                "Error stopping vslice %s: %s" % (
                    vslice.name, parseFVexception(e)),
                user=request.user, msg_type=DatedMessage.TYPE_ERROR)
        else:
            DatedMessage.objects.post_message_to_user(
                "Successfully stopped vslice %s" % vslice.name,
                request.user, msg_type=DatedMessage.TYPE_SUCCESS)
        return HttpResponseRedirect(reverse("vslice_detail", args=[vslice_id]))
    else:
        return HttpResponseNotAllowed(["POST"])

def select_ui_plugin(request, vslice_id):
    vslice = get_object_or_404(Vslice, id=vslice_id)
    
    plugins_info = getattr(settings, "UI_PLUGINS", [])
    
    logger.debug("select_ui_plugin plugins_info %s" % (plugins_info,))
    
    # plugin functions should return (name, description, url)
    plugins = [get_callable(plugin[0])(vslice) for plugin in plugins_info]

    logger.debug("select_ui_plugin plugins %s" % (plugins,) )
    
    return simple.direct_to_template(
        request,
        template=TEMPLATE_PATH+"/select_ui_plugin.html",
        extra_context={
            "plugins": plugins, "vslice": vslice,
            "breadcrumbs": (
                ("Home", reverse("home")),
                ("Project %s" % vslice.project.name, reverse("project_detail", args=[vslice.project.id])),
                ("Vslice %s" % vslice.name, reverse("vslice_detail", args=[vslice_id])),
                ("Select UI", request.path),
            ),
        },
    )

def add_aggregate(request, vslice_id):
    '''Add aggregate to vslice'''
    
    vslice = get_object_or_404(Vslice, id=vslice_id)
    
    must_have_permission(request.user, vslice.project, "can_edit_vslices")
    
    aggregate_list = vslice.project.aggregates.exclude(
        id__in=vslice.aggregates.values_list("id", flat=True)).filter(leaf_name="VtPlannerAggregate")
    
    if request.method == "GET":
        return simple.direct_to_template(
            request, template=TEMPLATE_PATH+"/add_aggregates.html",
            extra_context={
                "aggregate_list": aggregate_list,
                "vslice": vslice,
                "breadcrumbs": (
                    ("Home", reverse("home")),
                    ("Project %s" % vslice.project.name, reverse("project_detail", args=[vslice.project.id])),
                    ("Vslice %s" % vslice.name, reverse("vslice_detail", args=[vslice_id])),
                    ("Add Vslice Aggregates", request.path),
                ),
            }
        )
    
    elif request.method == "POST":
        # check which submit button was pressed
        try:
            agg_id = int(request.POST.get("id", 0))
        except ValueError:
            raise Http404

        if agg_id not in aggregate_list.values_list("id", flat=True):
            raise Http404
        aggregate = get_object_or_404(Aggregate, id=agg_id).as_leaf_class()
        return HttpResponseRedirect(aggregate.add_to_vslice(
            vslice, reverse("vslice_add_agg", args=[vslice_id])))
    else:
        return HttpResponseNotAllowed("GET", "POST")
        
        
        
def add_aggregate_vtam(request,vslice_id, vtam_id):
    '''Add aggregate to vslice'''
    print (vslice_id)
    print (vtam_id)
    agg_id = vtam_id
    vslice = get_object_or_404(Vslice, id=vslice_id)
    from vt_plugin.models import VtPlugin#, VTServer, VM, Action
    vt_aggs = vslice.aggregates.filter(leaf_name=VtPlugin.__name__.lower())
    try:
        from vt_plugin.controller.vtAggregateController.vtAggregateController import askForAggregateResources

        for agg in vt_aggs:
            vtPlugin = agg.as_leaf_class()
            project_uuid = Project.objects.filter(id = vslice.project_id)[0].uuid
            askForAggregateResources(vtPlugin, projectUUID = project_uuid, sliceUUID = vslice.uuid)
    except:
        pass
    aggregate = get_object_or_404(Aggregate, id=agg_id).as_leaf_class()
    aggregate.add_to_vslice(vslice, reverse("vslice_add_agg", args=[vslice_id]))

        
        
    
def update_aggregate(request, vslice_id, agg_id):
    '''Update any info stored at the aggregate'''
    
    vslice = get_object_or_404(Vslice, id=vslice_id)

    must_have_permission(request.user, vslice.project, "can_edit_vslices")
    
    aggregate = get_object_or_404(
        Aggregate, id=agg_id, id__in=vslice.aggregates.values_list(
            "id", flat=True)).as_leaf_class()

    if request.method == "POST":
        #return HttpResponseRedirect(aggregate.add_to_slice(
        return HttpResponseRedirect(aggregate.add_controller_to_vslice(
            vslice, reverse("vslice_detail", args=[vslice_id])))
    else:
        return HttpResponseNotAllowed(["POST"])

def remove_aggregate(request, vslice_id, agg_id):

    vslice = get_object_or_404(Vslice, id=vslice_id)

    must_have_permission(request.user, vslice.project, "can_edit_vslices")
    
    aggregate = get_object_or_404(
        Aggregate, id=agg_id, id__in=vslice.aggregates.values_list(
            "id", flat=True)).as_leaf_class()

    if request.method == "POST":
        try:
            return HttpResponseRedirect(aggregate.remove_from_vslice(
                vslice, reverse("vslice_detail", args=[vslice_id])))
        except MultipleObjectsReturned as e:
            DatedMessage.objects.post_message_to_user(
                str(e), request.user, msg_type=DatedMessage.TYPE_ERROR)
        except:
            pass
        # If any error occurs, redirect to vslice detail page
        return HttpResponseRedirect(
            reverse('vslice_detail', args=[vslice_id]))
    else:
        return HttpResponseNotAllowed(["POST"])



def contact(request,vslice_id):
    if request.method == 'POST': # If the form has been submitted...
        #form = ContactForm(request.POST) # A form bound to the POST data
        usable=0;
        if 'id_subject' in request.POST:
           usable+=1
           subject = request.POST['id_subject']
           logger.debug('tua nonnna!!!!!!!!!!!!!!!!!!!!!! id_subject\n')
           logger.debug(subject)
          
        if 'available' in request.POST:
           usable+=1
           available = request.POST['available']
           logger.debug('tua nonnna!!!!!!!!!!!!!!!!!!!!!! available\n')

        server = xmlrpclib.Server("https://user:password@127.0.0.1:9445")
        valueBack=server.get_resources()
        logger.debug(valueBack)
        if usable==2: # All validation rules pass
            logger.debug("oooooooooooooooooooooooooooooooooooooooooooooooooook")
            return HttpResponseRedirect( reverse('vslice_detail', args=[vslice_id]))
            # Process the data in form.cleaned_data
            # ...
            #request.POST['available']=1
            #return HttpResponseRedirect('/vslice/detail/'.vslice_id.'/') # Redirect after POST
            #return HttpResponse(valueBack)
            #url='/vslice/detail/'+vslice_id+'/'
            #return render_to_response(url, {"pippo": "pippo"})
            #return HttpResponse(valueBack)
    else:
        form = ContactForm() # An unbound form
    return HttpResponseRedirect(request.META.get('HTTP_REFERER')) # Redirect after POST
    #return render(request, 'contact.html', {   'form': form,})
'''
def freeRes(request,vslice_id):
	splitAdd=request.POST['vtplanner_url'].split('/')
	newAdd=splitAdd[2].split(':')
	print(splitAdd[2])
	print(newAdd[0])
	nameS=("%s" %request.POST['vSliceName'])
	string='urn:publicid:IDN+geni:gpo:gcf+slice+'+nameS
	urn=[string]
	urn = [(','.join(str(v) for v in urn))]
	prevdir=os.getcwd()
	os.chdir("/root/gcf/")
	local_path = os.path.normpath(os.path.dirname(__file__))
	client = GENI3Client(newAdd[0], newAdd[1], key_path, cert_path)
	sys.path.append('/root/gcf/src/')
	p = subprocess.Popen(['python', 'src/omni.py', 'getslicecred', nameS], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	res=err
	errInit=err.find('<?xml version="1.0"?>')
	errEnd =err.find('</signed-credential>') +20
	mycred=res[errInit:errEnd]
	os.chdir(prevdir)
	finalcred={'geni_value': mycred,'geni_version': '3', 'geni_type': 'geni_sfa'}
	jsonToClean= client.delete(urn, [finalcred])
	return HttpResponse(jsonToClean)
'''	
def provisionRes(request,vslice_id):
	splitAdd=request.POST['vtplanner_url'].split('/')
	newAdd=splitAdd[2].split(':')
	print(splitAdd[2])
	print(newAdd[0])
	nameS=("%s" %request.POST['vSliceName'])
	string='urn:publicid:IDN+geni:gpo:gcf+slice+'+nameS
	urn=[string]
	urn = [(','.join(str(v) for v in urn))]
	prevdir=os.getcwd()
	os.chdir("/root/gcf/")
	local_path = os.path.normpath(os.path.dirname(__file__))
	client = GENI3Client(newAdd[0], newAdd[1], key_path, cert_path)
	sys.path.append('/root/gcf/src/')
	p = subprocess.Popen(['python', 'src/omni.py', 'getslicecred', nameS], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	res=err
	errInit=err.find('<?xml version="1.0"?>')
	errEnd =err.find('</signed-credential>') +20
	mycred=res[errInit:errEnd]
	os.chdir(prevdir)
	finalcred={'geni_value': mycred,'geni_version': '3', 'geni_type': 'geni_sfa'}
	#jsonToClean= client.delete(urn, [finalcred])
	client.provision(urn, [finalcred], best_effort=True, end_time= datetime.now())
	
	
	
	
def getRes(request,vslice_id):
	#ServerAddress="https://openflow:openflow@10.216.32.44:8001"
	splitAdd=request.POST['vtplanner_url'].split('/')
	#ServerAddress="https://"+request.POST['vtplanner_username']+":"+request.POST['vtplanner_password']+"@"+splitAdd[2]
	newAdd=splitAdd[2].split(':')
	#server = xmlrpclib.Server(ServerAddress)
	print(splitAdd[2])
	print(newAdd[0])
	nameS=("%s" %request.POST['vSliceName'])
	string='urn:publicid:IDN+geni:gpo:gcf+slice+'+nameS
	urn=[string]
	urn = [(','.join(str(v) for v in urn))]
	
	################################################
	#Here I have the client v3 call
	#it is based on the AMSoil/test/client
	key_path ='/root/.gcf/alice-key.pem'
	cert_path='/root/.gcf/alice-cert.pem'
	# instanciate the client
	import subprocess
	prevdir=os.getcwd()
	os.chdir("/root/gcf/")
	local_path = os.path.normpath(os.path.dirname(__file__))
	client = GENI3Client(newAdd[0], newAdd[1], key_path, cert_path)
	sys.path.append('/root/gcf/src/')
	p = subprocess.Popen(['python', 'src/omni.py', 'getslicecred', nameS], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	res=err
	errInit=err.find('<?xml version="1.0"?>')
	errEnd =err.find('</signed-credential>') +20
	mycred=res[errInit:errEnd]
	os.chdir(prevdir)
	finalcred={'geni_value': mycred,'geni_version': '3', 'geni_type': 'geni_sfa'}
	jsonToClean= client.status(urn, [finalcred])
	print (jsonToClean)
	################################################
	
	if (jsonToClean['output']==None):
		xml=jsonToClean['value']['geni_urn']
		jsonBack=xml2json(xml)
		print (jsonBack)
	elif('[SEARCHFAILED]' in jsonToClean['output']):
		#logger.debug("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
		jsonBack=[{}]
	else:
		jsonBack=[{}]

	return HttpResponse(jsonBack) #ritorna il mio xml 
	
def checkAv(request,vslice_id):
	splitAdd=request.POST['vtplanner_url'].split('/')
	newAdd=splitAdd[2].split(':')
	#ServerAddress="https://"+request.POST['vtplanner_username']+":"+request.POST['vtplanner_password']+"@"+splitAdd[2]
	#server = xmlrpclib.Server(ServerAddress)
	xml=[]
	if request.method == 'POST': # If the form has been submitted...			vSliceName
	    if 'vSliceName' in request.POST:
				vSliceName=request.POST['vSliceName']
	    if 'xml' in request.POST:
             print('this is the rspec')
             rspec = request.POST['xml']
             print (rspec)
             nameS=("%s" %request.POST['vSliceName'])
             string='urn:publicid:IDN+geni:gpo:gcf+slice+'+nameS
             urn=[string]
             urn = [(','.join(str(v) for v in urn))]
             logger.debug("###########################################################%s" %urn)
             ################################################
             #Here I have the client v3 call
             #it is based on the AMSoil/test/client
             key_path ='/root/.gcf/alice-key.pem'
             cert_path='/root/.gcf/alice-cert.pem'
             # instanciate the client
             import subprocess
             prevdir=os.getcwd()
             os.chdir("/root/gcf/")
             local_path = os.path.normpath(os.path.dirname(__file__))
             client = GENI3Client(newAdd[0], newAdd[1], key_path, cert_path)
             sys.path.append('/root/gcf/src/')
             p = subprocess.Popen(['python', 'src/omni.py', 'getslicecred', nameS], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
             out, err = p.communicate()
             res=err
             errInit=err.find('<?xml version="1.0"?>')
             errEnd =err.find('</signed-credential>') +20
             mycred=res[errInit:errEnd]
             os.chdir(prevdir)
             finalcred={'geni_value': mycred,'geni_version': '3', 'geni_type': 'geni_sfa'}
             jsonToClean= client.status(urn, [finalcred])
             print client.allocate(string, [finalcred], rspec, datetime.now())
             print (jsonToClean)
	################################################
             
             
             
             #xml=server.Allocate(urn,cred,rspec, "")
             logger.debug(xml)
	   
	return HttpResponse(xml) #ritorna il mio xml     


def freeRes(request,vslice_id):
	#ServerAddress="https://openflow:openflow@10.216.32.44:8001"
	splitAdd=request.POST['vtplanner_url'].split('/')
	#ServerAddress="https://"+request.POST['vtplanner_username']+":"+request.POST['vtplanner_password']+"@"+splitAdd[2]
	newAdd=splitAdd[2].split(':')
	#server = xmlrpclib.Server(ServerAddress)
	print(splitAdd[2])
	print(newAdd[0])
	nameS=("%s" %request.POST['vSliceName'])
	string='urn:publicid:IDN+geni:gpo:gcf+slice+'+nameS
	urn=[string]
	urn = [(','.join(str(v) for v in urn))]
	
	################################################
	#Here I have the client v3 call
	#it is based on the AMSoil/test/client
	key_path ='/root/.gcf/alice-key.pem'
	cert_path='/root/.gcf/alice-cert.pem'
	# instanciate the client
	import subprocess
	prevdir=os.getcwd()
	os.chdir("/root/gcf/")
	local_path = os.path.normpath(os.path.dirname(__file__))
	client = GENI3Client(newAdd[0], newAdd[1], key_path, cert_path)
	sys.path.append('/root/gcf/src/')
	p = subprocess.Popen(['python', 'src/omni.py', 'getslicecred', nameS], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	res=err
	errInit=err.find('<?xml version="1.0"?>')
	errEnd =err.find('</signed-credential>') +20
	mycred=res[errInit:errEnd]
	os.chdir(prevdir)
	finalcred={'geni_value': mycred,'geni_version': '3', 'geni_type': 'geni_sfa'}
	resp= client.delete(urn, [finalcred])
	print (resp)
	return HttpResponse(resp)
	################################################



def xml2json(rspec):
 root = ET.fromstring(rspec)
 email      =root[0].get('email')
 description=root[0].get('description')
 root[0][0].attrib
 url_ =root[0][0].get('url')
 type_=root[0][0].get('type')

 vertices=[{}]
 edges=[{}]
 #vms=[{}]
 matches=[{}]
 algorithm=root[0][1].get('algorithm')
 ofversion=root[0][1].get('ofversion')
 #vertici
 vertexname=(root[0][2].tag).replace("{/opt/foam/schemas}", "openflow:");
 vertices.pop()
 #vms.pop()
 for child in root[0][2]:
  type_=child.get('type')
  if (type_=="switch"):
    tablesize=child.get('tablesize')
    switchtype=child.get('switchtype')
    dpid=child.get('dpid')
    name=child.get('name')
    print (type_)
    tmpVert={'tablesize':tablesize,'switchtype':switchtype, 'dpid':dpid, 'name':name, 'type': "switch"}
    vertices.append(tmpVert)
  if(type_=="vm"):
    type="vm"
    cpu_frequency=child.get('cpu_frequency');
    cpus_number=child.get('cpus_number');
    dpid=child.get('dpid');
    memory=child.get('memory');
    name=child.get('name'); 
    tmpVm={'dpid':dpid, 'name':name, 'memory':memory, 'cpu_frequency':cpu_frequency,'cpus_number':cpus_number, 'type': "vm"  }
    vertices.append(tmpVm)
    
 
 #edges
 edgename=(root[0][3][0].tag).replace("{/opt/foam/schemas}", "openflow:");
 edges.pop()
 for child in root[0][3]:
  srcDPID=child.get('srcDPID')
  dstDPID=child.get('dstDPID')
  bw=child.get('bw')
  tmpEdge={'srcDPID':srcDPID,'dstDPID':dstDPID, 'bw':bw }
  edges.append(tmpEdge) 
 #completeList=[{'vertices':vertices},{'vms':vms}, {'edges':edges}]
 completeList=[{'vertices':vertices}, {'edges':edges}]
 jsonBack= json.dumps(completeList)
 return jsonBack

