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


def generate_table(topTen, max_rows=10):
    trail_info=get_trail_info()
    rec_trails=trail_info.iloc[topTen][['name', 'elevation', 'distance', 'stars', 'trail_attributes']]
    # print (rec_trails)
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in rec_trails.columns])] +
        # Body
        [html.Tr([
            html.Td(rec_trails.iloc[i][col]) for col in rec_trails.columns
        ]) for i in range(min(len(rec_trails), max_rows))]
    )


def get_recommendations_ui(ui_numerical): #,trails):
    trail_info=get_trail_info()
    #Numerical data processing
    num=ui_numerical
    print (num)
    numerical_data=trail_info[['elevation','distance','stars']]
    # numerical_data=trails[['elevation', 'distance']]
    dist_numerical=euclidean_distances(numerical_data, num)
    dft_sort=pd.DataFrame.from_records(dist_numerical).sort_values(by=0)
    topTen = dft_sort[:10].index.values
    #Hiking attribute matching
    return topTen


def get_recommendations_name(trail_name):
    trail_info=get_trail_info()
    trail_names=trail_info['name'].str.lower()
    trail_info['lowcase_names']=trail_names
    hike_idx=trail_info.index[trail_info['lowcase_names']==trail_name].tolist()
    # index=hike_idx[0]
    # #Numerical data processing
    numerical_data=trail_info[['elevation','distance','stars']]
    num=trail_info.iloc[hike_idx[0]][['elevation','distance','stars']]
    # num=trail_user
    # print (num)
    # dist_numerical=euclidean_distances(numerical_data, num)
    scaled_num=StandardScaler().fit_transform(numerical_data)
    # cosine_sim_num=cosine_similarity(scaled_num,scaled_num)
    cosine_sim_num=linear_kernel(scaled_num,scaled_num)
    print ('CSN', cosine_sim_num[0])

    #Categorical hike difficulty data processing
    categ_data=trail_info[['difficulty']]
    #Binarize labels
    lbd=LabelBinarizer()
    diffic_binary=lbd.fit_transform(categ_data)
    scaled_difficulty=StandardScaler().fit_transform(diffic_binary)
    # cosine_sim_diffic=cosine_similarity(scaled_difficulty,scaled_difficulty)
    cosine_sim_diffic=linear_kernel(scaled_difficulty,scaled_difficulty)
    print ('CSDIFF', cosine_sim_diffic[0])

    ##Text data preprocessing
    tv=TfidfVectorizer()
    tags=trail_info['tags']
    tag_matrix=tv.fit_transform(tags)
    cosine_sim_tags=linear_kernel(tag_matrix,tag_matrix)
    print('CSTAG', cosine_sim_tags.shape)

# trail_info = pd.read_pickle('./data/alltrails_ontario_curated.pkl')
trail_info=get_trail_info()
trail_names=trail_info['name'].str.lower()
# unique_tags=[tag.replace(' ','') for tags in trail_info.trail_attributes for tag in tags]
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

    html.Div(id='output'),

    html.Div(title='select trail name', id='trail_name',children=[
    html.P('Or enter trail name'),
    dcc.Dropdown(id='dropdown-trailname',
    options=[{'label':name, 'value':name} for name in trail_names])
    ])
    ]),

    html.Br(),

    html.Button(id='submit-button', n_clicks=0,children='Submit'),

    html.Div(id='recommendations-ui'),
    html.Div(id='recommendations-name'),

])

# Callback for user input based recommendations
@app.callback(Output('recommendations-ui', 'children'),
[Input('submit-button','n_clicks')],
[State('input-elevation','value'),
State('input-distance','value'),
])
def output(n_clicks, elev, dist): #, rating):
    ui_numerical=[[]]
    recs=[]
    if(dist != None):
        ui_numerical=[[float(elev), float(dist), 5.0]]
        print (ui_numerical)
        recs=get_recommendations_ui(ui_numerical) #, trail_info)
    return (generate_table(recs))


# Callback for trail name based recommendations
@app.callback(Output('recommendations-name','children'),
[Input('submit-button','n_clicks')],
[State('dropdown-trailname','value')])
def getrec(n_clicks, trail_name):
    if trail_name != None:
        recs=get_recommendations_name(trail_name)
    # print ('here')
    return('You chose a hike name: ', trail_name)




if __name__ == '__main__':
    app.run_server(debug=True)
