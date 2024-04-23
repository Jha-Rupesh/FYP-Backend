# Vehicle Parking Management System


## Setting Up the Project:
1. Clone this repository to your local machine using `git clone <repo URL>
2. Navigate to the project folder and Open terminal.
3. To setup environment.
```
py -m venv env
.\env\Scripts\Activate.ps1
pip install -r requirements.txt

```
4. To run the project
```
py manage.py makemigrations
py manage.py migrate
py manage.py createsuperuser
py manage.py runserver
```
5. Visit http://localhost:8000/ in your web browser. To see the existing API list.
6. Visit http://localhost:8000/admin in your web browser. To see the django admin page.