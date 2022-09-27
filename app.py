import os
import time
import pandas as pd
from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from ast import literal_eval
import datetime
# https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset
DEFAULT_ITEMS_PER_PAGE = 100
os.environ['API_USER'] = 'airflow'
os.environ['API_PASSWORD'] = "airflow"

# literal_eval : string 형식의 dict 를 dict로 변


def unpacking_genre(x):
    '''
    Parameters
    ----------
    x : String 
            metadata['geners']
    Returns
    -------
    list
        genres 
    '''
    genre_x = literal_eval(x)
    if len(genre_x) == 0:
        return None
    else:
        return [genre['name'] for genre in genre_x]


def transform_date(x):
    '''
    Parameters
    ----------
    x : String
            metadata['release_date'] dataframe .
    Returns
    -------
    x : string (year).
    '''
    x = x.split("-")[0]
    if x == 'nan':
        return None
    else:
        return x


def unpacking_keywords(x):
    '''
    Parameters
    ----------
    x : Str .
    Returns
    -------
    list
        List.
    '''
    keyword_x = literal_eval(x)
    if len(keyword_x) == 0:
        return None
    else:
        return [keyword['name'] for keyword in keyword_x]


def unpacking_cast(x):
    '''
    Parameters
    ----------
    x : TYPE
        DESCRIPTION.
    Returns
    -------
    list
        DESCRIPTION.
    '''
    cast_x = literal_eval(x)
    if len(cast_x) == 0:
        return None
    else:
        return [cast['name'] for cast in cast_x]


def _read_ratings(file_path):
    ratings = pd.read_csv(file_path)

    # Subsample dataset.
    ratings = ratings.sample(n=100000, random_state=0)
    ratings['timestamp'] = ratings['timestamp'].apply(lambda x:convert_datetime(x) )
    # Sort by ts, user, movie for convenience.
    ratings = ratings.sort_values(by=["timestamp", "userId", "movieId"])
    ratings["userId"] = ratings["userId"].astype(str)
    ratings["movieId"] = ratings["movieId"].astype(str)

    return ratings


def _read_metadata(file_path):
    '''
    Returns metadata
    Parameters
    ------------
    file path : metadata.csv file_path
    '''
    metadata = pd.read_csv(file_path)
    metadata = metadata[["id", "title", "genres", "original_language",
                         "overview", "release_date", "vote_average", "vote_count"]]

    # id,title,generes,original_language,overview,release_date 의 타입 변환
    metadata["id"] = metadata["id"].astype(str)
    metadata["title"] = metadata["title"].astype(str)
    metadata["genres"] = metadata["genres"].astype(str)
    metadata["original_language"] = metadata["original_language"].astype(str)
    metadata["overview"] = metadata["overview"].astype(str)
    metadata["release_date"] = metadata["release_date"].astype(str)

    metadata['genres'] = metadata.genres.apply(lambda x: unpacking_genre(x))
    metadata["release_date"] = metadata.release_date.apply(
        lambda x: transform_date(x))
    return metadata


def _read_keywords(file_path):
    keywords = pd.read_csv(file_path)
    keywords["id"] = keywords["id"].astype(str)
    keywords["keywords"] = keywords["keywords"].astype(str)

    keywords['keywords'] = keywords.keywords.apply(
        lambda x: unpacking_keywords(x))
    return keywords


def _read_credits(file_path):
    credit = pd.read_csv(file_path)
    #credit = credit.sample(n=100, random_state=0)
    credit = credit[['cast', 'id']]
    credit["id"] = credit["id"].astype(str)
    credit["cast"] = credit["cast"].astype(str)
    credit["cast"] = credit['cast'].apply(lambda x: unpacking_cast(x))
    return credit


app = Flask(__name__)
# File path
app.config["ratings_file_path"] = "/Users/pn_jh/Desktop/개발/Kaggle_data를 이용한 영화추천시스템/MovieRecommandSystem./dataset/ratings.csv"
app.config["links_file_path"] = "/Users/pn_jh/Desktop/개발/Kaggle_data를 이용한 영화추천시스템/MovieRecommandSystem./dataset/links.csv"
app.config["keywords_file_path"] = "/Users/pn_jh/Desktop/개발/Kaggle_data를 이용한 영화추천시스템/MovieRecommandSystem./dataset/keywords.csv"
app.config["credits_file_path"] = "/Users/pn_jh/Desktop/개발/Kaggle_data를 이용한 영화추천시스템/MovieRecommandSystem./dataset/credits.csv"
app.config["metadata_file_path"] = "/Users/pn_jh/Desktop/개발/Kaggle_data를 이용한 영화추천시스템/MovieRecommandSystem./dataset/movies_metadata.csv"

# Dataframe File
app.config["ratings"] = _read_ratings(app.config["ratings_file_path"])
app.config["metadatas"] = _read_metadata(app.config["metadata_file_path"])
app.config["credits"] = _read_credits(app.config["credits_file_path"])
app.config["keywords"] = _read_keywords(app.config["keywords_file_path"])

# USER // PASSWORD (환경변수)
auth = HTTPBasicAuth()
users = {os.environ["API_USER"]: generate_password_hash(
    os.environ["API_PASSWORD"])}
# PASS WORD 유효한지 판단


@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False


@app.route("/")
def hello():
    return "Hello from the Movie Rating API!"


@app.route("/ratings")
@auth.login_required
def ratings():
    """
    Returns ratings from the kaggle_movie_dataset.
    캐글 영화 데이터셋의 rating.csv 파일 반환
    Parameters
    ----------
    start_date : str
        Start date to query from (inclusive).
    end_date : str
        End date to query upto (exclusive).
    offset : int
        Offset to start returning data from (used for pagination).
    limit : int
        Maximum number of records to return (used for pagination).
    """

    start_date_ts = request.args.get("start_date", None)
    end_date_ts = request.args.get("end_date", None)

    offset = int(request.args.get("offset", 0))
    limit = int(request.args.get("limit", DEFAULT_ITEMS_PER_PAGE))

    ratings_df = app.config.get("ratings")
    # dataframe 에서 start_date 와 end_date 사이의 것들만 반환
    if start_date_ts:
        ratings_df = ratings_df.loc[ratings_df["timestamp"] >= start_date_ts]

    if end_date_ts:
        ratings_df = ratings_df.loc[ratings_df["timestamp"] < end_date_ts]
    # offset <= x < offset + limit 을 반환  즉 limit 개수만큼
    subset = ratings_df.iloc[offset: offset + limit]

    return jsonify(
        {
            "result": subset.to_dict(orient="records"),
            "offset": offset,
            "limit": limit,
            "total": ratings_df.shape[0],
        }
    )


@app.route("/credits")
@auth.login_required
def credit_json():
    credits_df = app.config.get("credits")
    return jsonify(
        {
            "result": credits_df.to_dict(orient="records"),
            "total": credits_df.shape[0],
        }
    )

@app.route("/keywords")
@auth.login_required
def keyword_json():
    keyword_df = app.config.get("keywords")
    return jsonify(
        {
            "result" : keyword_df.to_dict(orient = "records"),
            "total" : keyword_df.shape[0]
            }
        )
    




# 날짜 형식으로 변환
def _date_to_timestamp(date_str):
    if date_str is None:
        return None
    return int(time.mktime(time.strptime(date_str, "%Y-%m-%d")))
def convert_datetime(unixtime):
    """
    
    Parameters
    ----------
    unixtime : TYPE
        INT , UNIXTIME
    Returns
    -------
    date : TYPE 
        str, 
    """
    date = datetime.datetime.fromtimestamp(unixtime).strftime('%Y-%m-%d')
    return date # format : str

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)

