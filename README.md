<div align="center">

# BreakFree
This is a habit tracker api project that i converted from a djago project. So, what you do is, create rooms that you and your friends can see and than you can start the counter and leaderboard is there to show who has the longest streak. 
</div>

### Cloning the repository

--> Clone the repository using the command below :
```bash
git clone https://github.com/rajatbhai980/breakfree-api-.git

```

--> Move into the directory where we have the project files : 
```bash
cd breakfree-api

```

--> Create a virtual environment :
```bash
# Let's install virtualenv first
pip install virtualenv

# Then we create our virtual environment
virtualenv env

```

--> Activate the virtual environment(You need to activate the virtual environment each time you restart the pc) :
```bash
env\scripts\activate

```
 
 --> Install the pip install -r requirements.txt 

 --> create .env.local and paste the following (add your own secret key)
 ```bash
DEBUG = False
SECRET_KEY = 'your secret key'
ALLOWED_HOSTS = localhost,127.0.0.1,.railway.app 
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000

DATABASE_ENGINE='django.db.backends.sqlite3'
DB_PATH=db.sqlite3

```


#

### Running the App

--> To run the App, we use :
```bash
python manage.py runserver

```

> ⚠ Then, the development server will be started at http://127.0.0.1:8000/

#
