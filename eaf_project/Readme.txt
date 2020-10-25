#packages required
1- pip install uvicorn
2- pip install sqlalchemy
3- pip install pydantic
4- pip install databases
5- pip install fastapi
6- pip install secrets
7- pip install typing

#username and password to use
Username="admin"
Password="admin"

#folder structure
  - __init__.py : defines the package.
  - database.py : contains the database setup code.
  - models.py : contains the database table creations.
  - schema.py : contains the pydantic models fof data validations.
  - main.py : contains the integration of all the modules and api's defined here (run this python file, it is the starting point of execution).

#for loading database
Database Used: Sqllite
There are two ways to do it.
1- Use test.db file as it is.
2- Use the api to load the data either from Swagger UI(http://127.0.0.1:8000/docs) or hit the below link after running main.py http://127.0.0.1:8000/loadDatabase.

#for testing
Use Swagger UI(http://127.0.0.1:8000/docs) to perform different operations.
