#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 25 22:38:36 2022

@author: pn_jh
"""

import requests


session = requests.Session()
response = session.get("http://127.0.0.1:5000/ratings")
session.auth = ("airflow" , "airflow")
response = session.get(
    "http://127.0.0.1:5000/ratings",
    params = {
        "start_date" : "2010-05-03",
        "end_date" : "2010-05-04",
        },
    )

def _get_session():
    session = requests.Session()
    session.auth = ("airflow" , "airflow")
    base_url =  "http://127.0.0.1:5000"
    return session,base_url


def _get_with_pagination(session,url,params,batch_size = 100):
    offset = 0
    total = None
    while total is None or offset < total :
        response = session.get(
            url,
            params = {**params,
                      **{"offset" : offset, "limit" : batch_size}
                      }
            
            )
        response.raise_for_status()
        # 결과 상태를 체크 , JSON 을 parsing 
        response_json = response.json()
        # 결과를 함수 호출자에게 yield 
        yield from response_json["result"]
        offset += batch_size
        total = response_json["total"]