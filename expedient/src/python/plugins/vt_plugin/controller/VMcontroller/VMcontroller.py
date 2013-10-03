import copy
from expedient.clearinghouse.slice.models import Slice
from expedient.clearinghouse.vslice.models import Vslice
from expedient.clearinghouse.project.models import Project
from vt_plugin.models import VtPlugin, VTServer, VM, Action
from vt_manager.communication.utils.XmlHelper import XmlHelper
from vt_plugin.utils.Translator import Translator
import xmlrpclib, uuid
from vt_plugin.utils.ServiceThread import *
from vt_plugin.controller.dispatchers.ProvisioningDispatcher import *

class VMcontroller():
    
    "manages creation of VMs from the input of a given VM formulary"
    
    @staticmethod
    def processVMCreation(instance, server_id, slice, requestUser):

        if VM.objects.filter(sliceId = slice.uuid, name =instance.name):
            raise ValidationError("Another VM with name %s already exists in this slice. Please choose a new name" % instance.name)
        rspec = XmlHelper.getSimpleActionQuery()
        actionClassEmpty = copy.deepcopy(rspec.query.provisioning.action[0])
        actionClassEmpty.type_ = "create"
        rspec.query.provisioning.action.pop()

        instance.uuid = uuid.uuid4()
        instance.serverID = server_id
        instance.state = "on queue"
        instance.sliceId = slice.uuid
        instance.sliceName= slice.name

        #assign same virt technology as the server where vm created
        s = VTServer.objects.get(uuid = server_id)
        instance.virtTech = s.virtTech
        instance.projectId = slice.project.uuid
        instance.projectName = slice.project.name
        instance.aggregate_id = s.aggregate_id
        print "--------------------"
        print instance.disc_image
        #assign parameters according to selected disc image
        #TODO get the rest of image choices!
        if instance.disc_image == 'test':
            instance.operatingSystemType = 'GNU/Linux'
            instance.operatingSystemVersion = '6.0'
            instance.operatingSystemDistribution = 'Debian'
            instance.hdOriginPath = "default/test/lenny"
        if instance.disc_image == 'default':
            instance.operatingSystemType = 'GNU/Linux'
            instance.operatingSystemVersion = '6.0'
            instance.operatingSystemDistribution = 'Debian'
            instance.hdOriginPath = "default/default.tar.gz"

        actionClass = copy.deepcopy(actionClassEmpty)
        actionClass.id = uuid.uuid4()
        Translator.VMmodelToClass(instance, actionClass.server.virtual_machines[0])
        print ("=====inizio====")
        print instance.name 
        print instance.uuid 
        #print instance.status 
        #print instance.project_id 
        #print instance.project_name 
        #print instance.slice_id 
        #print instance.slice_name 
        #print instance.operating_system_type 
        #print instance.operating_system_version 
        #print instance.operating_system_distribution 
        #print instance.virtualization_type 
        #print instance.server_id 
        #print instance.xen_configuration.hd_setup_type
        #print instance.xen_configuration.hd_origin_path 
        #print instance.xen_configuration.virtualization_setup_type
        #print instance.xen_configuration.memory_mb
        print server_id
        print ("=====fine====")
        server = VTServer.objects.get(uuid = server_id)
        actionClass.server.uuid = server_id
        actionClass.server.virtualization_type = server.getVirtTech()
        rspec.query.provisioning.action.append(actionClass)
         
        ServiceThread.startMethodInNewThread(ProvisioningDispatcher.processProvisioning,rspec.query.provisioning, requestUser)


    @staticmethod
    def processVMCreationVslice(instance, server_id, vslice, requestUser):
        #server_id='14abde2b-c299-4d85-ba28-577f70f49220'
        print("processVMCreationVslice.....")
        if VM.objects.filter(sliceId = vslice.uuid, name =instance.name):
            raise ValidationError("Another VM with name %s already exists in this slice. Please choose a new name" % instance.name)
        rspec = XmlHelper.getSimpleActionQuery()
        actionClassEmpty = copy.deepcopy(rspec.query.provisioning.action[0])
        actionClassEmpty.type_ = "create"
        rspec.query.provisioning.action.pop()

        instance.uuid = uuid.uuid4()
        instance.serverID = server_id
        instance.state = "on queue"
        instance.sliceId = vslice.uuid
        instance.sliceName= vslice.name
        print instance.uuid
        print instance.serverID
        print instance.state
        print instance.sliceId
        print instance.sliceName

        ####assign same virt technology as the server where vm created
        s = VTServer.objects.get(uuid = server_id)
        instance.virtTech = s.virtTech
        #instance.virtTech='xen'
        instance.projectId = vslice.project.uuid
        instance.projectName = vslice.project.name
        instance.aggregate_id = s.aggregate_id
        #instance.aggregate_id = server_id
        #instance.disc_image ='default'
        ####assign parameters according to selected disc image
        ####TODO get the rest of image choices!
        
        if instance.disc_image == 'test':
            instance.operatingSystemType = 'GNU/Linux'
            instance.operatingSystemVersion = '6.0'
            instance.operatingSystemDistribution = 'Debian'
            instance.hdOriginPath = "default/test/lenny"
        if instance.disc_image == 'default':
            instance.operatingSystemType = 'GNU/Linux'
            instance.operatingSystemVersion = '6.0'
            instance.operatingSystemDistribution = 'Debian'
            instance.hdOriginPath = "default/default.tar.gz"
            #instance.hdOriginPath = "file-image"
        actionClass = copy.deepcopy(actionClassEmpty)
        actionClass.id = uuid.uuid4()
        Translator.VMmodelToClass(instance, actionClass.server.virtual_machines[0])
        print ("=====inizio====")
        print instance.name 
        print instance.uuid 
        #print instance.status 
        #print instance.project_id 
        #print instance.project_name 
        #print instance.slice_id 
        #print instance.slice_name 
        #print instance.operating_system_type 
        #print instance.operating_system_version 
        #print instance.operating_system_distribution 
        #print instance.virtualization_type 
        #print instance.server_id 
        #print instance.xen_configuration.hd_setup_type
        #print instance.xen_configuration.hd_origin_path 
        #print instance.xen_configuration.virtualization_setup_type
        #print instance.xen_configuration.memory_mb
        print server_id
        print ("=====fine====")
        
        
        server = VTServer.objects.get(uuid = server_id)
        actionClass.server.uuid = server_id
        actionClass.server.virtualization_type = server.getVirtTech()
        #actionClass.server.virtualization_type = server.getVirtTech()
        rspec.query.provisioning.action.append(actionClass)
        print requestUser
        print rspec
        ServiceThread.startMethodInNewThread(ProvisioningDispatcher.processProvisioning,rspec.query.provisioning, requestUser)

