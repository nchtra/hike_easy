import pandas as pd
import pymongo
from pymongo import MongoClient


client=MongoClient()
# table=client.Ontario_reviewsdb.hikes
table=client.Ontario_allreviewsdb.hikes
data=pd.DataFrame(list(table.find()))

#Create pandas DataFrames
dfr=[]

reviews=data.reviews

for i in range(len(reviews)):
    name = data.hike_name[i]
    difficulty = data.hike_difficulty[i]
    distance=data.total_distance
    elevation = data.elevation_gain[i]
    try: #if elevation != '':
        elevation = elevation.replace('\nELEVATION GAIN\n','').strip()
        if 'm' in elevation:
            elevation=float((elevation.replace(' m','')).replace(',',''))
            elevation=float("{0:.2f}".format(elevation))
        elif 'feet' in elevation:
            elevation=(elevation.replace(' feet','')).replace(',','')
            elevation=float(elevation)*0.3048
            elevation=float("{0:.2f}".format(elevation))
        if nan in elevation:
            elevation=0.
    except AttributeError:
        pass
        # elevation=int(elevation)
        # elevation=
    # else:
    #     elevation = 0
    distance = (data.total_distance[i].replace('\nDISTANCE\n', '').strip())
    if 'km' in distance:
        distance=float(distance.replace(' km', ''))
    elif('miles' in distance):
        distance=float(distance.replace(' miles', ''))*1.6
    nreviews=data.num_reviews[i]
    stars=float(data.stars[i])
    region=data.hike_region[i]
    trail_attributes=data.hike_attributes[i]
    route_type=data.route_type[i].replace('\nROUTE TYPE\n','').strip()

    # row={
    # 'name':name,
    # 'difficulty': difficulty,
    # 'elevation': elevation,
    # 'distance':distance,
    # 'trail_attributes':trail_attributes,
    # 'route_type':route_type,
    # 'stars':stars,
    # 'nreviews':nreviews
    # # 'review':review
    # }

    allreviews_trail=''
    for j in range(len(reviews[i])):
        review=list(reviews[i][j].values())[0]
        try:
            review=review.decode('utf-8')
        except AttributeError:
            pass

        if review != '':
            #Create a single string with all reviews for a given trail
            allreviews_trail += str(review).strip()
            # print (review)
            # row={
            # 'name':name,
            # 'difficulty': difficulty,
            # 'elevation': elevation,
            # 'distance':distance,
            # 'trail_attributes':trail_attributes,
            # 'route_type':route_type,
            # 'stars':stars,
            # 'nreviews':nreviews
            # # 'review':review
            # }
        else:
            continue
        # allreviews=allreviews_trail
    # print (j, allreviews_trail, sep='')
    row={
    'name':name,
    'difficulty': difficulty,
    'elevation': elevation,
    'distance':distance,
    'trail_attributes':trail_attributes,
    'route_type':route_type,
    'stars':stars,
    'nreviews':nreviews,
    'review':allreviews_trail
    }
    # print (row)
    dfr.append(row)

df=pd.DataFrame(dfr)
# df.to_pickle('./dftst.pkl')
# df.to_pickle('./hiking_attributes_ontario1.pkl')
df.to_pickle('./alltrails_ontario.pkl')
