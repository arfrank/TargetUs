#this should really be done via a dictionary, but quick then fast
def determine_device(headers):
	ua = headers.get('User-Agent')
	family, device = 'default', 'default'
	if 'iPhone' in ua:
		family = 'iOS'
		device = 'iPhone'
	elif 'iPod' in ua:
		family = 'iOS'
		device = 'iPod'
	elif 'iPad' in ua:
		family = 'iOS'
		device = 'iPad'
	elif 'Android' in ua:
		family = 'Android'
		if 'Android 2.1' in ua:
			device = 'Eclair'
		elif 'Android 2.0' in ua:
			device = 'Eclair'
		elif 'Android 2.2' in ua:
			device = 'Froyo'
		elif 'Android 2.3' in ua:
			device = 'Gingerbread'
		elif 'Android 3.0' in ua:
			device = 'Honeycomb'
	elif 'webOS' in ua:
		family = 'webOS'
		if 'Pre' in ua:
			device = 'Pre'
		elif 'Pixi' in ua:
			device = 'Pixi'
		elif 'Veer' in ua:
			device = 'Veer'
	return family, device