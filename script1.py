from flask import Flask, render_template, request, Markup
import learn

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    # return render_template("index.html")
    countries, country_name, date, time = learn.get_country()
    da, ti, world_total_confirmed_cases, world_total_confirmed_cases_new, world_total_death, world_total_death_new, world_total_recovered, world_recovered_new, world_total_active, world_total_serious, country_cases, country_total_cases, country_total_death, country_total_recovered, country_recovered_new, country_total_active, country_cases_new, country_death_new, country_total_serious, world_total_predicted_cases, country_total_predicted_cases, fig = learn.covid_processing()
    # x = pd.DataFrame(np.random.randn(20, 5))

    detected_country = country_name
    if request.args.get("select_country") in countries:
        country_name = request.args.get("select_country")
        da, ti, world_total_confirmed_cases, world_total_confirmed_cases_new, world_total_death, world_total_death_new, world_total_recovered, world_recovered_new, world_total_active, world_total_serious, country_cases, country_total_cases, country_total_death, country_total_recovered, country_recovered_new, country_total_active, country_cases_new, country_death_new, country_total_serious, world_total_predicted_cases, country_total_predicted_cases, fig = learn.covid_processing(
            str(country_name))

    countries.remove(country_name)

    iframe = Markup(fig)

    return render_template("index.html", detected_country=detected_country, country=countries,
                           country_name=country_name, date=date, time=time, da=da, ti=ti,
                           world_total_confirmed_cases=world_total_confirmed_cases,
                           world_total_confirmed_cases_new=world_total_confirmed_cases_new,
                           world_total_death=world_total_death, world_total_death_new=world_total_death_new,
                           world_total_recovered=world_total_recovered, world_recovered_new=world_recovered_new,
                           world_total_active=world_total_active,
                           world_total_serious=world_total_serious,
                           country_cases=country_cases, country_total_cases=country_total_cases,
                           country_total_death=country_total_death,
                           country_total_recovered=country_total_recovered, country_recovered_new=country_recovered_new,
                           country_total_active=country_total_active,
                           country_cases_new=country_cases_new, country_death_new=country_death_new,
                           country_total_serious=country_total_serious,
                           world_total_predicted_cases=world_total_predicted_cases,
                           country_total_predicted_cases=country_total_predicted_cases, fig=iframe)
    '''return f"{simplejson.dumps(country_cases)},Name = {country_name}, Total Case = {country_total_cases}, New Case = {country_cases_new}, Total Death = {country_total_death}, New Death = {country_death_new}, Total Active = {country_total_active}"'''


if __name__ == "__main__":
    from waitress import serve

    serve(app)
    app.run(debug=True)
