# Elastic_Search
Flask API supports two services , data indexer using elastic search and tone analyzer using IBM watson service
## How to use the service?
1- clone the rebo 

    git clone https://github.com/NourhanMS/Elastic_Search.git
2- run index.py file 

    python index.py
3- To use tone analyzer service , send a get request with hotel name 

    ex. http://127.0.0.1:5000/tones?hotel=hotel_name
  
4- To index your data , send a get request 

    ex. http://127.0.0.1:5000/indexer
  
Note :Download hotels dataset from here https://www.kaggle.com/datafiniti/hotel-reviews

