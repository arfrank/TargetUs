from tipfy import RequestHandler
import logging
from tipfy.appengine.sharded_counter import Counter
from utils import devices
from google.appengine.api import namespace_manager
from model import hashes
#LETS SET SOME NAMING PATTERNS!

# THINGS WE CARE ABOUT
# DEVICE
#	Family
#	Type
# TIME
#	Hour
#	24 Hour

# FOR NAMESPACE GLOBALS
#

# FOR HASH
# URL
# TYPE
# DEVICE
# 
class MainHandler(RequestHandler):
	def namespace_statistics(self, namespace, keywords):
		Counter(namespace).increment()
		Counter(namespace+'-'+keywords['family']).increment()
		Counter(namespace+'-'+keywords['device']).increment()
		
	
	#THIS GOES IN THE FORM
	#namespace-hash-index(-time?)
	
	def hash_statistics(self, namespace, hash, keywords):
		counter_names = [keywords['device'],keywords['family']]
		Counter(namespace+'-'+hash).increment()
		for name in counter_names:
			Counter(namespace+'-'+hash+'-'+name).increment()
		h = hashes.Hash.all().filter('hash =', hash).filter('deleted = ',False).get()
		if h:
			h.increment()
			h.get_location(keywords['family']).increment()
			
		#lets do things for times
		
		
	def post(self):
		logging.info("Statistics: ")
		namespace = self.request.form.get('Namespace')
		hash = self.request.form.get('Hash')
		keywords = {}
		keywords['device'] = self.request.form.get('Device')
		keywords['family'] = self.request.form.get('Family')
		keywords['time'] = self.request.form.get('Time')
		
		ns = namespace_manager.get_namespace()
		namespace_manager.set_namespace(namespace)

		self.hash_statistics(namespace,hash, keywords)
		self.namespace_statistics(namespace, keywords)
		time = self.request.form.get('Time')
		ua = self.request.form.get('User-Agent')
		logging.info(time)
		logging.info("IN THIS FUNCTION WE PROCESS STATISTICS FOR A POST")
		logging.info(ua)


		# Restore the saved namespace.
		namespace_manager.set_namespace(ns)

		return ''
		
	def get(self):
		self.post()