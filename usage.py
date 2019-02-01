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
import base64
import dash_table


def get_trail_info():
    trail_dat=pd.read_pickle('./data/alltrails_ontario_curated.pkl')
    return trail_dat


def generate_table(topTen, indx='', max_rows=10):
    trail_info=get_trail_info()
    colnames=['name', 'elevation', 'distance', 'difficulty', 'stars', 'tags_str']
    rec_trails=trail_info.iloc[topTen][['name', 'elevation', 'distance', 'difficulty', 'stars', 'tags_str']]

    if indx != '':
        inptrail=trail_info.iloc[indx][['name', 'elevation', 'distance', 'difficulty', 'stars', 'tags_str']]
        inptr = html.Table(
        [html.Tr([html.Th(col) for col in colnames])] +
        [html.Td(inptrail[col]) for col in rec_trails.columns]
        )

    return (
        # inptr,
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

def get_recommendations_ui(ui_numerical, tagsui=None):
    trail_info=get_trail_info()
    #Numerical data processing
    num=ui_numerical
    numerical_data=trail_info[['elevation','distance','stars']]
    dist_numerical=euclidean_distances(numerical_data, num)
    dft_sort=pd.DataFrame.from_records(dist_numerical).sort_values(by=0)
    topTen = dft_sort[:10].index.values
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
    return(topTen, index)


trail_info=get_trail_info()
trail_names=trail_info['name'].str.lower()
unique_tags= pd.Series([tag for tags in trail_info.trail_attributes for tag in tags]).unique()
unique_tags=sorted(unique_tags)
uniqtags_nospace=[tag.replace(' ', '') for tag in unique_tags]

# Main image
main_img = base64.b64encode(open('./img/img_header.jpg', 'rb').read())


app = dash.Dash(__name__)

app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

app.layout = html.Div([

    html.Div(html.H1('Hike Easy', style = {'textAlign': 'center'})),
    html.Div(html.H3('Personalized hiking recommendation system!', style = {'textAlign': 'center'})),
    html.Div(html.Img(id='head-image', src='data:image/jpeg;base64,{}'.format(main_img.decode('ascii')),
                      style = {'width':'100%', 'padding':'0','margin':'0','box-sizing':'border-box'})),

    html.Div(title='select hike characteristics', id='trail-distance', children=[
    html.H4('Enter distance, elevation for hike'),
    dcc.Input(id='input-elevation',type='text', placeholder='Enter elevation (in m))'),
    dcc.Input(id='input-distance',type='text', placeholder='Enter distance (in KM))'),

    html.Button(id='submit-button', n_clicks=0,children='Submit'),
    html.Button(id='reset-button', n_clicks=0,children='reset'),

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
@app.callback(Output('input-elevation', 'value'),
[Input('reset-button', 'n_clicks')]
)
def reset(click):
    if (click !=0):
        return ('')

@app.callback(Output('input-distance', 'value'),
[Input('reset-button', 'n_clicks')]
)
def reset(click):
    if (click !=0):
        return ('')

# Callback for user input based recommendations
@app.callback(Output('recommendations-ui', 'children'),
[Input('submit-button','n_clicks'),
Input('reset-button', 'n_clicks')],
[State('input-elevation','value'),
State('input-distance','value'),
])
def ui_output(subclick, resetclick, elev, dist):
    ui_numerical=[[]]
    recs=[]

    if dist != None:
        try:
            ui_numerical=[[float(elev), float(dist), 5.0]]
            recs=get_recommendations_ui(ui_numerical)
            return (generate_table(recs))
        except ValueError or TypeError:
            return ('  ')
    else:
        return ('')

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
