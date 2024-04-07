## Market Statistics
A Django for back-end and React for front-end web project built to aid investors/traders in:
* Tracking the performance of various investment products.
* Tracking economics conditions with respect to investment product values using various statistical techniquess.
* Setting up a customized dashboard of analysis metrics.

### Technology
* Python 3.12
* Django 5
* ReactJS 18
* Vite 5
* Bootstrap 5

### Installation
Please create a new virtual environment and install all Python dependencies using the requirements.txt file in the root directory using:
```
python -m pip install -r requirements.txt
```
Next, refer to the file frontend/package.json to see all ReactJS dependencies and run:
```
npm install
```
to collect the required packages to run the project.

### Launch
You'd need to run two local servers on different ports, one for the back-end (port 8000 for Django), and the other for the front-end (port 3000 for ReactJS).
To run back-end server, activate the virtual environment, redirect to the folder where you've cloned the project and run:
```
python manage.py runserver
```
Then boot up the front-end server by first redirecting to the frontend folder, then type in the command line:
```
npm run dev
```

Note: In case you want to change the port of the front-end server, please change the CORS_ALLOWED_ORIGIN in marketstats/settings.py to:
```
CORS_ALLOWED_ORIGIN = ["http://localhost:port_number"]
```
