import pandas as pd
pd.set_option('display.float_format', lambda x: '%.6f' % x)
import dash
from dash import dcc
from dash import html
import plotly.graph_objects as go

# Data Preprocessing

# open dataset
eu_data = pd.read_excel('data/eu_data.xlsx')

# create new features
eu_data['NonRenewable energy consumption (TJ) 2015'] = eu_data['Total final energy consumption (TFEC) (TJ) 2015'] - eu_data['Renewable energy consumption (TJ) 2015']
eu_data['NonRenewable energy consumption (%) 2015'] = eu_data['NonRenewable energy consumption (TJ) 2015']/eu_data['Total final energy consumption (TFEC) (TJ) 2015']
eu_data['Renewable energy consumption (%) 2015'] = eu_data['Renewable energy consumption (TJ) 2015']/eu_data['Total final energy consumption (TFEC) (TJ) 2015']


# Building the Plots

# 1-MAP
# token to use a free type of map from mapbox
mapbox_token = 'pk.eyJ1IjoiYW5hYmVhdHJpemZpZyIsImEiOiJjbDF0NXZ4dW4yNjFrM2pxcnp1ZzQ1cGl1In0.vpjAAtkv4flG_jtgOHcDQw'

data_scattermap = dict(type='scattermapbox',
                       lat=eu_data['lat'], 
                       lon=eu_data['lon'],
                       mode=['markers', 'lines', 'text'][0],
                       #hover_name=eu_data['Countries'], hover_data=eu_data['Population, total 2022'],
                       #hoverinfo='name',
                       text=eu_data['Countries'],
                       customdata=round(eu_data['Population, total 2022']/1000000,1),
                       marker=dict(color='blue',
                                   opacity=0.7,
                                   size=eu_data['Population, total 2022']/2000000
                                   
                                  ),
                       hovertemplate="<b>Country: </b> %{text} <br>" +
                                     "<b>Population (2022): </b> %{customdata}M <br>",
                                     #"<b>GDP per capita (2020): </b> %{customdata[1]}" ,
                       hovertext='name'
                      )


layout_scattermap = dict(mapbox=dict(style='light',
                                     accesstoken=mapbox_token,
                                     #layers=[dict(source=feature) for feature in data_geo['features']],
                                     center=dict(lat=eu_data['lat'].iloc[5],
                                                 lon=eu_data['lon'].iloc[5]
                                                ),
                                     zoom=2.5
                                    ),
                         autosize=True,
                         margin=dict(
                                    l=30,
                                    r=30,
                                    b=20,
                                    t=40
                                    ),
                         title=dict(text='World Map',
                                    x=.5
                                   ),
                         hovermode='closest'
                         
                        )

fig_scattermap = go.Figure(data=data_scattermap, layout=layout_scattermap)

# 2-BARCHART

data = eu_data[['Countries',
                'Renewable energy consumption (%) 2015',
                'NonRenewable energy consumption (%) 2015',
                'Total final energy consumption (TFEC) (TJ) 2015'
               ]].sort_values(by='Renewable energy consumption (%) 2015')

data_bar1 = dict(type='bar',
                orientation='h',
                x=round(data['Renewable energy consumption (%) 2015'],2),
                y=data['Countries'],
                hovertemplate="<b>Country: </b> %{y} <br>" +
                              "<b>Energy (TJ): </b> %{x} <br>",
                name='Renewable',
                marker_color='green'
               )

data_bar2 = dict(type='bar',
                orientation='h',
                x=round(data['NonRenewable energy consumption (%) 2015'],2),
                y=data['Countries'],
                hovertemplate="<b>Country: </b> %{y} <br>" +
                              "<b>Energy (TJ): </b> %{x} <br>",
                name='NonRenewable',
                marker_color='gray'
               )

layout_bar = dict(title=dict(
                        text='Renewable and NonRenewable energy consumption (2015)',
                        x=.5
                        ),
                  xaxis=dict(title='Energy Consumption (%)'),
                  yaxis=dict(title='Country'),
                  barmode='stack'
                 )

fig_bar = go.Figure(data=[data_bar1,data_bar2] , layout=layout_bar)

# 3-SCATTERPLOT
data = eu_data[['Countries',
                'Country Code',
                'Human capital index (HCI) (scale 0-1) 2020',
                'Life expectancy at birth, total (years) 2014'
               ]]

data_scatter = dict(type='scatter',
                    mode='markers+text',
                    x=round(data['Life expectancy at birth, total (years) 2014'],2),
                    y=round(data['Human capital index (HCI) (scale 0-1) 2020'],2),
                    hovertemplate="<b>Country: </b> %{customdata} <br>" +
                                  "<b>HCI: </b> %{y} <br>" +
                                  "<b>Life expectancy: </b> %{x} <br>",
                    text=data['Country Code'],
                    customdata=data['Countries'],
                    textposition='top center',
                    marker=dict(size=eu_data['Population, total 2022']/1000000,
                                color='green',
                                opacity=0.7,
                                sizemin=4
                                )
               )

layout_scatter = dict(title=dict(
                            text='HCI X Life Expectancy',
                            x=.5
                            ),
                      xaxis=dict(title='Life expectancy at birth in years (2014)'),
                      yaxis=dict(title='Human capital index (HCI)')
                 )

fig_scatter = go.Figure(data=data_scatter , layout=layout_scatter)

# The App itself
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app = dash.Dash(__name__)

server = app.server

app.layout = html.Div(children=[
    # All elements from the top of the page
    html.Div([
        html.H1(children='Hello Dash'),

        html.Div(children='''
            Dash: A web application framework for Python.
        '''),

        dcc.Graph(
            id='map',
            figure=fig_scattermap
        ),  
    ]),
    # New Div for all elements in the new 'row' of the page
    html.Div([
        html.H1(children='Hello Dash', style = {'textAlign':'center','marginTop':20,'marginBottom':20, 'backgroundColor': 'gray'}),

        html.Div(children='''
            Dash: A web application framework for Python.
        '''),

        dcc.Graph(
            id='bar',
            figure=fig_bar
        ),  
    ]),
    # New Div for all elements in the new 'row' of the page
    html.Div([
        html.H1(children='Hello Dash'),

        html.Div(children='''
            Dash: A web application framework for Python.
        '''),

        dcc.Graph(
            id='scatter',
            figure=fig_scatter,
            style={'display': 'inline-block'}
        ),
        dcc.Graph(
            id='bar2',
            figure=fig_bar,
            style={'display': 'inline-block'}
        ),

    ]),
])


'''app.layout = html.Div(
    html.Div(
        children=[
            html.H1(children='My First DashBoard'),
            html.Div(children='Example of html Container'),
            dcc.Graph(
                id='map-graph',
                figure=fig_scattermap
                )
                ]
            ),
    html.Div(
        children=[
        html.H1(children='second graph'),
        html.Div(children='Example of html Container'),
        dcc.Graph(
            id='bar-graph',
            figure=fig_bar
            )
        ]
    )
)
'''



if __name__ == '__main__':
    app.run_server(debug=True)