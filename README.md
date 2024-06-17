# HealthMate: Online Doctor Consultation
### [Try Here](https://healthmate.pythonanywhere.com/)

HealthMate is an online platform designed to facilitate seamless doctor consultations and healthcare management. It offers a range of services including appointment booking, online consultations, home sample collection, and medical records management. HealthMate aims to provide personalized and convenient healthcare solutions at your fingertips.

## Features

- User Authentication: Register, login, and manage your account.
- Appointment Booking: Schedule appointments with doctors online.
- Online Consultations: Consult with doctors through online sessions.
- Home Sample Collection: Book home sample collection for lab tests.
- Medical Records Management: Manage and access your medical records easily.
- Secure and User-Friendly: Ensures user data privacy and offers a simple interface.
- Admin Dashboard: Manage doctors, specialities, reviews and lab tests through the admin panel.

## Installation

1. Clone the repository:
```
git clone https://github.com/abhishek800449/healthmate.git
```

2. Create a python virtual environment to install dependencies:
```
python -m venv env
```

3. Activate the envrionment according to your machine type:
   
  - (Windows) `env\Scripts\activate`
  - (Mac/Linux) `source bin/activate`

4. Install dependencies:
```
pip install -r requirements.txt
```

5. Create a `.env` file in the project root and configure your environment variables given in `.env-sample` file.

6. Apply migrations:
```
python manage.py migrate
```

7. Create a superuser account:
```
python manage.py createsuperuser
```

8. Run the development server:
```
python manage.py runserver
```

The application will be accessible at ```http://localhost:8000/```.