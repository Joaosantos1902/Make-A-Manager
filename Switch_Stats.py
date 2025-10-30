import requests
import time
import json
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

#Thingsboard token generator
def getToken():
    username = "joaolivramento@tecnico.ulisboa.pt"
    password = "ZZbI6k6zOkMY9qKEHQlvhHzkB6WIzcfj"
    
    url = "https://iot.istartlab.tecnico.ulisboa.pt/api/auth/login"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    loginJSON = {"username": username, "password": password}
    #print(loginJSON)
    tokenAuthResp = requests.post(url, headers=headers, json=loginJSON)
    #print(tokenAuthResp)
    data = tokenAuthResp.json()
    token = data['token']
    #print(token)
    return token

def getStats_month():
    counter = 0
    printing_counter = 0
    idle_counter = 0
    paused_counter = 0
    attention_counter = 0
    error_counter = 0
    other_counter = 0
    stopped_counter = 0
    limit = 500000

    switch = "http://iot.istartlab.tecnico.ulisboa.pt/api/plugins/telemetry/DEVICE/20f75dc0-67b1-11f0-bf00-9d4f62b6993c/values/timeseries"
    params = {
        "keys": "switchStatus",
        "startTs": int((int(time.time()) - 2629743*2) * 1000),  # 7 days ago in milliseconds
        "endTs": int(time.time()) * 1000,  # Current time in milliseconds
        "limit": limit
    }
    headers = {
        "X-Authorization": "Bearer "+ getToken(),
    }

    switchstatus = requests.get(switch, headers=headers, params=params)

    switchstatus_data = switchstatus.json()

    switch_stats = pd.DataFrame({
        "timestamp": [item['ts'] for item in switchstatus_data['switchStatus']],
        "switchStatus": [item['value'] for item in switchstatus_data['switchStatus']]
    })


    # Detecta onde o valor muda
    mudanca = switch_stats['switchStatus'] != switch_stats['switchStatus'].shift()

    switch_stats = switch_stats.loc[mudanca,'switchStatus'].value_counts().reset_index()
    switch_stats.columns = ['switchStatus', 'Count']
    switch_stats.set_index('switchStatus', inplace=True)

    params_2 = {
    "keys": "User_Name,User_ID,switchStatus",
    "startTs": int((int(time.time()) - 2629743*2) * 1000),  # 7 days ago in milliseconds
    "endTs": int(time.time()) * 1000,  # Current time in milliseconds
    "limit": limit
    }

    switch_user = requests.get(switch, headers=headers, params=params_2)

    switch_user_data = switch_user.json()

    data = switch_user_data  # atalhar

    switch_user_stats = pd.DataFrame({
        "timestamp":    [item ['ts'] for item in data['User_ID']],
        "User_ID":      [item ['value'] for item in data['User_ID']],
        "User_Name":    [item ['value'] for item in data['User_Name']],
    })



    item_info = switch_user_stats[['User_ID', 'User_Name']].drop_duplicates()

    # Detecta onde o valor muda
    mudanca = switch_user_stats['User_ID'] != switch_user_stats['User_ID'].shift()

    switch_user_stats = switch_user_stats.loc[mudanca,'User_ID'].value_counts().reset_index()
    switch_user_stats.columns = ['User_ID', 'Count']
    switch_user_stats.set_index('User_ID', inplace=True)

    filtered_df_per_user_final = pd.merge(
        switch_user_stats,
        item_info,
        on='User_ID',
        how='left'
    )
    filtered_df_per_user_final = filtered_df_per_user_final[['User_Name', 'User_ID', 'Count']]
    filtered_df_per_user_final.set_index('User_ID', inplace=True)


    return switch_stats, filtered_df_per_user_final

