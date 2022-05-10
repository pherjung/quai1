# quai1
Bourse d'échange de journées de travail

## How to install
Install python3 and pip on your computer. Download project:
```
git clone https://github.com/pherjung/quai1

```

### Set up virtual environment:
```
python3 -m venv env
source env/bin/activate
```

### Install dependencies
```
pip install -r requirements.txt
```

### Migrate Database
```
cd src
python3 manage.py makemigrations
python3 manage.py migrate
```

### Run server
```
python3 manage.py runserver
```
