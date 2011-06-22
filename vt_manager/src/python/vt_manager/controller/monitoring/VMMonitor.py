from threading import Thread
from vt_manager.communication.XmlRpcClient import XmlRpcClient
from vt_manager.communication.utils.XmlHelper import XmlHelper
from vt_manager.controller.actions.ActionController import ActionController
from vt_manager.models.Action import Action
from vt_manager.utils.UrlUtils import UrlUtils

'''
	author:msune
	Encapsulates VM monitoring methods	
'''

class VMMonitor(): 
	
	@staticmethod
	def sendUpdateVMs(server):
		#Recover from the client the list of active VMs
		obj = XmlHelper.getListActiveVMsQuery()
	
		#Create new Action 
		action = ActionController.createNewAction(Action.MONITORING_SERVER_VMS_TYPE,Action.QUEUED_STATUS,server.getUUID(),"") 

			
		obj.query.monitoring.action[0].id = action.getUUID() 
		obj.query.monitoring.action[0].server.virtualization_type = server.getid = server.getVirtTech() 
		XmlRpcClient.callRPCMethod(server.getAgentURL(),"send",UrlUtils.getOwnCallbackURL(),0,server.agentPassword,XmlHelper.craftXmlClass(obj))
		
		

	@staticmethod
	def processUpdateVMsList(server,vmList):
		from vt_manager.models.VirtualMachine import VirtualMachine
		for vm in server.getChildObject().vms.all():
			isUp = False
			for iVm in vmList:
				if iVm.uuid == vm.uuid:
					#Is running
					vm.setState(VirtualMachine.RUNNING_STATE)
					isUp = True
					break

			if isUp:
				continue

			#Is not running
			vm.serState(VirtualMachine.STOPPED_STATE)
		
