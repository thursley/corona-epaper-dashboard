import requests
import pandas

def get_vac_quote(state_key):
    # estimated from rki data
    population_th = 2133378
    population_brd = 83190556

    key_state = f"DE-{state_key.upper()}"

    vac_dashboard_url ="https://impfdashboard.de/static/data/germany_vaccinations_by_state.tsv"
    vac_count_path = "vac.tsv"

    response = requests.get(vac_dashboard_url)
    if not response.ok:
        print(f"could not get file at url '{vac_dashboard_url}'. abort.")
        exit(1)

    with open(vac_count_path, 'wb') as f:
        f.write(response.content)

    data = pandas.read_csv(vac_count_path, sep='\t')
    
    if state_key not in ['all', 'brd']:
        for index, row in data.iterrows():
            if row[0] == key_state:
                index_state = index
                break
        
        population = population_th
        first_vac_count = data["peopleFirstTotal"].values[index_state]
    else:
        population = population_brd
        first_vac_count = sum(data["peopleFirstTotal"].values)

    vac_quote = first_vac_count / population
    return vac_quote

if __name__ == "__main__":
    print(f"quote for Thüringen: {(get_vac_quote('th') * 100).round(1)}")
    print(f"quote for Deutschland: {(get_vac_quote('brd') * 100).round(1)}")
