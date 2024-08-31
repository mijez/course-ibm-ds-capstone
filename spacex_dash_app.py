# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# options for site selection Dropdown
launch_site_options = [
        {'label': 'ALL Sites', 'value':'ALL'},
        # create list of dicts for launch sites
        *[{'label': s, 'value': s} for s in sorted(spacex_df['Launch Site'].unique())]]


# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    options=launch_site_options,
                                    value='ALL',
                                    placeholder='Select a Launch Site',
                                    searchable=True,
                                    id='site-dropdown'),
                                html.Br(),
                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),
                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):    
    if entered_site=='ALL':
        data=spacex_df.groupby('Launch Site')['class'].count().reset_index()
        #resulting DataFrame
        #     Launch Site  class
        # 0   CCAFS LC-40     26
        # 1  CCAFS SLC-40      7
        # 2    KSC LC-39A     13
        # 3   VAFB SLC-4E     10

        fig=px.pie(
            data,
            values='class',
            names='Launch Site',
            title='Total Success Launches by Site'
            )
        return fig
    else:
        data = spacex_df.loc[spacex_df['Launch Site'].eq(entered_site)]['class'].value_counts().reset_index().sort_values(by='index')
        data['names'] = data['index'].replace({0: 'failed', 1: 'success'})
        # resulting DataFrame for 'CCAFS LC-40'
        #    index  class    names
        # 0      0     19   failed
        # 1      1      7  success

        fig = px.pie(
            data,
            values='class',
            names='names',
            color='index', # set more intuitive pie chart colors
            color_discrete_map={0: 'lightpink', 1: 'lightgreen'},
            title=f'Success and Failed Launches for Site {entered_site}'
        )

        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(    
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')])
def get_payload_chart(entered_site, payload_range):
    # filter by payload mass first
    data=spacex_df.loc[spacex_df['Payload Mass (kg)'].between(*payload_range)]
    if entered_site != 'ALL':
        # filter by specific site if selected
        data = data.loc[data['Launch Site'].eq(entered_site)]

    fig = px.scatter(data, x='Payload Mass (kg)', y='class', color='Booster Version Category')

    # improve legend appearance
    fig.update_layout(
        legend=dict(
            xanchor='right',
            yanchor='middle',
            y=0.3,
            x=0.99,
            orientation='h'))
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=False)