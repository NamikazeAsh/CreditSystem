#!/bin/sh

# Run Django tests
python manage.py test CreditApp.tests.test_serializers CreditApp.tests.test_views CreditApp.tests.test_models

# Check the exit status of the tests
if [ $? -eq 0 ]; then
    # If tests pass, start Django server
    python manage.py runserver 0.0.0.0:8000
else
    echo "Django tests failed. Exiting."
fi