# rent book

A library service for electronic books is being developed through this project. Users are able to browse books and loan them.
## Goals

The project's main functionalities are:

* A user can search for books by title, author, or genre  
* Loaning books:
    - The loan period for books is two weeks, and the user cannot access the book after this period.
    - A user cannot borrow the same book twice in a row. (For example, for 4 consecutive weeks)
    - While a book is being loaned by a user, it cannot be loaned to another user while the loan period is ongoing.
    - Books sometimes have prerequisites, and users can't loan a book if they don't already have the prerequisites.
        - In other words, if A is a prerequisite of B and B is a prerequisite of C, users can only borrow C after having already loaned A and B.
    - Getting each book's prerequisites.

## Usage

1- The first step is to copy the project:

```commandline
git clone https://github.com/Mazafard/loan-book
```

2- Configure your `environment`:

```commandline
$ cd loan-book
$ virtualenv venv
$ pip3 install -r requirements.txt 
```

3- Once the database is created and connected to the app, the `settings.py` file should now look like this:
```python
...

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME', 'DB_NAME'),
        'USER': os.environ.get('DB_USER', 'DB_USER'),
        'PASSWORD': os.environ.get('DB_PASS', 'DB_PASS'),
        'HOST': os.environ.get('DB_HOST', 'DB_PASS'),
        'PORT': os.environ.get('DB_PORT', 'DB_PORT'),
    }
}

...
```

4- To run all `migrations`, follow these steps:

```commandline
$ python3 manage.py makemigrations
```

5- Initialize the database by loading the first set of data:

```commandline
$ python3 manage.py load_data
```

7- Create a super user for the admin panel in order to view it and manage it:

```commandline
$ python3 manage.py createsuperuser
```

8- Use this command to run the application:

```commandline
$ python3 manage.py runserver
```

Click on the following link for the browser: http://127.0.0.1:8000

A big hoorah!