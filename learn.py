import functools
from flask_caching import Cache

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from covid import Covid
from datetime import datetime
import plotly.express as px
from requests.exceptions import ConnectionError
import requests
import urllib.request
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import sqdb
from sqdb import con, con2

cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})


def get_country(c="india"):
    ### Geting Location ###
    ext_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
    ip = requests.get('https://api64.ipify.org').text
    ip_url = f"https://reallyfreegeoip.org/json/{ip}"
    r = requests.get(ip_url)
    ip_details = r.json()
    if c:
        county_name = c
    else:
        county_name = "india"
    ### Date Time ###
    dt = datetime.now()
    dates = dt.date()
    times = dt.time()
    date = dates.strftime("%Y-%m-%d")
    time = times.strftime('%I:%M %p')

    ### Getting worldometer data ###
    covid_data = Covid(source="worldometers")

    # Processing Countries Start
    countries = covid_data.list_countries()
    country = pd.DataFrame(countries, columns=["country"])
    return countries, county_name, date, time, covid_data


countries, country_name, date, time, covid_data = get_country()


def covid_processing(country_name=country_name):
    '''def extra_data():
        url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
        # url = "owid-covid-data.csv"
        db = pd.read_csv(url)
        return db

    db = extra_data()'''

    dtdb, db = sqdb.in_date(date, time)
    world = db[db["location"] == "World"]
    country = db[db["location"] == country_name.capitalize()]
    world_total = world[["location", "date", "total_cases", "total_deaths"]]
    country_total = country[["location", "date", "total_cases", "total_deaths"]]
    world_total = pd.DataFrame(world_total)
    world_total.insert(0, 'id', range(0, 0 + len(world_total)))
    country_total = pd.DataFrame(country_total)
    country_total.insert(0, 'id', range(0, 0 + len(country_total)))
    last_date = world_total.tail(1)
    last_cases = int(last_date["total_cases"])
    last_death = int(last_date["total_deaths"])

    ### Getting All Datas ###
    world_total_confirmed_cases = covid_data.get_total_confirmed_cases()
    world_total_confirmed_cases_new = world_total_confirmed_cases - last_cases
    world_total_death = covid_data.get_total_deaths()
    world_total_death_new = world_total_death - last_death
    world_total_recovered = covid_data.get_total_recovered()
    world_total_active = covid_data.get_total_active_cases()
    world_total_serious = covid_data.get_status_by_country_name('world')['critical']

    country_cases = covid_data.get_status_by_country_name(country_name)
    country_total_cases = country_cases['confirmed']
    country_total_death = country_cases['deaths']
    country_total_recovered = country_cases['recovered']
    country_total_active = country_cases['active']
    country_cases_new = country_cases['new_cases']
    country_death_new = country_cases['new_deaths']
    country_total_serious = country_cases['critical']

    ### Figure Making ###
    world_country = [world_total, country_total]
    world_country = pd.concat(world_country)
    fig = px.line(world_country, x="date", y="total_cases", title=f'Total Cases Compare Between World and {country_name}', color='location')
    fig = fig.to_html(fig, full_html=False)


    return world_total_confirmed_cases, world_total_confirmed_cases_new, world_total_death, world_total_death_new, world_total_recovered, world_total_active, world_total_serious, country_cases, country_total_cases, country_total_death, country_total_recovered, country_total_active, country_cases_new, country_death_new, country_total_serious, fig


'''world_total_confirmed_cases, world_total_confirmed_cases_new, world_total_death, world_total_death_new, world_total_recovered, world_total_active, world_total_serious, country_cases, country_total_cases, country_total_death, country_total_recovered, country_total_active, country_cases_new, country_death_new, country_total_serious, fig = covid_processing()

print(fig)'''
