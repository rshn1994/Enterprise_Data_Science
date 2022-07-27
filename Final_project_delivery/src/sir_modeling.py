import numpy as np
import pandas as pd 
from scipy import optimize
from scipy import integrate

import warnings
warnings.filterwarnings('ignore')

df_input_large=pd.read_csv('../data/processed/COVID_sir_flat_table.csv',sep=';').iloc[80:]
pop = pd.read_csv('../data/processed/population.csv',sep=';')

df_all = df_input_large.columns
df_all = list(df_all)

def SIR_model(SIR,beta,gamma):
    ''' Simple SIR model
        S: susceptible population
        I: infected people
        R: recovered people
        beta: 
        
        overall condition is that the sum of changes (differnces) sum up to 0
        dS+dI+dR=0
        S+I+R= N (constant size of population)
    
    '''
    
    S,I,R=SIR
    dS_dt=-beta*S*I/N0          #S*I is the 
    dI_dt=beta*S*I/N0-gamma*I
    dR_dt=gamma*I
    return([dS_dt,dI_dt,dR_dt])


# Functions for SIR model with time step
def SIR_model_t(SIR,t,beta,gamma):
    ''' Simple SIR model
        S: susceptible population
        t: time step, mandatory for integral.odeint
        I: infected people
        R: recovered people
        beta: 
        
        overall condition is that the sum of changes (differnces) sum up to 0
        dS+dI+dR=0
        S+I+R= N (constant size of population)
    
    '''
    
    S,I,R=SIR
    dS_dt=-beta*S*I/N0          #S*I is the 
    dI_dt=beta*S*I/N0-gamma*I
    dR_dt=gamma*I
    return dS_dt,dI_dt,dR_dt


#Function defined for optimize curve fit
def fit_odeint(x, beta, gamma):
    '''
    helper function for the integration
    '''
    return integrate.odeint(SIR_model_t, (S0, I0, R0), t, args=(beta, gamma))[:,1] # we only would like to get dI

#Fitting parameter for SIR model
for each in df_all[1:]:
    ydata = np.array(df_input_large[each])
    t=np.arange(len(ydata))
    N0 = 6000000 #max susceptible population

    # ensure re-initialization 
    I0=ydata[0]
    S0=N0-I0
    R0=0

    popt, pcov = optimize.curve_fit(fit_odeint, t, ydata, maxfev = 1600000)
    perr = np.sqrt(np.diag(pcov))

    # get the final fitted curve
    fitted=fit_odeint(t, *popt).reshape(-1,1)
    df_input_large[each +'_fitted'] = fitted 
    
df_input_large.to_csv('../data/processed/COVID_sir_fitted_table.csv', sep=';')
df_input_large.head()