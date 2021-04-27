from flask import Flask, render_template, jsonify, request, Markup
import pandas as pd
import numpy as np
import learn
import json
import decimal
import simplejson

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    # return render_template("index.html")
    countries, country_name, date, time, covid_data = learn.get_country()
    world_total_confirmed_cases, world_total_confirmed_cases_new, world_total_death, world_total_death_new, world_total_recovered, world_total_active, world_total_serious, country_cases, country_total_cases, country_total_death, country_total_recovered, country_total_active, country_cases_new, country_death_new, country_total_serious, fig = learn.covid_processing()
    # x = pd.DataFrame(np.random.randn(20, 5))

    detected_country = country_name
    if request.args.get("select_country") in countries:
        country_name = request.args.get("select_country")
        world_total_confirmed_cases, world_total_confirmed_cases_new, world_total_death, world_total_death_new, world_total_recovered, world_total_active, world_total_serious, country_cases, country_total_cases, country_total_death, country_total_recovered, country_total_active, country_cases_new, country_death_new, country_total_serious, fig = learn.covid_processing(str(country_name))

    countries.remove(country_name.lower())

    iframe = Markup(fig)

    return render_template("index.html", detected_country=detected_country, country=countries,
                           country_name=country_name, date=date, time=time,
                           world_total_confirmed_cases=world_total_confirmed_cases,
                           world_total_confirmed_cases_new=world_total_confirmed_cases_new,
                           world_total_death=world_total_death, world_total_death_new=world_total_death_new,
                           world_total_recovered=world_total_recovered, world_total_active=world_total_active,
                           world_total_serious=world_total_serious,
                           country_cases=country_cases, country_total_cases=country_total_cases,
                           country_total_death=country_total_death,
                           country_total_recovered=country_total_recovered, country_total_active=country_total_active,
                           country_cases_new=country_cases_new, country_death_new=country_death_new,
                           country_total_serious=country_total_serious, fig=iframe)
    '''return f"{simplejson.dumps(country_cases)},Name = {country_name}, Total Case = {country_total_cases}, New Case = {country_cases_new}, Total Death = {country_total_death}, New Death = {country_death_new}, Total Active = {country_total_active}"'''


if __name__ == "__main__":
    app.run(debug=True)
