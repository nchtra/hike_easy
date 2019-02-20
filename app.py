import dash
from dash.dependencies import Input, Output,State
import dash_html_components as html
import dash_core_components as dcc
import dash_table as dt
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from scipy.spatial.distance import pdist, cdist
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, OneHotEncoder ,LabelBinarizer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel
import base64

# ################################################### #
# CUSTOM FUNCTIONS FOR RECOMMENDATIONS
# ################################################### #

def get_trail_info():
    '''
    Function to read the Ontario hiking trail dataset from a pickle file
    '''
    trail_dat=pd.read_pickle('./data/alltrails_ontario_curated_0219.pkl')
    # reviews_dat=pd.read_pickle('./data/alltrails_ontario_review_keywords.pkl')
    # print (reviews_dat.head())
    # trail_dat=pd.concat([trail_dat1, reviews_dat], axis=1)
    trail_dat.columns = ['difficulty', 'distance', 'elevation', 'name', \
                        'route_type', 'stars', 'trail_attributes', 'trailName', 'tagstr', \
                        'tags_str', 'lname', 'features', 'keywords_list', 'keywords']
    return trail_dat


# Create dash table based on user input TRAIL
def generate_dash_table_tname(rec_trails, indx=''):
    '''
    Create a dash table based on the input trail selected by user
    '''
    trail_info=get_trail_info()
    colnames=['name', 'elevation', 'distance', 'difficulty', 'stars', 'features', 'keywords']

    if indx != '':
        inptrail = trail_info.iloc[indx][colnames]
    toptrails = dt.DataTable(id = 'trail_dtable',
    style_data={'whiteSpace': 'normal'},
    css=[{
        'selector': '.dash-cell div.dash-cell-value',
        'rule': 'display: inline; white-space: inherit; overflow: inherit;\
        text-overflow: inherit;'}],
    columns=[{'name':i.capitalize(), 'id': i} for i in colnames],
    data=rec_trails.to_dict('rows'),
    style_as_list_view=True, sorting=True, sorting_type="multi",
    style_header={
        'backgroundColor': 'white',
        'fontWeight': 'bold',
        'fontSize': 20
    },
    style_cell={
        'textAlign': 'left',
        'fontSize':12
    },
    style_cell_conditional=[
        {'if': {'column_id': 'name'},
         'width': '20%'},
        {'if': {'column_id': 'features'},
         'width': '25%'},
        {'if': {'column_id': 'keywords'},
          'width': '15%'},
    ],
    )
    return(toptrails)

# Generate top ten similar trails based on user input features
def get_recommendations_ui(ui_numerical, tagsui):
    '''
    Create dash table based on trail features selected by user. Trail features
    include hike distance, elevation and text trail features
    '''
    trail_info=get_trail_info()
    ui_tagsarr=tagsui.split(' ')
    trail_info=trail_info[trail_info.features.str.contains('|'.join(ui_tagsarr))]
    # Euclidean distance measure for numerical data only!
    num=ui_numerical
    numerical_data=trail_info[['elevation','distance']]
    num_eucdist=euclidean_distances(numerical_data, num)
    dfnum_sort=pd.DataFrame.from_records(num_eucdist).sort_values(by=0)
    topTen = dfnum_sort[:10].index.values
    #Create the final set of trails
    colnames=['name', 'elevation', 'distance', 'difficulty', 'stars', 'features', 'keywords']
    rec_trails=trail_info.iloc[topTen][colnames]
    return rec_trails

# Generate top ten similar hikes based on trail selected by user
def get_recommendations_tname(trail_name):
    '''
    Create a list of top 10 recommendations based on cosine similarity score or
    Euclidean distance measures
    '''
    trail_info=get_trail_info()
    cosine_sim=np.loadtxt('./data/cosine_sim_allfeat3.dat')
    indices=pd.Series(trail_info.index, index=trail_info['trailName'])
    index=indices[trail_name]
    #Extract pairwise similarity score with all trails for the input trail
    similarity_scores = list(enumerate(cosine_sim[index]))
    sorted_scores=sorted(similarity_scores, key=lambda x:x[1], reverse=True)
    sorted_scores=sorted_scores[1:11]
    topTen=[i[0] for i in sorted_scores]
    #Create the final set of trails
    colnames=['name', 'elevation', 'distance', 'difficulty', 'stars', 'features', 'keywords']
    rec_trails=trail_info.iloc[topTen][colnames]
    return (rec_trails, index)


# ################################################### #
# TRAIL CONTENTS TO BE USED FOR MENU OPTIONS IN APP
# ################################################### #

#This is initial data I need for the dropdowns
trail_info=get_trail_info()
trail_names=trail_info['name'].str.lower()
unique_tags = ['dogs on leash', 'wheelchair friendly', 'kid friendly', \
 'hiking', 'mountain biking', 'trail running', 'forest', \
 'fishing', 'horseback riding', 'bird watching', 'lake', 'river', 'waterfall',\
 'wild flowers', 'wildlife', 'rocky', 'beach', \
 'dog friendly', 'scramble', 'camping', 'rock climbing', 'cave', \
 'paddle sports', 'backpacking']
unique_tags=sorted(unique_tags)
uniqtags_nospace=[tag.replace(' ', '') for tag in unique_tags]

# ################################################### #
# END FUNCTIONS, BEGIN MAIN CONTENT
# ################################################### #

# Main image
main_img = base64.b64encode(open('./img/img_header.jpg', 'rb').read())

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#Main Dash app section
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

# Dash app layout
app.layout = html.Div([

    # HEADING TEXT AND IMAGE

    html.Div(html.H1('HikeEasy', style = {'textAlign': 'center', 'padding': '1px',
    'fontSize': 60, 'margin-bottom': '10px'})),

    html.Div(html.H4('Leading you to the right path',
    style = {'textAlign': 'center', 'margin-top': '10px', 'fontSize': 20})),

    html.Div(html.Img(id='head-image',
    src='data:image/jpeg;base64,{}'.format(main_img.decode('ascii')),
    style = {'width':'100%', 'height': '200px', 'padding':'0','margin':'0','box-sizing':'border-box'})),

    html.Div(title='Select of enter trail name', id='trail_name',children=[
    html.H4('Enter trail name', style={'fontSize': 20}),
    dcc.Dropdown(id='dropdown-trailname',
    options=[{'label':name, 'value':name} for name in trail_names], style = {'width': '51%'})
    ]),

    html.H4('or', style={'fontSize': 20}),

    html.Div(title='select hike characteristics', id='trail-distance', children=[
    html.H4('Select trail features', style={'fontSize': 20}),
    dcc.Input(id ='input-elevation',type='text', placeholder='Enter elevation (in m))', style = {'margin-right': '5px'}), # style={'float':'left'}),
    dcc.Input(id ='input-distance',type='text', placeholder='Enter distance (in km))'), # style={'float':'left'}),
    dcc.Dropdown(id = 'dropdown-tags', style = {'width': '51%', 'margin-top': '5px', 'margin-bottom': '5px'},
    options = [{'label': name, 'value': name.replace(' ', '')} for name in unique_tags], multi=True),

    html.Button(id='submit-button', n_clicks=0,children='Submit', style = {'margin-right': '5px'}),
    html.Button(id='reset-button', n_clicks=0,children='reset'),

    ]),

    html.Br(),

    html.Div(id='trail-name-details', style={'display':'block'}),
    html.Div(id='recommendations-name', style={'display':'block'}),
    html.Br(), html.Br(),
    html.Div(id='recommendations-ui', style={'display':'block'}),

    ], style = {'background-color': 'rgba(102, 102, 255, 0.1)', 'margin': '-5px'}) # 'background-image': 'url(./img/bg_img.png)',



# Dash app callbacks
# Functions to reset the trail selection dropdown
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

@app.callback(Output('dropdown-tags', 'value'),
[Input('reset-button', 'n_clicks')]
)
def reset(click):
    if (click !=0):
        return ('')

# Callback for user input features based recommendations
@app.callback(Output('recommendations-ui', 'children'),
[Input('submit-button','n_clicks'),
Input('reset-button', 'n_clicks')],
[State('input-elevation','value'),
State('input-distance','value'),
State('dropdown-tags', 'value')
])
def ui_output(subclick, resetclick, elev, dist, tagsui):
    ui_numerical=[[]]
    recs=[]

    if dist != None:
        try:
            # ui_numerical=[[float(elev), float(dist), 5.0]]
            ui_numerical=[[float(elev), float(dist)]]
            tagstr = [' '.join([x for x in tagsui])][0]
            recs=get_recommendations_ui(ui_numerical, tagstr)
            return (generate_dash_table_tname(recs))
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
        recs, index=get_recommendations_tname(trail_name)
        return (generate_dash_table_tname(recs, index))
    else:
        return ('  ')

if __name__ == '__main__':
    app.run_server(debug=True)
