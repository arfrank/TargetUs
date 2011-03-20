from tipfy import RequestHandler
import logging

class MainHandler(RequestHandler):
	def post(self):
		time = self.request.form.get('time')
		headers = self.request.form.get('headers')
		logging.info(time)
		logging.info("IN THIS FUNCTION WE PROCESS STATISTICS FOR A POST")
		logging.info(headers)
		return ''
		
	def get(self):
		self.post()