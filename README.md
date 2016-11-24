




TWEleReceipt
===================================

<font color="red">
    WARNING: This project is built under python2.7
</font>

This is a project to get receipts data from authority.
Which can calculate and summarize the data.

The server was built by Django, and default database was sqlite

# Client
	This client should run after the server was up.

Initial
-----------------------------------
        Modify the {server_ip} and {server_port} in TaskSolver.py

Start Client
-----------------------------------
        python2 TaskSolver.py


# Server

Initial
-----------------------------------
		virtualenv .
		source bin/activate
		pip install -r requirements.txt

Initial Database
-----------------------------------
		python manage.py makemigrations taskServer
		python manage.py migrate

Start Server
-----------------------------------
		python manage.py runserver  [server_ip:server_port]


Add Task  URL
-----------------------------------
        server_ip:server_port/

Author
-----------------------------------
[Chia-Wei Hsu](https://github.com/hsucw)<br />
[Daniel](https://github.com/daniel0076)<br />
[Stanley](https://github.com/stanley17112000)<br />
