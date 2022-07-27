from datetime import datetime
import pandas as pd
import numpy as np
import os
import sys

#ignore warnings if any
import warnings
warnings.filterwarnings('ignore')

# Get the current working directory path and append it
path = (os.getcwd()+'\\src\\')
sys.path.append(path)
import import_data

def store_relational_data():
    ''' Transformes the COVID data in a relational data set

    '''
    #Read the .csv file for the total number of covid cases 
    data_path = '../data/raw/COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
    pd_raw = pd.read_csv(data_path)

    #Obtain the per day cases 
    time_idx = pd_raw.columns[4:]
    # Convert the per day cases into a dataframe 
    df_plot = pd.DataFrame({
        'date': time_idx})
    df_input_large = pd_raw['Country/Region'].unique()

    #Browse over each country  and generate the total number of cases 
    for each in df_input_large:
        df_plot[each] = np.array(
            pd_raw[pd_raw['Country/Region'] == each].iloc[:, 4::].sum(axis=0))
    # Drop date from the dataframe        
    df = df_plot.drop('date', axis=1)

    # Merging the data set over COUNTRY for CODE column for worldmap
    df_code = pd.read_csv(
        'https://raw.githubusercontent.com/plotly/datasets/master/2014_world_gdp_with_codes.csv')
    world_raw = pd.DataFrame(
        {"COUNTRY": df_input_large, "Confirm cases": df.iloc[-1]})
    world_con = pd.merge(world_raw, df_code, on="COUNTRY").drop(
        'GDP (BILLIONS)', axis=1)
    world_con.to_csv('../data/processed/COVID_CRD.csv', sep=';', index=False)

    # Continuation of data preparation
    pd_data_base = pd_raw.rename(columns={'Country/Region': 'COUNTRY',
                                          'Province/State': 'state'})

    pd_data_base['state'] = pd_data_base['state'].fillna('no')

    pd_data_base = pd_data_base.drop(['Lat', 'Long'], axis=1)

    pd_relational_model_1 = pd_data_base.set_index(['state', 'COUNTRY']) \
        .T                              \
        .stack(level=[0, 1])             \
        .reset_index()                  \
        .rename(columns={'level_0': 'date',
                         0: 'confirmed'},
                )
    pd_relational_model = pd.merge(
        pd_relational_model_1, df_code, on="COUNTRY").drop('GDP (BILLIONS)', axis=1)
    pd_relational_model['date'] = pd_relational_model.date.astype(
        'datetime64[ns]')

    pd_relational_model.to_csv(
        '../data/processed/20200823_COVID_relational_confirmed.csv', sep=';', index=False)

    # SIR model data preparation
    sir_plot = pd.DataFrame({
        'date': time_idx})
    # sir_plot.head()
    sir_arr = pd_raw['Country/Region'].unique()
    sir_list = sir_arr.tolist()
    for each in sir_list:
        sir_plot[each] = np.array(
            pd_raw[pd_raw['Country/Region'] == each].iloc[:, 4::].sum(axis=0))
    # sir_plot.head()

    # to convert all the dates into datetime
    time_idx = [datetime.strptime(each, "%m/%d/%y") for each in sir_plot.date]
    # to convert datetime function to string
    time_str = [each.strftime('%Y-%m-%d') for each in time_idx]
    # time_str[0:5]

    # Storing the processed data file and sep';' is a seperator [German std]
    sir_plot.to_csv('../data/processed/COVID_sir_flat_table.csv',
                    sep=';', index=False)

    print(' Number of rows stored: '+str(pd_relational_model.shape[0]))
    print(' Latest date is: '+str(max(pd_relational_model.date)))

    # Processing Data for Cases per pop:
    list_cases_country, df_country_info = import_data.import_cases_data()
    json_object_cases = import_data.import_json()

    #Generate an empty dataframe for countries 
    df_country = pd.DataFrame()
    # Browse over the iso codes of each country 
    for each in list_cases_country:
        df_country_info['iso_code'].unique()
        df_country_info['iso_code'] == each
        #Concatenate each country to the empty dataframe and reset indices 
        df_country = pd.concat(
            [df_country, df_country_info[df_country_info['iso_code'] == each]],
            sort=False)
        df_country = df_country.reset_index(drop=True)
    #Obtain the list of country name from dataframe 
    location_list = df_country_info['location'].unique()

    #Define an empty dictionary to append the dates
    dict_country = {}

    # Browse over the country names 
    for each in location_list:
        dict_country.update({
            each:
            len(df_country_info[df_country_info['location'] == each]['date'])
        })
    # Adjust the dataframe to consider from the least starting \
    # date to the most recent ending date for all countries
    country_name_date = max(dict_country, key=lambda x: dict_country[x])
    df_list = df_country_info[df_country_info['location'] ==
                              country_name_date].copy()
    df_list.reset_index(drop=True)
    #Convert the dataframe of dates to datetime 
    df_list['date'] = pd.to_datetime(df_list['date'], format='%Y-%m-%d')
    #Drop irrelevant columns from the dataframe 
    df_list = df_list.drop(df_list.iloc[:, :3], axis=1).drop(df_list.iloc[:, 4:],
                                                             axis=1)
    # Browse over the iso codes of each country 
    for each in list_cases_country:
        df_country_info['iso_code'].unique()
        df_info = df_country_info[df_country_info['iso_code'] == each]

        #Drop irrelevant columns from the dataframe and retain Cases per pop column
        df_data = df_info.drop(df_info.iloc[:, :3], axis=1).drop(
            df_info.iloc[:, 5:],
            axis=1).rename(columns={'total_cases': 'Cases_per_pop_' + each})
        #Obtain the population for each country from the json dictionary 
        pop = json_object_cases[each]['population']
        #Divide by the population to obtain cases per population 
        df_data.iloc[:, 1] = df_data.iloc[:, 1].div(pop, axis=0)
        #Convert date in the date dataframe to datetime format
        df_data['date'] = pd.to_datetime(df_data['date'], format='%Y-%m-%d')
        # join date dateframe wit the cases per pop dataframe 
        df_list = df_list.join(df_data.set_index('date'), on='date')
        # Reset the indices for the entire dataframe 
        df_list = df_list.reset_index(drop=True)
    # Save the generated .csv file in the processed data folder 
    df_list.to_csv('../data/processed/Cases_pop_NoNaN.csv',
                   sep=';', index=False)

    # Procesing Vaccination Data:
    # import vaccinaton data from owid website 
    df_vaccination_info = import_data.import_vacc_data()
    #Create an empty dataframe for vaccination 
    df_vaccination = pd.DataFrame()
    #Browse over the list of country iso codes 
    for each in list_cases_country:
        df_vaccination_info['iso_code'].unique()
        df_vaccination_info['iso_code'] == each
        # Concatenate the vaccination inforamtion to the empty dataframe
        df_vaccination = pd.concat([
            df_vaccination,
            df_vaccination_info[df_vaccination_info['iso_code'] == each]
        ],
            sort=False)
        # Reset indices for the vaccination dataframe 
        df_vaccination = df_vaccination.reset_index(drop=True)
    #Obtain the country names from the vaccination dataframe 
    location_vacc_list = df_vaccination_info['location'].unique()

    #Create an empty dictionary for the vaccination information 
    dict_vacc_country = {}
    # Browse over the list of countries 
    for each in location_vacc_list:
        # Append the country names to the dictionary
        dict_vacc_country.update({
            each:
            len(df_vaccination_info[df_vaccination_info['location'] == each]
                ['date'])
        })

    # Adjust the dataframe to consider from the least starting \
    # date to the most recent ending date for all countries
    country_vacc_name_date = max(dict_vacc_country,
                                 key=lambda x: dict_vacc_country[x])
    df_vacc_list = df_vaccination_info[df_vaccination_info['location'] ==
                                       country_vacc_name_date].copy()
    #Reset the indices for the dataframe
    df_vacc_list.reset_index(drop=True)
    #Convert the dataframe of dates to datetime 
    df_vacc_list['date'] = pd.to_datetime(
        df_vacc_list['date'], format='%Y-%m-%d')

     #Drop irrelevant columns from the dataframe    
    df_vacc_list = df_vacc_list.drop(df_vacc_list.iloc[:, :2],
                                     axis=1).drop(df_vacc_list.iloc[:, 3:], axis=1)
    #Browse over the list of country iso codes 
    for each in list_cases_country:
        df_vaccination_info['iso_code'].unique()
        df_vacc_info = df_vaccination_info[df_vaccination_info['iso_code'] == each]
        #Drop irrelevant columns from the dataframe and retain Vaccination per pop column
        df_vacc_data = df_vacc_info.drop(df_vacc_info.iloc[:, :2], axis=1).drop(
            df_vacc_info.iloc[:, 4:],
            axis=1).rename(columns={'total_vaccinations': 'Vacc_per_pop_' + each})
        #Obtain the population for each country from the json dictionary     
        pop = json_object_cases[each]['population']
        #Divide by the population to obtain vaccination per population 
        df_vacc_data.iloc[:, 1] = df_vacc_data.iloc[:, 1].div(pop, axis=0)
        #Convert date in the date dataframe to datetime format
        df_vacc_data['date'] = pd.to_datetime(df_vacc_data['date'],
                                              format='%Y-%m-%d')
        # join date dateframe wit the cases per pop dataframe 
        df_vacc_list = df_vacc_list.join(
            df_vacc_data.set_index('date'), on='date')
        # Reset the indices for the entire dataframe     
        df_vacc_list = df_vacc_list.reset_index(drop=True)
     # Save the generated .csv file in the processed data folder
    df_vacc_list.to_csv('../data/processed/Vax_per_pop.csv',
                        sep=';', index=False)


if __name__ == '__main__':

    store_relational_data()
