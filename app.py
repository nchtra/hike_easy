# import hike_easy
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

# Function to get the trail dataset
def get_trail_info():
    trail_dat=pd.read_pickle('./data/alltrails_ontario_curated.pkl')
    return trail_dat


# Create dash table based on the user input FEATURES
def generate_dash_table_ui(topTen, indx='', max_rows=10):
    trail_info=get_trail_info()
    colnames=['name', 'elevation', 'distance', 'difficulty', 'stars', 'tags_str']
    rec_trails=trail_info.iloc[topTen][['name', 'elevation', 'distance', 'difficulty', 'stars', 'tags_str']]
    if indx != '':
        inptrail = trail_info.iloc[indx][['name', 'elevation', 'distance', 'difficulty', 'stars', 'tags_str']]
    return (dt.DataTable(id = 'ui_dtable',
    style_data={'whiteSpace': 'normal'},
    css=[{'selector': '.dash-cell div.dash-cell-value',
        'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
    }],
    columns=[{'name':i, 'id': i} for i in colnames],
    data=rec_trails.to_dict('rows'),
    style_cell={'textAlign': 'left'}, style_as_list_view=True, sorting=True, sorting_type="multi",
    ))


# Create dash table based on user input TRAIL
def generate_dash_table_tname(topTen, indx=''):
    trail_info=get_trail_info()
    colnames=['name', 'elevation', 'distance', 'difficulty', 'stars', 'tags_str']
    rec_trails=trail_info.iloc[topTen][['name', 'elevation', 'distance', 'difficulty', 'stars', 'tags_str']]

    if indx != '':
        inptrail = trail_info.iloc[indx][['name', 'elevation', 'distance', 'difficulty', 'stars', 'tags_str']]
    toptrails = dt.DataTable(id = 'trail_dtable',
    style_data={'whiteSpace': 'normal'},
    css=[{
        'selector': '.dash-cell div.dash-cell-value',
        'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
    }],
    columns=[{'name':i, 'id': i} for i in colnames],
    data=rec_trails.to_dict('rows'),
    # style_cell={'textAlign': 'left'}, style_as_list_view=True, sorting=True, sorting_type="multi
    style_cell={# all three widths are needed
    'minWidth': '180x', 'width': '180px', 'maxWidth': '180px',
    'whiteSpace': 'normal', 'textAlign':'center'
    },
     style_as_list_view=True, sorting=True, sorting_type="multi",
    )
    return(toptrails)

# Generate top ten similar hikes based on user input features
def get_recommendations_ui(ui_numerical, tagsui=None):
    trail_info=get_trail_info()
    # Transform tags for dataset
    vectorizer = CountVectorizer()
    alltag_transform = vectorizer.fit_transform(trail_info['tagstr'])
    alltag_array = alltag_transform.toarray()

    # Simple Euclidean distance measure for numerical data only!
    num=ui_numerical
    numerical_data=trail_info[['elevation','distance']]
    num_cossim=euclidean_distances(numerical_data, num)
    dfnum_sort=pd.DataFrame.from_records(num_cossim).sort_values(by=0)

    # Transform tags from user input using the vectorizer vocabulary generate from dataset
    cv = CountVectorizer(vocabulary=vectorizer.vocabulary_)
    tagsui_transform = cv.fit_transform(np.array([tagsui]))
    tagsui_array = tagsui_transform.toarray()

    # Combine numerical and text vectorization into a single list
    inpfeat_list = ui_numerical[0] + list(tagsui_array[0])
    # numerical_logdata=trail_info[['log_elevation','log_distance','stars']]

    # cat_allfeat = np.concatenate([num_cossim, tag_cossim], axis=1)
    # allfeat_cossim = cosine_similarity(cat_allfeat, cat_allfeat)
    # dfall_sort = pd.DataFrame.from_records(allfeat_cossim).sort_values(by=0)
    # print ('all sort: ', allfeat_cossim.shape, dfall_sort)
    topTen = dfnum_sort[:10].index.values
    return topTen

# Generate top ten similar hikes based on trail selected by user
def get_recommendations_tname(trail_name):
    trail_info=get_trail_info()
    cosine_sim=np.loadtxt('./data/cosine_sim2.dat')
    indices=pd.Series(trail_info.index, index=trail_info['trailName'])
    index=indices[trail_name]
    #Extract pairwise similarity score with all trails for the input trail
    similarity_scores = list(enumerate(cosine_sim[index]))
    sorted_scores=sorted(similarity_scores, key=lambda x:x[1], reverse=True)
    sorted_scores=sorted_scores[1:11]
    topTen=[i[0] for i in sorted_scores]
    return(topTen, index)


# ################################################### #
# END FUNCTIONS, BEGIN MAIN CONTENT
# ################################################### #
trail_info=get_trail_info()
trail_names=trail_info['name'].str.lower()
unique_tags= pd.Series([tag for tags in trail_info.trail_attributes for tag in tags]).unique()
unique_tags=sorted(unique_tags)
uniqtags_nospace=[tag.replace(' ', '') for tag in unique_tags]

# Main image
main_img = base64.b64encode(open('./img/img_header.jpg', 'rb').read())

app = dash.Dash(__name__)
server = app.server
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

# MAIN DASH APP LAYOUT
app.layout = html.Div([

    # HEADING TEXT AND IMAGE
    html.Div(html.H1('Hike Easy', style = {'textAlign': 'center', 'padding': '1px', 'height': '12px', 'margin-top': '-5px'})),
    html.Div(html.H4('Personalized hiking recommendation system!', style = {'textAlign': 'center', 'height': '10px', 'margin-top': '5px'})),
    html.Div(html.Img(id='head-image', src='data:image/jpeg;base64,{}'.format(main_img.decode('ascii')),
                      style = {'width':'100%', 'height': '200px', 'padding':'0','margin':'0','box-sizing':'border-box'})),

    html.Div(title='select trail name', id='trail_name',children=[
    html.H4('Enter trail name'),
    dcc.Dropdown(id='dropdown-trailname',
    options=[{'label':name, 'value':name} for name in trail_names])
    ]),

    html.H4('or'),

    html.Div(title='select hike characteristics', id='trail-distance', children=[
    html.H4('Enter distance, elevation for hike'),
    dcc.Input(id ='input-elevation',type='text', placeholder='Enter elevation (in m))'),
    dcc.Input(id ='input-distance',type='text', placeholder='Enter distance (in KM))'),
    dcc.Dropdown(id = 'dropdown-tags',
    options = [{'label': name, 'value': name} for name in unique_tags], multi=True),

    html.Button(id='submit-button', n_clicks=0,children='Submit'),
    html.Button(id='reset-button', n_clicks=0,children='reset'),

    ]),

    html.Br(),

    html.Div(id='trail-name-details', style={'display':'block'}),
    html.Div(id='recommendations-name', style={'display':'block'}),
    html.Div(id='recommendations-ui', style={'display':'block'}),

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

@app.callback(Output('dropdown-tags', 'value'),
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
            # return (generate_table_ui(recs))
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
        # return (generate_table(recs, index))
        return (generate_dash_table_tname(recs, index))
    else:
        return ('  ')

if __name__ == '__main__':
    app.run_server(debug=True)
