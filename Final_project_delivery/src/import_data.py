import subprocess
import os
import requests
import json
import pandas as pd
from datetime import datetime

def import_json():
    data_cases = requests.get('https://covid.ourworldindata.org/data/owid-covid-data.json')
    json_object_cases=json.loads(data_cases.content)

    return json_object_cases


def import_cases_data():
    ''' Get data by a git pull request, the source code has to be pulled first
        Result is stored in the predifined csv structure. If there is no Repository 
        not present then clone the data from GitHub.
    '''
    
    if os.path.exists('../data/raw/COVID-19/'):
        print('Repository Exists: Fetch the latest data from repository')
        git_pull = subprocess.Popen( "git pull" ,
                             cwd = os.path.dirname('../data/raw/COVID-19/' ),
                             shell = True,
                             stdout = subprocess.PIPE,
                             stderr = subprocess.PIPE )
        (out, error) = git_pull.communicate()
    else:
        print('Repository not present. Fetch the entire repository')
        git_clone = subprocess.Popen( "git clone https://github.com/CSSEGISandData/COVID-19.git" ,
                             cwd = os.path.dirname('../data/raw/' ),
                             shell = True,
                             stdout = subprocess.PIPE,
                             stderr = subprocess.PIPE )
        (out, error) = git_clone.communicate()


    url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"
    df_country_info = pd.read_csv(url, sep=',')


    
    # load json object for the total number of COVID cases
    json_object_cases=import_json()

    countries_list = list(json_object_cases.keys())
    country_remove=['OWID_INT','OWID_CYN']
    list_cases_country=list(set(countries_list) - set(country_remove))

    return list_cases_country, df_country_info

def import_vacc_data():
    ''' Get data by a git pull request, the source code has to be pulled first
        Result is stored in the predifined csv structure. If there is no Repository 
        not present then clone the data from GitHub.
    '''
    
    # Requesting the Vacination data from our world in data:
    url_vaccination = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv'

    #Dumping all data from json into a variable:
    df_vaccination_info = pd.read_csv(url_vaccination, sep=',')

    return df_vaccination_info


if __name__ == '__main__':
    import_json()
    import_cases_data()
    import_vacc_data()
    