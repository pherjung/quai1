# quai1
Bourse d'échange de journées de travail

## How to install
Install python and pip on your computer. Download project:
```
git clone https://github.com/pherjung/quai1

```

### Set up virtual environment:
```
python -m venv env
source env/bin/activate
```

### Install dependencies
```
pip install -r requirements.txt
```

### Migrate Database
```
cd quai1
python manage.py migrate
```

### Run server
```
python manager.py runserver
```
