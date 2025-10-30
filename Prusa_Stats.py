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

    prusa4url = "http://iot.istartlab.tecnico.ulisboa.pt/api/plugins/telemetry/DEVICE/40ea8710-3a4d-11f0-bf00-9d4f62b6993c/values/timeseries"
    prusa5url = "http://iot.istartlab.tecnico.ulisboa.pt/api/plugins/telemetry/DEVICE/4c093e90-363b-11f0-bf00-9d4f62b6993c/values/timeseries"
    prusa6url = "http://iot.istartlab.tecnico.ulisboa.pt/api/plugins/telemetry/DEVICE/472de8a0-3a49-11f0-bf00-9d4f62b6993c/values/timeseries"
    params = {
        "keys": "printerStatus,Job_Owner_ID,Job_Owner_Name,jobProgress",
        "startTs": int((int(time.time()) - 604800) * 1000),  # 7 days ago in milliseconds
        "endTs": int(time.time()) * 1000,  # Current time in milliseconds
        "limit": limit
    }
    headers = {
        "X-Authorization": "Bearer "+ getToken(),
    }

    prusa4response = requests.get(prusa4url, headers=headers, params=params)
    prusa5response = requests.get(prusa5url, headers=headers, params=params)
    prusa6response = requests.get(prusa6url, headers=headers, params=params)

    prusa4json_data = prusa4response.json()
    prusa5json_data = prusa5response.json()
    prusa6json_data = prusa6response.json()
    #print(json_data['Job_Owner_ID'])

    prusa4_stats = pd.DataFrame({
        "timestamp": [item['ts'] for item in prusa4json_data['printerStatus']],
        "printerStatus": [item['value'] for item in prusa4json_data['printerStatus']],
        "Job_Owner_ID": [item['value'] for item in prusa4json_data['Job_Owner_ID']],
        "Job_Owner_Name": [item['value'] for item in prusa4json_data['Job_Owner_Name']],
        "JobProgress": [item['value'] for item in prusa4json_data['jobProgress']]
    })

    prusa5_stats = pd.DataFrame({
        "timestamp": [item['ts'] for item in prusa5json_data['printerStatus']],
        "printerStatus": [item['value'] for item in prusa5json_data['printerStatus']],
        "Job_Owner_ID": [item['value'] for item in prusa5json_data['Job_Owner_ID']],
        "Job_Owner_Name": [item['value'] for item in prusa5json_data['Job_Owner_Name']],
        "JobProgress": [item['value'] for item in prusa5json_data['jobProgress']]
    })
    prusa6_stats = pd.DataFrame({
        "timestamp": [item['ts'] for item in prusa6json_data['printerStatus']],
        "printerStatus": [item['value'] for item in prusa6json_data['printerStatus']],
        "Job_Owner_ID": [item['value'] for item in prusa6json_data['Job_Owner_ID']],
        "Job_Owner_Name": [item['value'] for item in prusa6json_data['Job_Owner_Name']],
        "JobProgress": [item['value'] for item in prusa6json_data['jobProgress']]
    })

    prusa4_stats.to_csv('csv_files/prusa4_stats_week.csv', index=False)
    prusa5_stats.to_csv('csv_files/prusa5_stats_week.csv', index=False)
    prusa6_stats.to_csv('csv_files/prusa6_stats_week.csv', index=False)

    return prusa4_stats, prusa5_stats, prusa6_stats  


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

    prusa4url = "http://iot.istartlab.tecnico.ulisboa.pt/api/plugins/telemetry/DEVICE/40ea8710-3a4d-11f0-bf00-9d4f62b6993c/values/timeseries"
    prusa5url = "http://iot.istartlab.tecnico.ulisboa.pt/api/plugins/telemetry/DEVICE/4c093e90-363b-11f0-bf00-9d4f62b6993c/values/timeseries"
    prusa6url = "http://iot.istartlab.tecnico.ulisboa.pt/api/plugins/telemetry/DEVICE/472de8a0-3a49-11f0-bf00-9d4f62b6993c/values/timeseries"
    params = {
        "keys": "printerStatus,Job_Owner_ID,Job_Owner_Name,jobProgress",
        "startTs":  int((int(time.time()) - 2629743*2) * 1000),  # 30 days ago in milliseconds   '''1754994373477,'''
        "endTs":  int((int(time.time()) - 2629743*0) * 1000),  # Current time in milliseconds  '''1755858373477,'''
        "limit": limit
    }
    headers = {
        "X-Authorization": "Bearer "+ getToken(),
    }

    prusa4response = requests.get(prusa4url, headers=headers, params=params)
    prusa5response = requests.get(prusa5url, headers=headers, params=params)
    prusa6response = requests.get(prusa6url, headers=headers, params=params)

    prusa4json_data = prusa4response.json()
    prusa5json_data = prusa5response.json()
    prusa6json_data = prusa6response.json()
    #print(json_data['Job_Owner_ID'])

    prusa4_stats = pd.DataFrame({
        "timestamp": [item['ts'] for item in prusa4json_data['printerStatus']],
        "printerStatus": [item['value'] for item in prusa4json_data['printerStatus']],
        "Job_Owner_ID": [item['value'] for item in prusa4json_data['Job_Owner_ID']],
        "Job_Owner_Name": [item['value'] for item in prusa4json_data['Job_Owner_Name']],
        "JobProgress": [item['value'] for item in prusa4json_data['jobProgress']]
    })


    prusa5_stats = pd.DataFrame({
        "timestamp": [item['ts'] for item in prusa5json_data['printerStatus']],
        "printerStatus": [item['value'] for item in prusa5json_data['printerStatus']],
        "Job_Owner_ID": [item['value'] for item in prusa5json_data['Job_Owner_ID']],
        "Job_Owner_Name": [item['value'] for item in prusa5json_data['Job_Owner_Name']],
        "JobProgress": [item['value'] for item in prusa5json_data['jobProgress']]
    })
    prusa6_stats = pd.DataFrame({
        "timestamp": [item['ts'] for item in prusa6json_data['printerStatus']],
        "printerStatus": [item['value'] for item in prusa6json_data['printerStatus']],
        "Job_Owner_ID": [item['value'] for item in prusa6json_data['Job_Owner_ID']],
        "Job_Owner_Name": [item['value'] for item in prusa6json_data['Job_Owner_Name']],
        "JobProgress": [item['value'] for item in prusa6json_data['jobProgress']]
    })

    prusa4_stats.to_csv('csv_files/prusa4_stats_month.csv', index=False)
    prusa5_stats.to_csv('csv_files/prusa5_stats_month.csv', index=False)
    prusa6_stats.to_csv('csv_files/prusa6_stats_month.csv', index=False)

    return prusa4_stats, prusa5_stats, prusa6_stats  


def number_of_prints(df):


    df['ts_utc'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)

    # 2) converter para Europa/Lisboa (DST tratado automaticamente)
    df['ts_pt'] = df['ts_utc'].dt.tz_convert('Europe/Lisbon')

    h = df['ts_pt'].dt.hour
    df['noite'] = (h >= 20) | (h < 6)

    #df.loc[(df['printerStatus'] == "ATTENTION") & (df['JobProgress'] == "0.0"), 'printerStatus'] = 'IDLE'
    #df.loc[(df['printerStatus'] == "ATTENTION") & (df['JobProgress'] == "0"), 'printerStatus'] = 'IDLE'
    df.loc[(df['printerStatus'] == "BUSY"), 'printerStatus'] = 'PRINTING'
    df.loc[(df['printerStatus'] == "PAUSED"), 'printerStatus'] = 'PRINTING'


    #mudanca = (df['printerStatus'] != df['printerStatus'].shift())
    #df = df.loc[mudanca]
    #df['grupo'] = df.loc[mudanca]

    
    

    #filtered_df = df['printerStatus'].value_counts().reset_index()

    #filtered_df.columns = ['printerStatus', 'Count']
    #filtered_df.set_index('printerStatus', inplace=True)
    #return filtered_df
    
    '''df['grupo'] = (df['printerStatus'] != df['printerStatus'].shift()).cumsum()


    df['tamanho_seq'] = df.groupby('grupo')['printerStatus'].transform('size')

    sequencias = df.groupby('grupo').agg({
    'printerStatus': 'first',
    'grupo': 'size',
    }).rename(columns={'grupo': 'tamanho_seq'})

    valor_escolhido = "PRINTING"
    sequencias_valor = sequencias[sequencias['printerStatus'] == valor_escolhido]
    sequencias_valor['categoria'] = sequencias_valor['tamanho_seq'].apply(classificar_tamanho)

    contagem = sequencias_valor['categoria'].value_counts().sort_index()

    resumo = sequencias_valor.groupby('categoria')['tamanho_seq'].agg(
    sequencias='count',
    total_ocorrencias='sum'
    ).reset_index()
    
    print(contagem)
    return resumo ''''''

    '''# Identificar sequências consecutivas por 'valores'
    df['grupo'] = (df['printerStatus'] != df['printerStatus'].shift()).cumsum()

    # Tamanho de cada sequência e se teve algum ponto à noite
    seq = df.groupby('grupo').agg(
        State=('printerStatus', 'first'),
        tamanho=('printerStatus', 'size'),
        noite=('noite', 'any')  # True se qualquer ponto da sequência foi à noite
    ).reset_index(drop=True)

    seq = seq[seq['State'] == 'PRINTING']
    seq['Time'] = seq['tamanho'].apply(classificar_tamanho)

    #Numero total de impressões por tamanho
    total_prints = (
        seq
        .groupby(['State','Time'])
        .size()
        .rename('Total Prints')
        .reset_index()
    )

    soma_ocorr_total = (
    seq
    .groupby(['State','Time'])['tamanho']
    .sum()
    .rename('Total Print Time (min)')
    .reset_index()
    )

    conta_seq_noite = (
        seq[seq['noite']]
        .groupby(['State','Time'])
        .size()
        .rename('Night Prints')
        .reset_index()
    )

    soma_ocorr_noite = (
    seq[seq['noite']]
    .groupby(['State','Time'])['tamanho']
    .sum()
    .rename('Night Print Time (min)')
    .reset_index()
    )

    resumo_noite = conta_seq_noite.merge(soma_ocorr_noite, on=['State','Time'], how='outer').fillna(0)


    return resumo_noite


def classificar_tamanho(n):
    n = int(n)
    if n <= 15:
        return '0m to 15m'
    elif n <= 60:
        return '15min to 1h'
    elif n <= 300:
        return  '1h to 5h'
    elif n <= 900:
        return '5h to 15h'
    elif n <= 1800:
        return '15h to 30h'
    else:
        return 'Over 30h'

    





    #mudanca = (df['printerStatus'] != df['printerStatus'].shift() and df['printerStatus'] == "PRINTING").cumsum()

    #df['grupo'] = df[mudanca]

    #df['tamanho_seq'] = df.groupby('grupo')['printerStatus'].transform('size')
    

    #filtered_df = df['printerStatus'].value_counts().reset_index()

    #filtered_df.columns = ['printerStatus', 'Count']
    #filtered_df.set_index('printerStatus', inplace=True)
    #return df



def filter_and_count_status(df, status):
    """
    Filter the DataFrame for a specific printer status and count occurrences.
    
    Args:
        df (DataFrame): The DataFrame containing printer status data.
        status (str): The printer status to filter by."""
    
    #Excluir dados sem Job_Owner_ID
    exclude = [""]

    df.loc[(df['printerStatus'] == "ATTENTION") & (df['JobProgress'] == "0.0"), 'printerStatus'] = 'IDLE'
    df.loc[(df['printerStatus'] == "ATTENTION") & (df['JobProgress'] == "0"), 'printerStatus'] = 'IDLE'

    

    


    # Criar condição segura para "Job_Owner_ID vazio ou nulo"
    condicao_vazio = df['Job_Owner_ID'].isna() | (df['Job_Owner_ID'].astype(str).str.strip() == "")

    # Aplicar só a quem tem status diferente de IDLE
    condicao_final = condicao_vazio & (df['printerStatus'] != "IDLE")

    # Substituir valores em falta
    df.loc[condicao_final, ['Job_Owner_ID', 'Job_Owner_Name']] = ["NO_ID", "UNKNOWN"]




    # Filter the DataFrame first
    active_df = df[~df['Job_Owner_ID'].isin(exclude)]



    


    # Associar ID e Nome de usuário
    item_info = active_df[['Job_Owner_ID', 'Job_Owner_Name']].drop_duplicates()



    
    
    
    if status == "ERROR":
        filtered_df = active_df[active_df['printerStatus'] == status]
        filtered_df.loc[(filtered_df['JobProgress'].astype(float) > 50) & (filtered_df['printerStatus'] == "ERROR"), ['Job_Owner_ID','Job_Owner_Name']] = ["Internal", "Internal"]
        filtered_df.loc[(filtered_df['printerStatus'] == "ERROR") & (filtered_df['JobProgress'] == "0.0"), ['Job_Owner_ID',"Job_Owner_Name"]] = ["NO_ID", "UNKNOWN"]
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

    elif status == "PRINTING":
        filtered_df = active_df[active_df['printerStatus'].isin([status,"ATTENTION"])]
        filtered_df_per_user = filtered_df['Job_Owner_ID'].value_counts().reset_index()
        filtered_df_per_user.columns = ['Job_Owner_ID', 'Minutes']
        filtered_df_per_user['categoria'] = filtered_df_per_user['Minutes'].apply(classificar_tamanho)
        filtered_df_per_user['Minutes'] = filtered_df_per_user['Minutes'].apply(lambda x: f"{x} minutes")


        filtered_df_per_user_final = pd.merge(
            filtered_df_per_user,
            item_info,
            on='Job_Owner_ID',
            how='left'
        )
        filtered_df_per_user_final = filtered_df_per_user_final[['Job_Owner_Name', 'Job_Owner_ID', 'Minutes', 'categoria']]
        filtered_df_per_user_final.set_index('Job_Owner_ID', inplace=True)

    else:
        filtered_df = active_df[active_df['printerStatus'] == status]
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

    df.loc[(df['printerStatus'] == "ATTENTION") & (df['JobProgress'] == "0.0"), 'printerStatus'] = 'IDLE'
    df.loc[(df['printerStatus'] == "ATTENTION") & (df['JobProgress'] == "0"), 'printerStatus'] = 'IDLE'



    # Criar condição segura para "Job_Owner_ID vazio ou nulo"
    condicao_vazio = df['Job_Owner_ID'].isna() | (df['Job_Owner_ID'].astype(str).str.strip() == "")

    # Aplicar só a quem tem status diferente de IDLE
    condicao_final = condicao_vazio & (df['printerStatus'] != "IDLE")


    # Substituir valores em falta
    df.loc[condicao_final, ['Job_Owner_ID', 'Job_Owner_Name']] = ["NO_ID", "UNKOWN"]


    # Detecta onde o valor muda
    mudanca = df['printerStatus'] != df['printerStatus'].shift() 

    # Substitui "A" que não sejam o início de uma sequência
    df.loc[(df['printerStatus'] == 'IDLE due to Authentication Failure') & (~mudanca), 'printerStatus'] = 'IDLE'
    df.loc[(df['printerStatus'] == 'ERROR') & (~mudanca), 'printerStatus'] = 'IDLE'

    stats = df['printerStatus'].value_counts().reset_index()
    stats.columns = ['printerStatus', 'Minutes/Times']
    #stats['Minutes/Times'] = stats['Minutes/Times'].apply(lambda x: f"{x} Minutes/Times")
    stats.set_index('printerStatus', inplace=True)
    
    stats_2 = stats.copy()

    statuses_to_include = ['IDLE', 'PRINTING',  'OFFLINE']                   # 'BUSY', 'ERROR', 'ATTENTION', 'PAUSED', 'STOPPED', 'FINISHED',
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
    'OFFLINE': "#000000AC",  # preto
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

    ax.legend(wedges, stats.index, title="State", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

    ax.set_title("Distribution of Printer States", fontsize=14)
    ax.axis("equal")  # Mantém o círculo proporcional

    # Mostrar no Streamlit
    st.pyplot(fig)


    return stats_2

'''
st.set_page_config(
    page_title="Prusa Stats",
    layout="wide",  # This enables wide mode
    initial_sidebar_state="collapsed"
)

st.title("IStartLab Printer Stats")

# Cria as 3 colunas lado a lado
col1, col2, col3 = st.columns(3)

prusa4_stats, prusa5_stats, prusa6_stats = getStats()

with col1:
    st.write("PRUSA 4 Stats:")
    st.write(printer_stats(prusa4_stats))
    st.write("PRUSA 4 Usage per User:")
    st.write(filter_and_count_status(prusa4_stats, "PRINTING"))
    st.write("PRUSA 4 Error Stats per User:")
    st.write(filter_and_count_status(prusa4_stats, "ERROR"))
    st.write("PRUSA 4 Attention Stats per User:")
    st.write(filter_and_count_status(prusa4_stats, "ATTENTION"))
with col2:
    st.write("PRUSA 5 Stats:")
    st.write(printer_stats(prusa5_stats))
    st.write("PRUSA 5 Usage per User:")
    st.write(filter_and_count_status(prusa5_stats, "PRINTING"))
    st.write("PRUSA 5 Error Stats per User:")
    st.write(filter_and_count_status(prusa5_stats, "ERROR"))
    st.write("PRUSA 5 Attention Stats per User:")
    st.write(filter_and_count_status(prusa5_stats, "ATTENTION"))
with col3:
    st.write("PRUSA 6 Stats:")
    st.write(printer_stats(prusa6_stats))
    st.write("PRUSA 6 Usage per User:")
    st.write(filter_and_count_status(prusa6_stats, "PRINTING"))
    st.write("PRUSA 6 Error Stats per User:")
    st.write(filter_and_count_status(prusa6_stats, "ERROR"))
    st.write("PRUSA 6 Attention Stats per User:")
    st.write(filter_and_count_status(prusa6_stats, "ATTENTION"))


time.sleep(3600)

st.rerun()  # Re-run the script every 60 seconds
'''