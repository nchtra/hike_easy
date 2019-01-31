import hike_easy
import dash
from dash.dependencies import Input, Output,State
import dash_html_components as html
import dash_core_components as dcc
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from scipy.spatial.distance import pdist, cdist
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, OneHotEncoder ,LabelBinarizer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel


def get_trail_info():
    trail_dat=pd.read_pickle('./data/alltrails_ontario_curated.pkl')
    return trail_dat


def generate_table(topTen, indx='', max_rows=10):
    trail_info=get_trail_info()
    colnames=['name', 'elevation', 'distance', 'difficulty', 'stars', 'trail_attributes']
    rec_trails=trail_info.iloc[topTen][['name', 'elevation', 'distance', 'difficulty', 'stars', 'trail_attributes']]
    # if (indx != ''):
    #     inp_trail_det=trail_info.iloc[indx][['name', 'elevation', 'distance', 'difficulty', 'stars', 'trail_attributes']]
    # else:
    #     inp_trail_det=''
    #
    #     print ('index', indx, inp_trail_det)

    return (

        # html.P(inp_trail_det),
        # html.Table(
        # html.Td(inp_trail_det.iloc[])
        # )

        html.Table(
        # Header
        # [html.Tr([html.Th(col) for col in rec_trails.columns])] +
        [html.Tr([html.Th(col) for col in colnames])] +
        # Body
        [html.Tr([
            html.Td(rec_trails.iloc[i][col]) for col in rec_trails.columns
        ]) for i in range(min(len(rec_trails), max_rows))]
        )
    )


def get_recommendations_ui(ui_numerical):
    trail_info=get_trail_info()
    #Numerical data processing
    num=ui_numerical
    # print (num)
    numerical_data=trail_info[['elevation','distance','stars']]
    # numerical_data=trails[['elevation', 'distance']]
    dist_numerical=euclidean_distances(numerical_data, num)
    dft_sort=pd.DataFrame.from_records(dist_numerical).sort_values(by=0)
    topTen = dft_sort[:10].index.values
    #Hiking attribute matching
    return topTen

def get_recommendations_name(trail_name):
    trail_info=get_trail_info()
    cosine_sim=np.loadtxt('./data/cosine_sim2.dat')
    indices=pd.Series(trail_info.index, index=trail_info['trailName'])
    index=indices[trail_name]
    #Extract pairwise similarity score with all trails for the input trail
    similarity_scores = list(enumerate(cosine_sim[index]))
    #Sort scores to extract the top ranked trails
    sorted_scores=sorted(similarity_scores, key=lambda x:x[1], reverse=True)
    sorted_scores=sorted_scores[1:11]
    topTen=[i[0] for i in sorted_scores]
    # return(topTen)
    return(topTen, index)


trail_info=get_trail_info()
trail_names=trail_info['name'].str.lower()
unique_tags=[tag for tags in trail_info.trail_attributes for tag in tags]

app = dash.Dash(__name__)

app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

app.layout = html.Div([

    html.Div(title='select hike characteristics', id='trail-distance', children=[
    html.P('Enter distance, elevation and star rating for hike'),
    dcc.Input(id='input-elevation',type='text', placeholder='Enter elevation (in m))'),
    dcc.Input(id='input-distance',type='text', placeholder='Enter distance (in KM))'),
    dcc.Dropdown(
    id='dropdown-tags',
    options=[{'label':name, 'value':name} for name in unique_tags],
    multi=True
    ),

    html.Button(id='submit-button', n_clicks=0,children='Submit'),

    html.Div(title='select trail name', id='trail_name',children=[
    html.P('Or enter trail name'),
    dcc.Dropdown(id='dropdown-trailname',
    options=[{'label':name, 'value':name} for name in trail_names])
    ])
    ]),

    html.Br(),

    html.Div(id='recommendations-ui', style={'display':'block'}),
    html.Div(id='trail-name-details', style={'display':'block'}),
    html.Div(id='recommendations-name', style={'display':'block'}),

])

# Function to reset the trail selection dropdown
@app.callback(Output('input-elevation', 'value'), [Input('submit-button', 'n_clicks')])
def reset_ifield(click):
    if click !=0:
        print (click)
        return None
# @app.callback(Output('dropdown-trailname','value'), [Input('dropdown-trailname', 'options')])
# def reset_dropdown(ddown):
#     return ''

# Callback for user input based recommendations
@app.callback(Output('recommendations-ui', 'children'),
[Input('submit-button','n_clicks')],
[State('input-elevation','value'),
State('input-distance','value'),
])
def ui_output(n_clicks, elev, dist):
    ui_numerical=[[]]
    recs=[]
    if dist != None:
        try:
            ui_numerical=[[float(elev), float(dist), 5.0]]
            recs=get_recommendations_ui(ui_numerical)
            return (generate_table(recs))
        except ValueError:
            return ('Please enter values')

# Callback for trail name based recommendations
@app.callback(Output('recommendations-name','children'),
[Input('dropdown-trailname','value')])
def getrec(trail_name):
    recs=[]
    index=''
    if trail_name != None:
        recs, index=get_recommendations_name(trail_name)
    return (generate_table(recs, index))

if __name__ == '__main__':
    app.run_server(debug=True)
