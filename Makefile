start:
	@heroku ps:scale web=1

deploy:
	git push heroku master

local:
	@DEBUG=true python app.py

reqs:
	@pip install -r requirements.txt

test:
	@nosetests

clean:
	@rm *.pyc
	@rm */*.pyc