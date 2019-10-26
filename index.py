from flask import Flask
from flask import request
import pandas as pd
import json
from ibm_watson import ToneAnalyzerV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from elasticsearch import Elasticsearch
es = Elasticsearch()

app = Flask(__name__) 

#read data and prepare it
data=pd.read_csv('7282_1.csv')

hotels_data=data[data['categories']=="Hotels"][["name","reviews.text","address","categories","city","country","latitude","longitude","postalCode","province"]]
hotels_data.dropna(axis = 0,inplace=True)
name_grouped_df=hotels_data.groupby("name")


def get_tones_info(reviews):
    tones_frequency={}
    tones_normalized_score_summation={}
    tones={}
    for text in reviews:
        tone_analysis = tone_analyzer.tone(
        {'text': text},
        sentences=None,
        content_type='application/json'
        ).get_result()

        tones_length= len(tone_analysis['document_tone']["tones"])

        for tone_index in range(0,tones_length):
            tone_id=tone_analysis['document_tone']["tones"][tone_index]["tone_id"]
            score=tone_analysis['document_tone']["tones"][tone_index]["score"]
            if( tone_id in tones_frequency):
                tones_frequency[tone_id]+=1
                tones_normalized_score_summation[tone_id]+=score
            else:
                tones_frequency[tone_id]=1
                tones_normalized_score_summation[tone_id]=score
   
    for tone_id in tones_frequency:
        tones[tone_id]="{0:.2f}".format(round(tones_normalized_score_summation[tone_id]/tones_frequency[tone_id],2))
    return tones
    

#Initiate IBM Tone analyzer service

authenticator = IAMAuthenticator('w8dAymrrKpbodOers7_d0DffaW27sgUNCkg74FZ95umT')
tone_analyzer = ToneAnalyzerV3(
    version='2017-09-21',
    authenticator=authenticator
)

tone_analyzer.set_service_url('https://gateway-lon.watsonplatform.net/tone-analyzer/api')


@app.route('/tones')
def tones_analyzer():
    hotel_name= request.args.get("hotel")
    if hotel_name == None:
       hotel_name="Cherokee Lodge Bed and Breakfast"
  

    hotel_data=hotels_data[hotels_data["name"]==hotel_name]
  
    tones=get_tones_info(hotel_data['reviews.text'])
    return json.dumps(tones)

@app.route('/indexer')
def indexer():
    counter=1
    for index,row in name_grouped_df.first().iterrows():
        hotel_data=hotels_data[hotels_data["name"]==index]

        #get hotel tones using IBM waston tone analyzer service
        tones=get_tones_info(hotel_data['reviews.text'])
        tones_string= json.dumps(tones)

        doc={
            "name":index,
            "city":row["city"],
            "country":row["country"],
            "address":row["address"],
            "latitude":row["latitude"],
            "longitude":row["longitude"],
            "postalCode":row["postalCode"],
            "province":row["province"],
            "tone":tones_string
        }
        res = es.index(index="basharsoft", doc_type='hotel', id=counter, body=doc)
        counter+=1
    return("data indexed")

 

# With debug=True, Flask server will auto-reload 
# when there are code changes
if __name__ == '__main__':
	app.run(port=5000, debug=True)

