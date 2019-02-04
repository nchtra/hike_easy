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


def get_trail_info():
    trail_dat=pd.read_pickle('./data/alltrails_ontario_curated.pkl')
    return trail_dat


def generate_table(topTen, indx='', max_rows=10):
    inptr=''
    trail_info=get_trail_info()
    colnames=['name', 'elevation', 'distance', 'difficulty', 'stars', 'tags']
    rec_trails=trail_info.iloc[topTen][['name', 'elevation', 'distance', 'difficulty', 'stars', 'tags_str']]

    if indx != '':
        inptrail=trail_info.iloc[indx][['name', 'elevation', 'distance', 'difficulty', 'stars', 'tags_str']]
        inptr = html.Table(
        [html.Tr([html.Th(col) for col in colnames])] +
        [html.Td(inptrail[col]) for col in rec_trails.columns]
        )

    return (
        inptr,
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

def generate_table_ui(topTen, max_rows=10):
    trail_info=get_trail_info()
    colnames=['name', 'elevation', 'distance', 'difficulty', 'stars', 'tags']
    rec_trails=trail_info.iloc[topTen][['name', 'elevation', 'distance', 'difficulty', 'stars', 'tags_str']]

    table_ui = html.Table([html.Tr([html.Th(col) for col in colnames])] +
    # Body
    [html.Tr([
        html.Td(rec_trails.iloc[i][col]) for col in rec_trails.columns
    ]) for i in range(min(len(rec_trails), max_rows))])

    return(table_ui)



def generate_graphical_output(topTen, indx):
    all_trails = get_trail_info()
    trail_rec = all_trails.iloc[topTen][['name']] #, 'elevation', 'distance', 'difficulty', 'stars', 'tags_str']]
    iwidth = 1200
    iheight = 300

    #Use input trail
    # print (all_trails.iloc[indx])
    user_trail = all_trails.iloc[indx]['urlname']
    print (user_trail)
    url_link= str('https://www.alltrails.com/explore/trail/canada/ontario/' + str(user_trail)) # + str('?ref=sidebar-static-map'))
    print ('url_link: ', url_link)
    page = html.Iframe(src=url_link, width=iwidth, height=iheight)
    return(page)

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
    # print ('similarity scores: ', similarity_scores)
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

# app.css.append_css({
#    'external_url': (
#        'assets/style_hikeEasy.css'
#    )
# })

app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

app.layout = html.Div([

    html.Div(html.H1('Hike Easy', style = {'textAlign': 'center', 'padding': '1px', 'height': '12px', 'margin-top': '-10px'})),
    html.Div(html.H3('Personalized hiking recommendation system!', style = {'textAlign': 'center', 'height': '10px'})),
    html.Div(html.Img(id='head-image', src='data:image/jpeg;base64,{}'.format(main_img.decode('ascii')),
                      style = {'width':'100%', 'height': '200px', 'padding':'0','margin':'0','box-sizing':'border-box'})),

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

    # html.Iframe(src='https://www.alltrails.com/explore/trail/canada/ontario/nassagaweya-and-bruce-trail-loop-from-rattlesnake-point?ref=sidebar-view-full-map',
    # width=1000, height=300), #style={'float': 'left', 'border': 'none'}),

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
            # return (generate_table(recs))
            return (generate_table_ui(recs))
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
        # print (recs, index)
        # generate_graphical_output(recs, index)
    # return (generate_table(recs, index))
        # return (generate_graphical_output(recs, index))
        return (generate_table(recs, index))
    else:
        return ('  ')

if __name__ == '__main__':
    app.run_server(debug=True)
