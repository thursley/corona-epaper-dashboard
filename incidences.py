import pandas
import requests

def get_7days_incidence():
    url = "https://opendata.jena.de/dataset/2cc7773d-beba-43ad-9808-a420a67ffcb3/resource/d3ba07b6-fb19-451b-b902-5b18d8e8cbad/download/corona_erkrankungen_jena.csv"
    inc_path = 'inc.csv'

    response = requests.get(url)
    if not response.ok:
        print("unable to get csv from server. abort.")
        exit(1)

    with open(inc_path, 'wb') as f:
        f.write(response.content)

    dataframe = pandas.read_csv(inc_path)
    print([sum(dataframe.neu_erkrankte[i-6:i+1])/1.11434 for i in range(6, len(dataframe.zeit))])


