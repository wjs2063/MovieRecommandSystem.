# MovieRecommandSystem.
airflow를 이용한 영화추천시스템


## 활용 데이터셋 
kaggle 영화 데이터셋 : https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset?select=ratings.csv

## 파일 설명 

### app.py   
: Flask api 로 ratings.csv 파일을 엔드포인트로 제공   
offset   
limit   
start_date   
end_date   
를 활용하여 원하는 날짜 간격 그리고 개수를 지정하여  
