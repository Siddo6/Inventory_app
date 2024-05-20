set -o errexit
pip install -r requirements.txt
python manage.y collectstatic --no-input
python manage.py migrate