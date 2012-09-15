start:
	@heroku ps:scale web=1

deploy:
	git push heroku master

local:
	@foreman start

reqs:
	@pip install -r requirements.txt

test:
	@nosetests

clean:
	@rm *.pyc
	@rm */*.pyc