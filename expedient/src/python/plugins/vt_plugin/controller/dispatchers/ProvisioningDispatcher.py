from vt_manager.communication.utils.XmlHelper import XmlHelper
import os
import sys
from expedient.common.messaging.models import DatedMessage
from vt_plugin.models import *
from vt_plugin.utils.ServiceThread import *
from vt_plugin.utils.Translator import Translator
import xmlrpclib, threading, logging
from expedient.clearinghouse.settings import ROOT_USERNAME, ROOT_PASSWORD, SITE_IP_ADDR

#PLUGIN_URL = 'https://'+ROOT_USERNAME+':'+ROOT_PASSWORD+'@'+SITE_IP_ADDR+'/vt_plugin/xmlrpc/vt_am/'

class ProvisioningDispatcher():
    
    '''
    manages all the (VM) provisioning actions (create, start, stop, reboot, delete)
    that go from the Vt Plugin to the VT AM
    '''
    
    @staticmethod    
    def processProvisioning(provisioning):

        #go through all actions in provisioning class
        print ("processProvisioning")
        for action in provisioning.action:
            #translate action to actionModel
            actionModel = Translator.ActionToModel(action,"provisioning")
            actionModel.requestUser = threading.currentThread().requestUser
            print ("action che ho io: ")
            print (actionModel.type)
            if actionModel.type == "create":
                print("CCCCCCCCCCCCCCCCREATE")
                if Action.objects.filter (uuid = actionModel.uuid):
                    #if action already exists we raise exception. It shouldn't exist because it is create action!
                    try:
                        raise Exception
                    except Exception as e:
                        logging.error("Action already exists")
                        logging.error(e)
                        return                
                else:
                    actionModel.save()

                try:
                    Server = VTServer.objects.get(uuid =  action.server.uuid)
                    VMmodel = Translator.VMtoModel(action.server.virtual_machines[0], Server.aggregate_id, "save")
                    print ("++++++++++++++++++inizio+++++++++++++++++++")
                    print Server.aggregate_id
                    print VMmodel.getName()
                    print VMmodel.getState()
                    print VMmodel.getUUID()
                    print VMmodel.getProjectId()
                    print VMmodel.getProjectName()
                    print VMmodel.getSliceId()
                    print VMmodel.getSliceName()
                    print VMmodel.getOStype()
                    print VMmodel.getOSversion()
                    print VMmodel.getOSdist()
                    print VMmodel.getVirtTech()
                    print VMmodel.getServerID()
                    print VMmodel.getHDsetupType()
                    print VMmodel.getHDoriginPath()
                    print VMmodel.getVirtualizationSetupType()
                    print VMmodel.getMemory()


                    print ("+++++++++++++++++++fine++++++++++++++++++++")
                    Server.vms.add(VMmodel)
                    actionModel.vm = VMmodel
                    actionModel.save()
                except Exception as e:
                    logging.error("Not possible to translate to VM model\n")
                    logging.error(e)
                    try:
                        vm_name = VMmodel.name
                    except:
                        vm_name = action.server.virtual_machines[0].name

                    DatedMessage.objects.post_message_to_user(
                        "Not possible to translate VM %s to a proper app model" % vm_name,
                        threading.currentThread().requestUser, msg_type=DatedMessage.TYPE_ERROR,
                    )

                    try:
                        VMmodel.completeDelete()
                        Server.vms.remove(VMmodel)
                    except:
                        pass

                    return                
                client = Server.aggregate.as_leaf_class().client
                
                ProvisioningDispatcher.connectAndSend('https://'+client.username+':'+client.password+'@'+client.url[8:], action, client)                

            elif actionModel.type == "delete" :

                #ProvisioningDispatcher.checkVMisPresent(action)
                VMmodel =  VM.objects.get(uuid = action.server.virtual_machines[0].uuid)
                if not  VMmodel:
                    try:
                        raise Exception
                    except Exception as e:
                        logging.error("No VM found to start it\n")
                        logging.error(e)
                        return
                    
                #ProvisioningDispatcher.checkActionIsPresent(actionModel)
                if Action.objects.filter(uuid = actionModel.uuid):
                    try:
                        raise Exception
                    except Exception as e:
                        logging.error("Action already exists")
                        logging.error(e)
                        return
                else:
                    logging.error("ACTION delete is going to be saved")
                    actionModel.vm = VMmodel
                    actionModel.save()
                
                try:	
                    Server = VTServer.objects.get(uuid = VMmodel.getServerID() )
                    client = Server.aggregate.as_leaf_class().client
                    ProvisioningDispatcher.connectAndSend('https://'+client.username+':'+client.password+'@'+client.url[8:], action, client) 
                    #VMmodel.completeDelete()
                except:
                    logging.error("Could not connect to AM")
                    logging.error(e)
                    DatedMessage.objects.post_message_to_user(
                        "Could not connect to AM",
                        threading.currentThread().requestUser, msg_type=DatedMessage.TYPE_ERROR,
                    )


            #elif actionModel.type == "start":
            else:
                
                #ProvisioningDispatcher.checkVMisPresent(action)
                VMmodel = VM.objects.get(uuid = action.server.virtual_machines[0].uuid)
                    
                if not VMmodel:
                    try:
                        raise Exception
                    except Exception as e:
                        logging.error("No VM found to start it\n")
                        logging.error(e)
                        return
                #AGENT_URL = VTServer.objects.get(name = VMmodel.getServerID() ).getAgentURL()                
                #ProvisioningDispatcher.checkActionIsPresent(actionModel)            
                if Action.objects.filter (uuid = actionModel.uuid):
                    try:
                        raise Exception
                    except Exception as e:
                        logging.error("Action already exists")
                        logging.error(e)
                        return
                else:
                    actionModel.vm = VMmodel
                    actionModel.save()
               
		try: 
                    Server = VTServer.objects.get(uuid = VMmodel.getServerID() )
                    client = Server.aggregate.as_leaf_class().client
                    ProvisioningDispatcher.connectAndSend('https://'+client.username+':'+client.password+'@'+client.url[8:], action, client)                
                except:
                    logging.error("Could not connect to AM")
                    logging.error(e)
                    DatedMessage.objects.post_message_to_user(
                        "Could not connect to AM",
                        threading.currentThread().requestUser, msg_type=DatedMessage.TYPE_ERROR,
                    )


    @staticmethod
    def connectAndSend(URL, action, client):
        print "connect and send"
        print client.username
        print client.password
        print SITE_IP_ADDR
        print URL
        print "----------action------------------"
        print action
        try:
            vt_manager = xmlrpclib.Server(URL)
            PLUGIN_URL = 'https://'+client.username+':'+client.password+'@'+SITE_IP_ADDR+'/vt_plugin/xmlrpc/vt_am/'
            print PLUGIN_URL
            print "send"
            vt_manager.send(PLUGIN_URL, XmlHelper.craftXmlClass(XmlHelper.getSimpleActionQuery(action)))
            print "sent"
        except Exception as e:
            logging.error("Exception connecting to VT Manager")
            logging.error(e)
            return

    @staticmethod
    def cleanWhenFail(vm , server = None):
        try:
            server.vms.remove(vm)
        except:
            pass
        ifaces = vm.ifaces.all()
        for iface in ifaces:
            vm.ifaces.remove(iface)
            iface.delete()
        try:
            #super(Resource).delete()
            vm.delete()
        except Exception as e:
            logging.error(e)

