import pandas as pd
import numpy as np
import geocoder
from covid import Covid
from datetime import datetime
import plotly.express as px
import requests
from bs4 import BeautifulSoup
import urllib.request
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import sqdb
from sqdb import con


def get_country(c="bangladesh"):
    ### Geting Location ###
    # ext_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
    ip = requests.get('https://api64.ipify.org').text
    # ip = geocoder.ip("me")
    # ip = ip.ip
    ip_url = f"https://reallyfreegeoip.org/json/{ip}"
    r = requests.get(ip_url)
    ip_details = r.json()
    if c:
        county_name = c
    else:
        county_name = "bangladesh"
        # county_name = ip_details["country_name"].lower()
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
    countries.remove("world")
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

    da = dtdb["datee"].values
    ti = dtdb["timee"].values

    ### Web Scraping ###
    full_page = requests.get("https://www.worldometers.info/coronavirus/")
    full_page = full_page.content
    soup = BeautifulSoup(full_page, "html.parser")
    ### Scrapping World Data ###
    world_o = soup.find_all("tr", {"class": "total_row_world"})[7]
    world_recovered_new = world_o.find_all("td")[7].text[1:].replace(',', '')
    if world_recovered_new == "":
        world_recovered_new = 0
    else:
        world_recovered_new = int(world_o.find_all("td")[7].text[1:].replace(',', ''))
    ### Scrapping Country Data ###
    country_o = soup.find_all("table", {"class": "table-hover"})[0]
    country_o = (country_o.find_all("tr"))
    counter = 0
    empty_dataframe = []
    for n in country_o:
        if n.find(["nobr", "a", "span"]) != None:
            empty_dataframe.append([counter, (n.find(["nobr", "a", "span"]).text).upper()])
        counter += 1
    c_scapped = pd.DataFrame(empty_dataframe)
    c_scapped.columns = ["C_ID", "C_Name"]
    C_ID_Selected = int(c_scapped[c_scapped["C_Name"] == country_name.upper()]["C_ID"])
    country_recovered_new = country_o[C_ID_Selected].find_all("td")[7].text.replace("+", "").replace(",", "")
    if country_recovered_new == "":
        country_recovered_new = 0
    else:
        country_recovered_new = int(country_o[C_ID_Selected].find_all("td")[7].text.replace("+", "").replace(",", ""))

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
    world_total_confirmed_cases = int(world_o.find_all("td")[2].text[:].replace(',', ''))
    world_total_confirmed_cases_new = int(world_o.find_all("td")[3].text[1:].replace(',', ''))
    world_total_death = covid_data.get_total_deaths()
    world_total_death_new = world_total_death - last_death
    world_total_recovered = covid_data.get_total_recovered()
    world_recovered_new = world_recovered_new
    world_total_active = covid_data.get_total_active_cases()
    world_total_serious = covid_data.get_status_by_country_name('world')['critical']

    country_cases = covid_data.get_status_by_country_name(country_name)
    country_total_cases = country_cases['confirmed']
    country_total_death = country_cases['deaths']
    country_total_recovered = country_cases['recovered']
    country_recovered_new = country_recovered_new
    country_total_active = country_cases['active']
    country_cases_new = country_cases['new_cases']
    country_death_new = country_cases['new_deaths']
    country_total_serious = country_cases['critical']

    ### Machine Learning ###
    ### World Prediction ###
    world_total_m = world[["location", "date", "total_cases", "total_deaths", "new_cases"]]
    world_total_m.loc[len(world_total_m.index)] = ["World", "", world_total_confirmed_cases, world_total_death,
                                                   world_total_confirmed_cases_new]
    world_total_m = pd.DataFrame(world_total_m)
    world_total_m.insert(0, 'id', range(0, 0 + len(world_total_m)))
    world_total_m = world_total_m.fillna(0)
    world_total_m = world_total_m.tail(30)
    x_world = np.array(world_total_m["id"]).reshape(-1, 1)
    y_world = np.array(world_total_m["total_cases"]).reshape(-1, 1)
    poly_world = PolynomialFeatures(degree=2)
    x_world = poly_world.fit_transform(x_world)
    reg = LinearRegression()
    reg.fit(x_world, y_world)
    accuracy_world = reg.score(x_world, y_world)
    predict_world = reg.predict(x_world)
    wc = int(world_total_m.tail(1)["id"])+1
    world_total_predicted_cases = int(reg.predict(poly_world.fit_transform([[wc]])))

    ### Country Prediction ###
    country_total_m = country[["location", "date", "total_cases", "total_deaths", "new_cases"]]
    country_total_m.loc[len(country_total_m.index)] = [country_name, "", country_total_cases, country_total_death,
                                                       country_cases_new]
    country_total_m = pd.DataFrame(country_total_m)
    country_total_m.insert(0, 'id', range(0, 0 + len(country_total_m)))
    country_total_m = country_total_m.fillna(0)
    country_total_m = country_total_m.tail(30)
    x_country = np.array(country_total_m["id"]).reshape(-1, 1)
    y_country = np.array(country_total_m["new_cases"]).reshape(-1, 1)
    poly_country = PolynomialFeatures(degree=3)
    x_country = poly_country.fit_transform(x_country)
    reg_c = LinearRegression()
    reg_c.fit(x_country, y_country)
    accuracy_country = reg_c.score(x_country, y_country)
    predict_country = reg_c.predict(x_country)
    cc = int(country_total_m.tail(1)["id"])+1
    country_total_predicted_cases = int(reg_c.predict(poly_country.fit_transform([[cc]])))

    ### Figure Making ###
    world_country = [world_total, country_total]
    world_country = pd.concat(world_country)
    fig = px.line(world_country, x="date", y="total_cases",
                  title=f'Total Cases Compare Between World and {country_name}', color='location')
    fig = fig.to_html(fig, full_html=False)

    return da, ti, world_total_confirmed_cases, world_total_confirmed_cases_new, world_total_death, world_total_death_new, world_total_recovered, world_recovered_new, world_total_active, world_total_serious, country_cases, country_total_cases, country_total_death, country_total_recovered, country_recovered_new, country_total_active, country_cases_new, country_death_new, country_total_serious, world_total_predicted_cases, country_total_predicted_cases, fig


'''da, ti, world_total_confirmed_cases, world_total_confirmed_cases_new, world_total_death, world_total_death_new, world_total_recovered, world_recovered_new, world_total_active, world_total_serious, country_cases, country_total_cases, country_total_death, country_total_recovered, country_recovered_new, country_total_active, country_cases_new, country_death_new, country_total_serious, world_total_predicted_cases, country_total_predicted_cases, fig = covid_processing()

print(world_total_predicted_cases, country_total_predicted_cases)'''
