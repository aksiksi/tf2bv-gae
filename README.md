tf2bv-gae
=========

A Google App Engine version of my tf2-backpack-viewer repo.

No dependencies - simply upload the whole thing to your account using the Google App Engine SDK.

See it in action: [2.tf2-bv.appspot.com](2.tf2-bv.appspot.com)

Structure
---------

```root:
	- flask

	- werkzeug
 
	- simplejson = jinja2 dependency
 
	- jinja2
 
	- application = contains the app's files, templates etc.
 
		* templates = contains jinja2 templates

		* static = contains favicon.ico, JS, and CSS files

		* __init__.py = initializes the Flask app

		* parse.py = contains parsing functions

		* views.py = contains the app's views and routing logic

	- cron.yaml = used for running update.py every hour
 
	- app.yaml = required by GAE

	- main.py = runs the Flask app using the GAE WSGI server

	- update.py = grabs the TF2 item schema every hour and stores it in memcache```