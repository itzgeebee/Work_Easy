# Work_Easy
A website that helps you locate the best cafe to work from
https://workeazy.herokuapp.com/

## About the Stack
The application is a fullstack application
I used:
- Flask for the backend
- HTML, CSS and Bootstrap for the frontend.
## Backend 
The [main.py](/main.py) contains a completed Flask Server.

### Setting up the backend


#### Install the dependencies
1. Python. I used version 3.9 for this project. Here's the instruction to install [python](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)
2. I recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virtual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)
3. PIP Dependencies - Once your virtual environment is up and running, install the required dependencies by running:
```bash
  pip install -r requirements.txt 
  ```

#### Key Pip Dependencies
- [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.
- [SQLAlchemy](https://docs.sqlalchemy.org/en/14/) is the Python SQL toolkit and ORM I used to handle the lightweight SQL database

#### Export flask
for Linux users:
execute: 
 ```bash
 $ export FLASK_APP = "main.py"
  ```
  
 for windows cmd:
 ```
 FLASK_APP=main.py
 ```
#### Run the Server

```bash
  flask run --reload
  ```
 
