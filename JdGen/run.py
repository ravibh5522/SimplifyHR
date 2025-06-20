# ai_hr_jd_project/run.py
from app import create_app

app = create_app()
if __name__ == '__main__':
    # When running locally for development, Flask's dev server is fine.
    # For production, use a WSGI server like Gunicorn.
    # Gunicorn command for Cloud Run: gunicorn --bind :$PORT app:app
    app.run(host='0.0.0.0', port=8085, debug=True, use_reloader=False, threaded=True)
