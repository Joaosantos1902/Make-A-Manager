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

#Min in 30 days 43200

def getStats_week():
    counter = 0
    printing_counter = 0
    idle_counter = 0
    paused_counter = 0
    attention_counter = 0
    error_counter = 0
    other_counter = 0
    stopped_counter = 0
    limit = 100000

    prusatv = "http://iot.istartlab.tecnico.ulisboa.pt/api/plugins/telemetry/DEVICE/b6f138e0-6c9e-11f0-bf00-9d4f62b6993c/values/timeseries"
    params = {
        "keys": "printerStatus,Job_Owner_ID,Job_Owner_Name,jobProgress",
        "startTs": int((int(time.time()) - 604800) * 1000),  # 7 days ago in milliseconds
        "endTs": int(time.time()) * 1000,  # Current time in milliseconds
        "limit": limit
    }
    headers = {
        "X-Authorization": "Bearer "+ getToken(),
    }

    prusatvresponse = requests.get(prusatv, headers=headers, params=params)


    prusatvjson_data = prusatvresponse.json()
    #print(json_data['Job_Owner_ID'])

    prusatv_stats = pd.DataFrame({
        "timestamp": [item['ts'] for item in prusatvjson_data['printerStatus']],
        "printerStatus": [item['value'] for item in prusatvjson_data['printerStatus']],
        "Job_Owner_ID": [item['value'] for item in prusatvjson_data['Job_Owner_ID']],
        "Job_Owner_Name": [item['value'] for item in prusatvjson_data['Job_Owner_Name']],
        "JobProgress": [item['value'] for item in prusatvjson_data['jobProgress']]
    })

    prusatv_stats.replace({'printerStatus': {'ERROR': 'OFFLINE'}}, inplace=True)

    prusatv_stats.to_csv('csv_files/prusa4_stats_week_TV.csv', index=False)


    return prusatv_stats


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

    prusatv = "http://iot.istartlab.tecnico.ulisboa.pt/api/plugins/telemetry/DEVICE/b6f138e0-6c9e-11f0-bf00-9d4f62b6993c/values/timeseries"
    params = {
        "keys": "printerStatus,Job_Owner_ID,Job_Owner_Name,jobProgress",
        "startTs": int((int(time.time()) - 2629743*1) * 1000),  # 7 days ago in milliseconds
        "endTs": int(time.time()) * 1000,  # Current time in milliseconds
        "limit": limit
    }
    headers = {
        "X-Authorization": "Bearer "+ getToken(),
    }

    prusatvresponse = requests.get(prusatv, headers=headers, params=params)

    prusatvjson_data = prusatvresponse.json()

    prusatv_stats = pd.DataFrame({
        "timestamp": [item['ts'] for item in prusatvjson_data['printerStatus']],
        "printerStatus": [item['value'] for item in prusatvjson_data['printerStatus']],
        "Job_Owner_ID": [item['value'] for item in prusatvjson_data['Job_Owner_ID']],
        "Job_Owner_Name": [item['value'] for item in prusatvjson_data['Job_Owner_Name']],
        "JobProgress": [item['value'] for item in prusatvjson_data['jobProgress']]
    })

    prusatv_stats.replace({'printerStatus': {'ERROR': 'OFFLINE'}}, inplace=True)

    prusatv_stats.to_csv('csv_files/prusa4_stats_month_TV.csv', index=False)


    return prusatv_stats




def filter_and_count_status(df, status):
    """
    Filter the DataFrame for a specific printer status and count occurrences.
    
    Args:
        df (DataFrame): The DataFrame containing printer status data.
        status (str): The printer status to filter by."""
    
    #Excluir dados sem Job_Owner_ID
    exclude = [""]


    # Criar condição segura para "Job_Owner_ID vazio ou nulo"
    condicao_vazio = df['Job_Owner_ID'].isna() | (df['Job_Owner_ID'].astype(str).str.strip() == "")

    # Aplicar só a quem tem status diferente de IDLE
    condicao_final = condicao_vazio & (df['printerStatus'] != "IDLE")

    # Substituir valores em falta
    df.loc[condicao_final, ['Job_Owner_ID', 'Job_Owner_Name']] = ["IST100000", "IStartLab"]




    # Filter the DataFrame first
    active_df = df[~df['Job_Owner_ID'].isin(exclude)]



    


    # Associar ID e Nome de usuário
    item_info = active_df[['Job_Owner_ID', 'Job_Owner_Name']].drop_duplicates()



    filtered_df = active_df[active_df['printerStatus'] == status]
    
    
    if status == "ERROR":
        
        filtered_df.loc[(filtered_df['JobProgress'].astype(float) > 50) & (filtered_df['printerStatus'] == "ERROR"), ['Job_Owner_ID','Job_Owner_Name']] = ["Internal", "Internal"]
        filtered_df_per_user = filtered_df['Job_Owner_ID'].value_counts().reset_index()
        filtered_df_per_user.columns = ['Job_Owner_ID', 'Count']
        filtered_df_per_user['Count'] = filtered_df_per_user['Count'].apply(lambda x: f"{x} times")

        filtered_df_per_user_final = pd.merge(
            filtered_df_per_user,
            item_info,
            on='Job_Owner_ID',
            how='left'
        )
        filtered_df_per_user_final = filtered_df_per_user_final[['Job_Owner_Name', 'Job_Owner_ID', 'Count']]
        filtered_df_per_user_final.set_index('Job_Owner_ID', inplace=True)
    else:
        filtered_df_per_user = filtered_df['Job_Owner_ID'].value_counts().reset_index()
        filtered_df_per_user.columns = ['Job_Owner_ID', 'Minutes']
        filtered_df_per_user['Minutes'] = filtered_df_per_user['Minutes'].apply(lambda x: f"{x} minutes")

        filtered_df_per_user_final = pd.merge(
            filtered_df_per_user,
            item_info,
            on='Job_Owner_ID',
            how='left'
        )
        filtered_df_per_user_final = filtered_df_per_user_final[['Job_Owner_Name', 'Job_Owner_ID', 'Minutes']]
        filtered_df_per_user_final.set_index('Job_Owner_ID', inplace=True)

    
    return filtered_df_per_user_final
   

def printer_stats(df):

    #Excluir dados sem Job_Owner_ID
    exclude = [""]



    # Criar condição segura para "Job_Owner_ID vazio ou nulo"
    condicao_vazio = df['Job_Owner_ID'].isna() | (df['Job_Owner_ID'].astype(str).str.strip() == "")

    # Aplicar só a quem tem status diferente de IDLE
    condicao_final = condicao_vazio & (df['printerStatus'] != "IDLE")

    # Substituir valores em falta
    df.loc[condicao_final, ['Job_Owner_ID', 'Job_Owner_Name']] = ["IST100000", "IStartLab"]

    stats = df['printerStatus'].value_counts().reset_index()
    stats.columns = ['printerStatus', 'Minutes/Times']
    #stats['Minutes/Times'] = stats['Minutes/Times'].apply(lambda x: f"{x} Minutes/Times")
    stats.set_index('printerStatus', inplace=True)

    statuses_to_include = ['IDLE', 'PRINTING', 'BUSY', 'ERROR', 'ATTENTION', 'PAUSED', 'STOPPED', 'FINISHED', 'OFFLINE']
    stats = stats.loc[stats.index.isin(statuses_to_include)]

    status_colors = {
    'IDLE': "#1ca3b8",  # azul
    'PRINTING': "#15b044",  # laranja
    'BUSY': "#ED9909",  # verde
    'ERROR': '#d62728',  # vermelho
    'PAUSED': "#949196",  # roxo
    'STOPPED': '#8c564b',  # castanho
    'FINISHED': '#e377c2',  # rosa
    'IDLE due to Authentication Failure': "#090909",  # cinzento
    'OFFLINE': "#000000",  # preto
    }

    stats = stats.reindex(status_colors.keys()).dropna()

    colors = [status_colors[status] for status in stats.index]


    fig, ax = plt.subplots(figsize=(6, 6), constrained_layout=True)

    wedges, texts, autotexts = ax.pie(
        stats['Minutes/Times'],
        autopct='%1.1f%%',
        colors=colors,
        startangle=90,
        textprops={'fontsize': 10},
        wedgeprops={'linewidth': 1, 'edgecolor': 'white'}
    )

    ax.legend(wedges, stats.index, title="Status", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

    ax.set_title("Distribuição dos Status do Impressora")
    ax.axis("equal")  # Mantém o círculo proporcional

    # Mostrar no Streamlit
    st.pyplot(fig)


    return stats

