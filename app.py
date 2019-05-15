# -*- coding: utf-8 -*-
"""
Data 608 Final Project

Created on Mon May 13 11:50:01 2019

@author: Iden
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
# import dash_table
from math import log10
from textwrap import dedent
from statistics import mean, median

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
# app.config['suppress_callback_exceptions'] = True


# Import data
cong = pd.read_excel("congestion.xls")
# fuel = pd.read_excel("fuel.xls")
energy = pd.read_excel("Monthly_Energy_Data.xlsx", sheet_name = "State")
regi = pd.read_excel("motor_vehicle_registration.xls")
pop = pd.read_excel("pop_by_county.xls")
public = pd.read_excel("public_transit.xls")
# length = pd.read_excel("street_length.xls")

# energy is too granular (monthly)
# Convert to annual average
total = 0
year = 2006
place = 162
for x in range(12):
    energy[year] = ""
    year += 1

for x in range(0, 13):
    place = 162
    for y in range(2, 145):
        if y % 12 == 0:
            total += energy.iloc[x, y]
            energy.iloc[x, place] = total/12
            total = 0
            place += 1
        else:
            total += energy.iloc[x, y]
            
energy = energy.drop(energy.index[[0, 1, 2, 3, 4, 5, 6, 7]])
vehicle_type = energy[['Subject', 2014, 2015, 2016, 2017]]

# Clean up the rest of the dataframes
reg_final = regi[['Subject', 2014, 2015, 2016, 2017]]
reg_final.iat[0, 0] = "State Registration"
reg_final.iat[1, 0] = "Honolulu Registration"
reg_final.iat[2, 0] = "Big Island Registration"
reg_final.iat[3, 0] = "Kauai Registration"
reg_final.iat[4, 0] = "Maui Registration"

pop_final = pop[['Subject', 2014, 2015, 2016, 2017]]
pop_final.iat[0, 0] = "State Population"
pop_final.iat[1, 0] = "Honolulu Population"
pop_final.iat[2, 0] = "Big Island Population"
pop_final.iat[3, 0] = "Kauai Population"
pop_final.iat[4, 0] = "Maui Population"

pub_final = public[['Subject', 2014, 2015, 2016, 2017]]
pub_final.iat[3, 0] = "Bus Revenue (dollars)"

data = vehicle_type
data = data.append(reg_final)
data = data.append(pop_final)
data = data.append(pub_final)
data = data.append(cong)

# Dropdown Indicators
data_ind = data['Subject'].unique()

def getTable():
    d1 = data.loc[data.Subject == "State Registration"].values.tolist()[0][1:5]
    d2 = data.loc[data.Subject == "State Population"].values.tolist()[0][1:5]
    
    mean1 = mean(d1)
    mean2 = mean(d2)
    
    median1 = median(d1)
    median2 = median(d2)
    
    temp = {'Category': ["State Registration", "State Population"],
            'Mean': [mean1, mean2],
            'Median': [median1, median2]}
    df = pd.DataFrame(data = temp)
    return df
    
info = getTable()

def generate_table(df, max_rows = 4):
    return html.Table(
            [html.Tr([html.Th(col) for col in df.columns])] +
            [html.Tr([
                    html.Td(df.iloc[i][col]) for col in df.columns
                    ]) for i in range(min(len(df), max_rows))]
            )

#App Design
app.layout = html.Div(children = [
        html.H1(
                children = "Final Project"
                ),

        html.Div([
                dcc.Markdown(dedent('''
                        #### Instructions
                        
                        Select two categories below to compare statistics regarding vehicles in the state of Hawaii.
                        '''))
                ]),                              
        
        html.Div([
                html.Label('Categories'),
                dcc.Dropdown(
                        id = 'Subjects',
                        options = [{'label':i, 'value':i} for i in data_ind],
                        value = ["State Registration", "State Population"],
                        multi = True
                        )
                ]),
                
        dcc.Graph(id = 'indicator-graphic'),
        
        html.Div(id = "table", children = [
                generate_table(info)]),
])
                
@app.callback(
        [Output('indicator-graphic', 'figure'),
         Output('table', 'children')],
        [Input('Subjects', 'value')])
def update_graph(val):
    d1 = data.loc[data.Subject == val[0]].values.tolist()[0][1:5]
    d2 = data.loc[data.Subject == val[1]].values.tolist()[0][1:5]
    
    mean1 = mean(d1)
    mean2 = mean(d2)
    
    median1 = median(d1)
    median2 = median(d2)
    
    temp = {'Category': [val[0], val[1]],
            'Mean': [mean1, mean2],
            'Median': [median1, median2]}
    
    df = pd.DataFrame(data = temp)
    
    trace0 = go.Bar(
            x = [2014, 2015, 2016, 2017],
            y = d1,
            name = val[0]
            )
    
    trace1 = go.Bar(
            x = [2014, 2015, 2016, 2017],
            y = d2,
            name = val[1]
            )
    
    figure = go.Figure(
                data = [trace0, trace1],
                layout = go.Layout(xaxis = {'title': 'Years'})
            )
    
    return figure, generate_table(df)
  
if __name__ == '__main__':
    app.run_server(debug=True)
