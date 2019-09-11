# FBP crawler
FBP crawler is a web spider for facebook, written in [Scrapy](https://scrapy.org/) framework without using Splash / Selenium. 
Currently, support only 
Facebook Page. Given a page id, It's can extract all the posts, images url, reaction count, comment count and so on.

## DISCLAIMER
This script is not authorized by Facebook. For commercial used please contact [Facebook](https://facebook.comorg/).

The purpose of this script is for **educational**, to demonstrate how Scrapy can be written to extract page without using Splash or Selenium.
Use it at your own risk.

## Installation

It's recommended to install inside an isolate environment. In this case, I had provided `envrionment.yml` 
that can be used by `conda`

`conda env create -f environment.yml`

Feel free to change environment name in `environment.yml`. Default is `fb-crawler`

`source activate fb-crawler`

## Usage

Active scrapy project by go into a directory `facebook_crawler`

`cd facebook_crawler`

In order to run a spider, you need a **page_id**, **username** and **password**.

**page_id** - can be found in the page url. 
For example https://www.facebook.com/ejeab **page_id** is `ejeab` https://www.facebook.com/Viciousant/ **page_id** is `Viciousant`

**username** - your email address that used to login

**password** - your password that used to login 

Example command to run spider and store results as the json file
```
scrapy crawl fb_page \
-a username="your_email@email.com" \
-a password="your_password" \
-a page_id="page_id_you_want_scrape" \
-o output.json
```

Store as csv file
```
scrapy crawl fb_page \
-a username="your_email@email.com" \
-a password="your_password" \
-a page_id="page_id_you_want_scrape" \
-o output.csv
```

Multiple pages scraping. Use comma as separation `,`
```
scrapy crawl fb_page \
-a username="your_email@email.com" \
-a password="yourpassword" \
-a page_id="ejeab,Viciousant" \
-o output.csv
```

## Store in database

Currently it support for Postgres database, will provide more in the future.

For less headache about database installation, I decided to use `docker-compose`.

In `docker-compose.yml` file. It's contain 2 services. Postgres database and Pgadmin4 (web app for database).

Feel free to change username, password, port for both services. 
Or you can set a username, password by using environment variable

`POSTGRES_USER` default is `postgres`

`POSTGRES_PASSWORD` default is `password`

`PGADMIN_DEFAULT_EMAIL` default is `pgadmin4`

`PGADMIN_DEFAULT_PASSWORD` default is `admin`

- Running a services `docker-compose up`. Access Postgres by `localhost:5432` and Pgadmin4 by `localhost:5555`.

- Now you can create a database by using SQL command or login to Pgadmin4 and create database manually.

Example database name from now on is **fb_page**

- Then you can create a tables. I had provided `create_sql_table.py`
```
python create_sql_table.py \
-a user="postgres" \ 
-a password="password" \
-a host="localhost" \
-a port="5432" \
-a database="fb_page"
```

- At the end of `settings.py`, Please uncomment and provide your database settings
```
DB_SETTINGS = {
    'db': 'fb_page',
    'user': 'postgres',
    'password': 'password',
    'host': 'localhost',
    'port': '5432'
}
``` 

- That is. you can now run a spider with `-a database=true` argument.
```
scrapy crawl fb_page \
-a username="your_email@email.com" \
-a password="yourpassword" \
-a page_id="page_id_you_want_to_scrape" \
-a database=true
```

## TODO

- More on documentation / Readme.md
- Better comments parsing / Fetch all comments
- Fixing bugs as I didn't had a decent testing yet.
