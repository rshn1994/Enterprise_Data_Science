import pandas as pd
import numpy as np
import os
import sys

from datetime import datetime
path=(os.getcwd()+'\\src\\')
sys.path.append(path)

import import_data


def store_relational_data():
    ''' Transformes the COVID data in a relational data set

    '''
    data_path='../data/raw/COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
    pd_raw=pd.read_csv(data_path)

    time_idx = pd_raw.columns[4:]
    df_plot = pd.DataFrame({
        'date':time_idx})
    df_input_large= pd_raw['Country/Region'].unique()
    
    for each in df_input_large:
        df_plot[each] =np.array(pd_raw[pd_raw['Country/Region']==each].iloc[:,4::].sum(axis=0))
    df = df_plot.drop('date', axis=1)
    
    #Merging the data set over COUNTRY for CODE column for worldmap
    df_code = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2014_world_gdp_with_codes.csv')
    world_raw =  pd.DataFrame({"COUNTRY" : df_input_large, "Confirm cases" :df.iloc[-1]})
    world_con = pd.merge(world_raw, df_code, on = "COUNTRY").drop('GDP (BILLIONS)', axis=1)
    world_con.to_csv('../data/processed/COVID_CRD.csv',sep=';',index=False)
    
    #Continuation of data preparation 
    pd_data_base=pd_raw.rename(columns={'Country/Region':'COUNTRY',
                      'Province/State':'state'})

    pd_data_base['state']=pd_data_base['state'].fillna('no')

    pd_data_base=pd_data_base.drop(['Lat','Long'],axis=1)


    pd_relational_model_1=pd_data_base.set_index(['state','COUNTRY']) \
                                .T                              \
                                .stack(level=[0,1])             \
                                .reset_index()                  \
                                .rename(columns={'level_0':'date',
                                                   0:'confirmed'},
                                                  )
    pd_relational_model = pd.merge(pd_relational_model_1, df_code, on = "COUNTRY").drop('GDP (BILLIONS)', axis=1)
    pd_relational_model['date']=pd_relational_model.date.astype('datetime64[ns]')
    
    pd_relational_model.to_csv('../data/processed/20200823_COVID_relational_confirmed.csv',sep=';',index=False)
    
    
    #SIR model data preparation
    sir_plot = pd.DataFrame({
    'date':time_idx})
    #sir_plot.head()
    sir_arr= pd_raw['Country/Region'].unique()
    sir_list = sir_arr.tolist()
    for each in sir_list:
        sir_plot[each] =np.array(pd_raw[pd_raw['Country/Region']==each].iloc[:,4::].sum(axis=0))
    #sir_plot.head()
    
    time_idx = [datetime.strptime(each, "%m/%d/%y") for each in sir_plot.date] #to convert all the dates into datetime 
    time_str= [each.strftime('%Y-%m-%d') for each in time_idx] #to convert datetime function to string
    #time_str[0:5]
    
    #Storing the processed data file and sep';' is a seperator [German std]
    sir_plot.to_csv('../data/processed/COVID_sir_flat_table.csv', sep=';',index=False)
    
    
    print(' Number of rows stored: '+str(pd_relational_model.shape[0]))
    print(' Latest date is: '+str(max(pd_relational_model.date)))

    #Processing Data for Cases per pop:
    list_cases_country,df_country_info=import_data.import_cases_data()
    json_object_cases=import_data.import_json()

    df_country = pd.DataFrame()
    for each in list_cases_country:
        df_country_info['iso_code'].unique()
        df_country_info['iso_code'] == each
        df_country = pd.concat(
            [df_country, df_country_info[df_country_info['iso_code'] == each]],
            sort=False)
        df_country = df_country.reset_index(drop=True)

    location_list = df_country_info['location'].unique()
    dict_country = {}
    for each in location_list:
        dict_country.update({
            each:
            len(df_country_info[df_country_info['location'] == each]['date'])
        })

    country_name_date = max(dict_country, key=lambda x: dict_country[x])
    df_list = df_country_info[df_country_info['location'] ==
                            country_name_date].copy()
    df_list.reset_index(drop=True)
    df_list['date'] = pd.to_datetime(df_list['date'], format='%Y-%m-%d')
    df_list = df_list.drop(df_list.iloc[:, :3], axis=1).drop(df_list.iloc[:, 4:],
                                                            axis=1)


    for each in list_cases_country:
        df_country_info['iso_code'].unique()
        df_info = df_country_info[df_country_info['iso_code'] == each]
        df_data = df_info.drop(df_info.iloc[:, :3], axis=1).drop(
            df_info.iloc[:, 5:],
            axis=1).rename(columns={'total_cases': 'Cases_per_pop_' + each})
        pop = json_object_cases[each]['population']
        df_data.iloc[:, 1] = df_data.iloc[:, 1].div(pop, axis=0)
        df_data['date'] = pd.to_datetime(df_data['date'], format='%Y-%m-%d')
        df_list = df_list.join(df_data.set_index('date'), on='date')
        df_list = df_list.reset_index(drop=True)

    df_list.to_csv('../data/processed/Cases_pop_NoNaN.csv', sep=';', index=False)

    #Procesing Vaccination Data:
    
    df_vaccination_info=import_data.import_vacc_data()
    df_vaccination = pd.DataFrame()
    for each in list_cases_country:
        df_vaccination_info['iso_code'].unique()
        df_vaccination_info['iso_code'] == each
        df_vaccination = pd.concat([
            df_vaccination,
            df_vaccination_info[df_vaccination_info['iso_code'] == each]
        ],
                                sort=False)
        df_vaccination = df_vaccination.reset_index(drop=True)


    location_vacc_list = df_vaccination_info['location'].unique()
    dict_vacc_country = {}
    for each in location_vacc_list:
        dict_vacc_country.update({
            each:
            len(df_vaccination_info[df_vaccination_info['location'] == each]
                ['date'])
        })

    country_vacc_name_date = max(dict_vacc_country,
                                key=lambda x: dict_vacc_country[x])
    df_vacc_list = df_vaccination_info[df_vaccination_info['location'] ==
                                    country_vacc_name_date].copy()
    df_vacc_list.reset_index(drop=True)
    df_vacc_list['date'] = pd.to_datetime(df_vacc_list['date'], format='%Y-%m-%d')
    df_vacc_list = df_vacc_list.drop(df_vacc_list.iloc[:, :2],
                                    axis=1).drop(df_vacc_list.iloc[:, 3:], axis=1)

    # # load json object for the total number of COVID cases
    # data_cases = requests.get('https://covid.ourworldindata.org/data/owid-covid-data.json')
    # json_object_cases=json.loads(data_cases.content)

    for each in list_cases_country:
        df_vaccination_info['iso_code'].unique()
        df_vacc_info = df_vaccination_info[df_vaccination_info['iso_code'] == each]
        df_vacc_data = df_vacc_info.drop(df_vacc_info.iloc[:, :2], axis=1).drop(
            df_vacc_info.iloc[:, 4:],
            axis=1).rename(columns={'total_vaccinations': 'Vacc_per_pop_' + each})
        pop = json_object_cases[each]['population']
        df_vacc_data.iloc[:, 1] = df_vacc_data.iloc[:, 1].div(pop, axis=0)
        df_vacc_data['date'] = pd.to_datetime(df_vacc_data['date'],
                                            format='%Y-%m-%d')
        df_vacc_list = df_vacc_list.join(df_vacc_data.set_index('date'), on='date')
        df_vacc_list = df_vacc_list.reset_index(drop=True)


    df_vacc_list.to_csv('../data/processed/Vax_per_pop.csv', sep=';', index=False)



if __name__ == '__main__':

    store_relational_data()