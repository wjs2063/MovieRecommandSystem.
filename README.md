# MovieRecommandSystem.
airflow, Flask 이용한 영화추천시스템

### 개발환경 
OS : mac m1 
Anaconda VM 

-> 배포는 Docker 이미지로 

### 사용 Tool 
airflow,Python,Flask

### VM 구축후  
1. DB 초기화  
```
airflow db init 
```
2. 유저 생성 
```
airflow users create  --username [쓰고싶은이름]  --firstname jeon  --lastname jaehyeon  --role Admin  --email jahy5352@naver.com 
```
3. 웹서버 생성 
```
airflow webserver --port 8080
```

## 활용 데이터셋 
kaggle 영화 데이터셋 : https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset?select=ratings.csv

## USAGE 
위 데이터 링크에서 모든파일을 다운받고 app.config['file_path'] 부분에 해당 ratings.csv 파일 설정해주면 쉽게 데이터를 얻을수있다.  
1. rating json
example :  http://127.0.0.1:5000/ratings?start_date=2012-09-09&end_date=2012-10-01  

2. credit json
example : http://127.0.0.1:5000/credits 

3. kewords json
exampl : http://127.0.0.1:5000/keywords
## 파일 설명 
ratings.csv -> 1995-01-09 ~ 2017-08-04 까지 의 데이터


### app.py   
: Flask api 로 ratings.csv 파일을 엔드포인트로 제공   
offset   
limit   
start_date   
end_date   
를 활용하여 원하는 날짜 간격 그리고 개수를 지정하여 제공  

HTTP Basic Auth 를 통하여  간단한 보안 생성

session 요청을 할때 항상 session.auth() 를 추가해주어야 http 401 에러가 뜨지않는다. 함수안에 캡슐화를 시

이러한 movie_api 를  캡슐화 + 제활용 가능하게 Hook 으로 

--------------------------------------------------------------------------------------
### 정규화 vs 반정규화 

추천시스템을 만들때 일별 영화순위는 ratings.csv 파일로 작성하면 큰 문제가없다. 하지만 개인별로 장르에 대한 선호도, 영화배우에 대한 선호도를 계산하여 추천시스템에 반영한다면 
pd.merge 과정은 필연적이다. merge 과정은 key 값을 기준으로 진행되기때문에 O(n^2) 시간이 소요되므로 성능에 좋지못하기때문에 반정규화해서 가져오는것이 성능에 이득일 것 같다. 


### airflow Basehook
https://airflow.apache.org/docs/apache-airflow/stable/_modules/airflow/hooks/base.html#BaseHook 

### DB Choosing 
https://airflow.apache.org/docs/apache-airflow/2.4.0/howto/set-up-database.html 
공식문서에서 Postgresql or mysql 추천 

### WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.


