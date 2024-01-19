#!/bin/sh

python manage.py test CreditApp.tests.test_serializers CreditApp.tests.test_views CreditApp.tests.test_models


if [ $? -eq 0 ]; then
    python manage.py runserver 0.0.0.0:8000
else
    echo "Django tests failed. Exiting."
fi