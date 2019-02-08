import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

trail_info=pd.read_pickle('./data/alltrails_ontario_curated.pkl')

tagsui_array = [[0, 0, 1]]

vectorizer = CountVectorizer()
alltag_transform = vectorizer.fit_transform(trail_info['tagstr'])
alltag_array = alltag_transform.toarray()
# print (alltag_array[0])

ui_numerical = [[100, 10]]
numerical_data=trail_info[['log_elevation','log_distance','stars']]
# numerical_data_list = numerical_data.values.tolist()
# alltags_list = alltag_transform.toarray().tolist()
# alltags_loflist = [[i] for i in alltags_list]
#
# list1=[]
# for i in range(len(numerical_data_list)):
#     sum = (numerical_data_list[i] + alltags_list[i])
#     list1.append(sum)
#     # print (sum)
# print (list1)
