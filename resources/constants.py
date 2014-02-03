import jinja2
import os

class Constants:

	# HTML tags
	BOLD_TAG = 'b'

	JINJA_ENVIRONMENT = jinja2.Environment(
		loader=jinja2.FileSystemLoader('templates/'),
    	extensions=['jinja2.ext.autoescape'],	
    	autoescape=True)
