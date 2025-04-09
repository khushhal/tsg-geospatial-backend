# Turl Street Group Assignment - Backend

This is the backend Django project for the Turl Street Group Assignment. It uses Docker, PostGIS, Redis, and Celery to process geospatial and census data efficiently.

---

## 🚀 Getting Started

Follow the steps below to set up the project from scratch:

### 1. 📥 Clone the Repository

```bash
git clone https://github.com/your-username/turl_street_group_assignment.git
cd turl_street_group_assignment
```
### 2. 🛠️ Create and Configure Your Environment

Make sure you create a new .env file by copying from .env.example:

```bash
cp .env.example .env
```
Then, edit the .env file and make sure to update the following:
```bash
CENSUS_API_KEY=your_api_key_here
```
To get a new Census API key, visit:
👉 https://api.census.gov/data/key_signup.html

Make sure you created new file .env and copied the content from .env.example and also update this
CENSUS_API_KEY to get the new api key go to this url

### 3. 📦 Download Required Geospatial Data
Download the shapefile data from the following Google Drive link:

👉 [Download Data Folder](https://drive.google.com/drive/folders/14krFfDOzba53SzEgsCyXrSHO1PBlbVKW?usp=drive_link)

Once downloaded:

Create a new folder named data in the project root.

Move the downloaded contents into this data folder

```bash
mkdir data
# Move downloaded files into this folder
```

### 4. 🐳 Start Docker Compose
```bash
docker compose up --build
```
This command will:

Set up the PostgreSQL with PostGIS

Launch Redis

Start the Django server

Start the Celery worker

Make sure Docker is running before executing the above.

## 📌 Initial Setup Commands
Once your containers are running, you need to populate your database.

### 1. 🔄 Import Geospatial Data
This will pull city, state, MSA, and county data from the shapefiles in the data/ folder and store it in the database.
```bash
docker compose run web python manage.py run_geoprocessing_tasks
```

### 2. 🧠 Scrape Census Data
Next, open an interactive shell and run the census scraping tasks manually:
```bash
docker compose run web python manage.py shell_plus
```
Once inside the shell, run:
```bash
from census.tasks import *

scrape_census_data_for_states_task()
scrape_census_data_for_counties_task()
scrape_census_data_for_cities_task()
```

⚠️ Note: These tasks pull data from an external census source which sometimes may not return data for all records.
It's recommended to run these tasks multiple times if you find records missing. This is expected due to ~5% failure rate from the source API.

### ✅ After That...
Your backend setup is complete 🎉

You can now open the frontend and start using the application!

## 📬 Questions?
Feel free to raise an issue or reach out to the maintainer.

