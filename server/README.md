TWEleReceipt-Server
===================================
This is a server to dispatch tasks to [taskSolver](https://github.com/stanley17112000/TWEleReceipt)<br />
The server was built by Django, and default database was sqlite


Initial
-----------------------------------
		virtualenv .
		source bin/activate
		pip install -r requirements.txt

Initial Database
-----------------------------------
		python manage.py makemigrations taskServer
		python manage.py migrate
		python manage.py loaddata taskServer/fixtures/initial_task.json 

Start Server
-----------------------------------
		python manage.py runserver

Author
-----------------------------------
[Chia-Wei Hsu](https://github.com/hsucw)<br />
[Daniel](https://github.com/daniel0076)<br />
[Stanley](https://github.com/stanley17112000)<br />
