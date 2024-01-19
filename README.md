# Credit System
A credit approval system based on past data as well as future transactions, using DRF.
## First time run instructions.
1. Pull repo and run <br> docker compose up --build
2. After that, open bash to import data from excel and setup db<br>docker exec -it creditsystem-web-1 bash
3. Run <br>python manage.py makemigrations<br>python manage.py migrate<br>python manage.py ingest_data
4. Restart with command<br>docker compose up --build
5. Server should work, use Postman to test the APIs.

## Video Link
video
