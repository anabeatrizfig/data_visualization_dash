import pandas as pd
pd.set_option('display.float_format', lambda x: '%.6f' % x)
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# Data Preprocessing

# open dataset
eu_data = pd.read_excel('data/eu_data_v2.xlsx', sheet_name='geral')
eu_time = pd.read_excel('data/eu_data_v2.xlsx', sheet_name='temporal')

# create new features
eu_data['NonRenewable energy consumption (TJ) 2015'] = eu_data['Total final energy consumption (TFEC) (TJ) 2015'] - eu_data['Renewable energy consumption (TJ) 2015']
eu_data['NonRenewable energy consumption (%) 2015'] = eu_data['NonRenewable energy consumption (TJ) 2015']/eu_data['Total final energy consumption (TFEC) (TJ) 2015']
eu_data['Renewable energy consumption (%) 2015'] = eu_data['Renewable energy consumption (TJ) 2015']/eu_data['Total final energy consumption (TFEC) (TJ) 2015']

eu_time.columns = ['Countries', 'Country Code', 'lat', 'lon', 'Year',
                   'Wind', 'Hydro',
                   'Solar', 'Nuclear',
                   'Biofuels', 'Geo Biomass Other',
                   'Coal', 'Oil',
                   'Gas', 'Renewable Consumption – Twh',
                   'No Renewable Consumption – Twh'
                ]

country_options = [dict(label=country, value=country) for country in eu_data['Countries'].unique()]
energy_options = ['Wind', 'Hydro',
                   'Solar', 'Nuclear',
                   'Biofuels', 'Geo Biomass Other',
                   'Coal', 'Oil',
                   'Gas']

# token to use a free type of map from mapbox
mapbox_token = 'pk.eyJ1IjoiYW5hYmVhdHJpemZpZyIsImEiOiJjbDF0NXZ4dW4yNjFrM2pxcnp1ZzQ1cGl1In0.vpjAAtkv4flG_jtgOHcDQw'
# 1-MAP - fixed - no filter applied

data_scattermap = dict(type='scattermapbox',
                    lat=eu_data['lat'], 
                    lon=eu_data['lon'],
                    mode=['markers', 'lines', 'text'][0],
                    text=eu_data['Countries'],
                    customdata=round(eu_data['Population, total 2022']/1000000,1),
                    marker=dict(color='steelblue',
                                opacity=0.8,
                                size=eu_data['Population, total 2022']/2000000
                                
                                ),
                    hovertext=eu_data['GDP per capita (current US$) 2020'],
                    hovertemplate="<b>Country: </b> %{text} <br>" +
                                    "<b>Population (2022): </b> %{customdata}M <br>"
                                    "<b>GDP per capita (2020): </b> US$ %{hovertext}"
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
                                    t=5
                                    ),
                        paper_bgcolor='#9EDBDA',
                        # title=dict(text='World Map',
                        #             x=.5
                        #         ),
                        hovermode='closest'
                        
                        )

fig_scattermap = go.Figure(data=data_scattermap, layout=layout_scattermap)

# Building the Plots
# 2-BARCHART

data_bar = eu_data[['Countries',
                    'Renewable energy consumption (%) 2015',
                    'NonRenewable energy consumption (%) 2015',
                    'Total final energy consumption (TFEC) (TJ) 2015'
    ]].loc[(eu_data['Countries'] != 'Czech Republic') &
           (eu_data['Countries'] != 'Malta')].sort_values(by='Renewable energy consumption (%) 2015')

data_bar1 = dict(type='bar',
            orientation='h',
            x=round(data_bar['Renewable energy consumption (%) 2015'],2),
            y=data_bar['Countries'],
            hovertemplate="<b>Country: </b> % {y} <br>" +
                        "<b>Energy (TJ): </b> % {x} <br>",
            name='Renewable',
            marker_color='green'
        )

data_bar2 = dict(type='bar',
            orientation='h',
            x=round(data_bar['NonRenewable energy consumption (%) 2015'],2),
            y=data_bar['Countries'],
            hovertemplate="<b>Country: </b> % {y} <br>" +
                        "<b>Energy (TJ): </b> % {x} <br>",
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
data_scatter = eu_data[['Countries',
                        'Country Code',
                        'Renewable Consumption – Twh',
                        'GDP per capita (current US$) 2020',
                        'GDP (current US$) 2020'                    ]]

data_scatter1 = dict(type='scatter',
                    mode='markers+text',
                    x=round(data_scatter['Renewable Consumption – Twh'],2),
                    y=round(data_scatter['GDP (current US$) 2020'],2),
                    customdata=data_scatter['Countries'],
                    textposition='top center',
                    marker=dict(size=eu_data['Population, total 2022']/1000000,
                                color='steelblue',
                                opacity=0.8,
                                sizemin=4
                                ),
                    hovertemplate="<b>Country: </b>%{customdata}<br>" +
                                  "<b>GDP (2020): </b>US$ %{y}<br>" +
                                  "<b>Renewable Consumption: </b>%{x}<br>"
                                  
                    # text=data_scatter['Country Code'],
               )

layout_scatter = dict(
                      margin=dict(
                                    l=40,
                                    r=40,
                                    b=20,
                                    t=5
                                    ),
                      paper_bgcolor='#9EDBDA',
                      xaxis=dict(title='Renewable Consumption – Twh 2020'),
                      yaxis=dict(title='GDP (current US$) 2020')
                 )

fig_scatter = go.Figure(data=data_scatter1 , layout=layout_scatter)

# The App itself
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app = dash.Dash(__name__)

server = app.server

app.layout = html.Div([
    html.Div([
        html.H1('Consumption of Energy in European Union Countries')
    ], className='title'),
    html.Div([
        html.P('Students:  Ana Beatriz Oliveira (20211023) | Carlos Nunes (20210997) | Eliane Gotuzzo (20210996)  .',className='paragraph')
    ], className='column_two'),
    html.Div([
        html.Div([
            html.Div([html.Label('Year:'),
                dcc.Slider(
                    id='year_slider',
                    min=eu_time['Year'].min(),
                    max=eu_time['Year'].max(),
                    marks={str(i): '{}'.format(str(i)) for i in
                            [2000, 2005, 2010, 2015, 2020]},
                    value=2020,
                    step=1)],
                className='column_two_filter'
                ),
            html.Div([html.Label('Country:'),
                dcc.Dropdown(
                    id='country_drop',
                    options=country_options,
                    value='Portugal',
                    multi=False
                )],
                className='column_two_filter'
                )],
            className='row'),
        html.Div([html.H4(children='')], className='row'),
        html.Div([html.Label('Type of Energy:'),
                dcc.Dropdown(
                    id='type_energy',
                    options=energy_options,
                    value=energy_options,
                    multi=True
                )],
                className='column_two_filter'
                )
            ], className='filter'),
    html.Div([
        html.Div([
            html.H2(children='EU Countries and Population (2022)'),
            dcc.Graph(
                id='map',
                figure=fig_scattermap
                ),
            html.H3(children='.  ')
            ],
            className='column_two'),
        html.Div([
            html.H2(children='Energy Consumption'),
            dcc.Graph(id='fig_line_up'),
            html.H3(children='Note: No data for Malta and Czech Republic')
                ],
                className='column1'
            )
        ],
        className='row'),
    html.Div([
        html.Div([
            html.H2(children='Renewable Consumption vs GDP per Country'),
            dcc.Graph(
                id='scatter',
                figure=fig_scatter
                # ,style={'display': 'inline-block', 'with': '90%'}
                ),
                html.H3(children='Note: size represents the population (2022)')
                ],
                className='column_two'),
            html.Div([
                html.H2(children='Energy Consumption per Type'),
                dcc.Graph(id='fig_line_down'),
                html.H3(children='Note: No data for Malta and Czech Republic')
            ],
            className='column1'
            )
    ],
    className='row')
     
])


@app.callback(
    Output('fig_line_up', 'figure'),    
    Input('country_drop', 'value'),
    Input('year_slider', 'value'),
)

def plots(countries, year):
    data = eu_time[['Countries',
                    'Year',
                    'Renewable Consumption – Twh',
                    'No Renewable Consumption – Twh'
                ]]

    variables = ['Renewable Consumption – Twh',
                'No Renewable Consumption – Twh']

    country = countries

    year = list(range(2000, year+1))

    data_filter = data.loc[(data['Countries'] == country) & (data['Year'].isin(year))]

    data_line = []

    for variable in variables:
             
        x_line = data_filter['Year']
        y_line =data_filter[variable]

        data_line.append(dict(type='scatter',
                            mode='lines',
                            x=x_line,
                            y=y_line,
                            text=y_line.name,
                            customdata=data_filter['Countries'],
                            name = variable.split('Consumption')[0],
                            hovertemplate="<b>Country: </b> %{customdata} <br>" +
                                        "<b>Year: </b> %{x} <br>" +
                                        "<b>Value: </b> %{y} <br>")
                        )

        layout_line = dict(
                                xaxis=dict(title='Year'),
                                yaxis=dict(title='Energy Consumption'
                                ),
                            legend=dict(
                                orientation="h"
                                # ,
                                # yanchor="bottom",
                                # y=1.02,
                                # xanchor="right",
                                # x=1
                                ),
                            margin=dict(
                                    l=40,
                                    r=40,
                                    b=20,
                                    t=5
                                    ),
                            paper_bgcolor='#9EDBDA'  
                            )

    
    
    return go.Figure(data=data_line , layout=layout_line)


@app.callback(
    Output('fig_line_down', 'figure'),    
    Input('country_drop', 'value'),
    Input('year_slider', 'value'),
    Input('type_energy', 'value')
)

def plots(countries, year, energy):

    data = eu_time[['Countries',
                    'Year',
                    'Wind', 'Hydro',
                    'Solar', 'Nuclear',
                    'Biofuels', 'Geo Biomass Other',
                    'Coal', 'Oil',
                    'Gas'
                ]]

    variables = energy

    country = countries

    year = list(range(2000, year+1))

    data_filter = data.loc[(data['Countries'] == country) & (data['Year'].isin(year))]

    data_line = []

    for variable in variables:
             
        x_line = data_filter['Year']
        y_line =data_filter[variable]

        data_line.append(dict(type='scatter',
                            mode='lines',
                            x=x_line,
                            y=y_line,
                            text=y_line.name,
                            customdata=data_filter['Countries'],
                            name = variable,
                            hovertemplate="<b>Country: </b> %{customdata} <br>" +
                                           "<b>Year: </b> %{x} <br>" +
                                           "<b>Value: </b> %{y} <br>")
                        )

        layout_line = dict(
                                xaxis=dict(title='Year'),
                                yaxis=dict(title='Energy Consumption'
                                ),
                            legend=dict(
                                orientation="h"
                                # ,
                                # yanchor="bottom",
                                # y=-1.4,
                                # xanchor="right",
                                # x=0.5

                                ),
                            margin=dict(
                                    l=40,
                                    r=40,
                                    b=20,
                                    t=5
                                    ),
                            paper_bgcolor='#9EDBDA'   
                            )

    
    
    return go.Figure(data=data_line , layout=layout_line)

if __name__ == '__main__':
    app.run_server(debug=True)