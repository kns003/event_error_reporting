# event_error_reporting
django admin event and alert reporting.

1. Clone the repo.

2. `pip install -r requirements.txt`

4. `python manage.py migrate`

3. Event tracker
    - Know all the events occuring in django admin with the fields intial and final values.
    - For the admin apps for which you need to track the events, import `LogCustomModelAdmin`
    - usage:
        - `from token_app.models import LogCustomModelAdmin`
        - `class YourModelAdmin(LogCustomModelAdmin)`
    - You can track all your events in `CustomLogEntry Admin`
    
4. Error Reporting.

    - Any exception which occurs in the Dajngo Admin are tracked in `ErrorReporting Admin`
    
    Demo Video - https://www.youtube.com/watch?v=TxplhoEDS9E
