'''
Created on Jul 23, 2013

@author: atty
'''

#def parseFVexception(exc):
#	try:
#	    return str(exc).split(':',2)[2][0:-2]
#        except:
#            return str(exc)
def parseFVexception(e):
    import re
    try:
        r = re.findall("!!(.*?)!!",str(e))
    except Exception,a:
        return str(e)
    if r:
        return r[0]
    else:
        return str(e)

class startAggregateException(Exception):
	def __init__(self, vslice, agg):
		self.value = value
	def __str__(self):
		return repr("Could not start Aggregate Manager: %s in vslice: %s."  %(agg.name, vslice.name))
