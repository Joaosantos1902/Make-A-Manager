#!/bin/bash

import requests
import json
import time
import sched
import bambulabs_api as bl

Central_API = "Central_SERVER_IP"

event_schedule = sched.scheduler(time.time, time.sleep)

def get_json_from_prusalink(printer_host, API_key, path):
    try:
        r = requests.get('http://' + printer_host + path, headers = {'X-Api-Key': API_key})
        r.raise_for_status()
        return_json = r.json()
    except requests.exceptions.HTTPError as err:
        return_json = {}
        print(f"Error getting json from {printer_host}")
        print(r)
    except requests.exceptions.JSONDecodeError as err:
        return_json = {}
        print(f"Error decoding json from {printer_host}")
        print(r)
    except requests.exceptions.ConnectionError as err:
        return_json = {}
        print(f"Error connecting to {printer_host}")

    return return_json

def get_printer_info(printer_Name):
    try:
        info = requests.get(Central_API+'/api/get_printer_info/'+printer_Name)
    except requests.exceptions.RequestException as e:
        print("Error geting printer info:", e)

    #print(info.json())
    return info.json()

def store_cards_list(cards):

    with open('cards_list.txt', 'w') as f:
        cards = json.dumps(cards)
        f.write(cards)
        f.close()
        

    return

def bambu_monitoring(printer_name,recheck=False):
    
    info = get_printer_info(printer_name)
    print(info)
    printerHost = info['printerHost']
    printerSerial = info['printerSerial']
    API_key = info['API_key']

    printer = bl.Printer(printerHost,API_key,printerSerial)

    try:
        printer.mqtt_start()
    except Exception as e:
        print(f"Error connecting to printer {printer_name}: {e}")
        print(f"Printer {printer_name} is OFFLINE")
        try:
            response = requests.post(Central_API+'/api/declare_dead/'+printer_name, json={})
            print(response.json(),response.status_code)
        except requests.exceptions.RequestException as e:
            print("Error declaring dead:", e)
 
        event_schedule.enter(time_between_checks, 1, bambu_monitoring, argument=(printer_name,))
    

        

    time.sleep(2)  # Wait for connection to establish



    printerStatus = str(printer.get_current_state()) if str(printer.get_current_state()) != "UNKNOWN" else "IDLE"
    state = printer.get_state()
    timeRemaining = printer.get_time() if printerStatus == "PRINTING" else -1
    jobProgress = printer.get_percentage() if printerStatus == "PRINTING" else 0
    currentJob = printer.get_file_name() if printerStatus == "PRINTING" else "No Job"

    print(f"Printer {printer_name} Status: {printerStatus}")
    print(f"State: {state}")
    print(f"Current Job: {currentJob}")
    print(f"Job Progress: {jobProgress}%")
    print(f"Time Remaining: {timeRemaining} seconds")

    printer.mqtt_stop()

    json_ = {
            "printerName": printer_name,
            "printerStatus": printerStatus,
            "currentJob": currentJob,
            "jobID": "",
            "jobProgress": jobProgress,
            'ReCheck': recheck,
            "TimeRemaining": timeRemaining,
        }
    

    try:
        response = requests.post(Central_API+'/api/post_printer_info', json=json_)
        print(response.json(),response.status_code)
    except requests.exceptions.RequestException as e:
        print("Error posting to Central API:", e)

    if response.json()['status'] == "Authentication Failure" and recheck == False:
        Unify_Plugin()
        bambu_monitoring(printer_name,recheck=True)

    elif response.json()['status'] == "Authentication Failure" and recheck == True:
        print("No Job to delete")
        event_schedule.enter(time_between_checks, 1, bambu_monitoring, argument=(printer_name,))
        
    else:
        event_schedule.enter(time_between_checks, 1, bambu_monitoring, argument=(printer_name,))




def prusa_monitoring(printer_name,recheck=False):
    info = get_printer_info(printer_name)
    printerHost = info['printerHost']
    API_key = info['API_key']
    prusalink_printer_status_path = info['Prusalink_Status_Path']
    prusalink_printer_job_path = info['Prusalink_Job_Path']
    prusalink_printer_status = get_json_from_prusalink(printerHost, API_key, prusalink_printer_status_path)
    prusalink_printer_job_file = get_json_from_prusalink(printerHost, API_key, prusalink_printer_job_path)
    
    print("JOB FILE:")
    print(prusalink_printer_job_file)
    print("STATUS FILE:")
    print(prusalink_printer_status)
    


    if prusalink_printer_status == {} and prusalink_printer_job_file == {}:
        print(f"Printer {printer_name} is OFFLINE")
        try:
            response = requests.post(Central_API+'/api/declare_dead/'+printer_name, json={})
        except requests.exceptions.RequestException as e:
            print("Error declaring dead:", e)
        print(response.json(),response.status_code)
        event_schedule.enter(time_between_checks, 1, prusa_monitoring, argument=(printer_name,))
        
    else:
        if prusalink_printer_job_file == {}:
            json_ = {
            "printerName": printer_name,
            "printerStatus": prusalink_printer_status['printer']['state'],
            "currentJob": "No Job",
            "jobID": "",
            "jobProgress": 0,
            'ReCheck': False,
            "TimeRemaining": -1,
        }
        else:
            json_ = {
                "printerName": printer_name,
                "printerStatus": prusalink_printer_status['printer']['state'],
                "currentJob": prusalink_printer_job_file['file']['name'],
                "jobID": prusalink_printer_job_file['id'],
                "jobProgress": prusalink_printer_job_file['progress'],
                'ReCheck': False,
                "TimeRemaining": prusalink_printer_job_file['time_remaining'],
            }


        if recheck == True:
            json_['ReCheck'] = True

        try:
            response = requests.post(Central_API+'/api/post_printer_info', json=json_)
            print(response.json(),response.status_code)
        except requests.exceptions.RequestException as e:
            print("Error posting to Central API:", e)

        if response.json()['status'] == "Authentication Failure" and recheck == False:
            Unify_Plugin()
            prusa_monitoring(printer_name,recheck=True)
        
        elif response.json()['status'] == "Authentication Failure" and recheck == True:
            if prusalink_printer_job_file != {} or 'job' in prusalink_printer_status:
                print("Deleting Job")
                send_delete_to_prusalink(printerHost,API_key, prusalink_printer_job_path+'/'+(str(prusalink_printer_job_file['id']) if 'id' in prusalink_printer_job_file else str(prusalink_printer_status['job']['id'])))
            else:
                print("No Job to delete")
            event_schedule.enter(time_between_checks, 1, prusa_monitoring, argument=(printer_name,))
            
        else:
            event_schedule.enter(time_between_checks, 1, prusa_monitoring, argument=(printer_name,))


#Function to send a delete request to prusalink in case of invalid job
def send_delete_to_prusalink(printer_host, API_key, path):
    try:
        r = requests.delete('http://' + printer_host + path, headers = {'X-Api-Key': API_key})
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("Error sending delete request to prusalink")


def Unify_Plugin():
    unify_token = "rCXGdBZEwi/Vme2qJruexg"

    unify_headers = {"Authorization": "Bearer rCXGdBZEwi/Vme2qJruexg", "accept": "application/json", "content-type": "application/json"}


    try:
        unify_cards = requests.get("https://192.168.1.168:12445/api/v1/developer/credentials/nfc_cards/tokens", headers=unify_headers,timeout=30, verify=False)
        cards = unify_cards.json()
    except requests.exceptions.RequestException as e:
        print("Error getting NFC cards from Unify:", e)
        cards = []
        
    try:

        unify_users = requests.get("https://192.168.1.168:12445/api/v1/developer/users", headers=unify_headers,timeout=30, verify=False)

        users = unify_users.json()
    except requests.exceptions.RequestException as e:
        print("Error getting users from Unify:", e)
        users = []



    if users == [] or cards == []:
        print("No users or cards found in Unify, skipping posting to Central API")
        return
    
    try:
        response = requests.post(Central_API+'/api/post_unify_info/cards', json=cards)
        print(response.json(),response.status_code)
    except requests.exceptions.RequestException as e:
        print("Error posting to Central API:", e)

    try:
        response = requests.post(Central_API+'/api/post_unify_info/users', json=users)
        print(response.json(),response.status_code)
    except requests.exceptions.RequestException as e:
        print("Error posting to Central API:", e)
    



    '''for i in json_r['data']:
        if i["nfc_id"] == UID:
            return True
    return False'''

def prusa_monitoring_scheduler():

    event_schedule.enter(time_between_checks, 1, prusa_monitoring, argument=(Printer4,))
    event_schedule.enter(time_between_checks, 1, prusa_monitoring, argument=(Printer5,))
    event_schedule.enter(time_between_checks, 1, prusa_monitoring, argument=(Printer6,))
    event_schedule.enter(time_between_checks, 1, bambu_monitoring, argument=(Printer7,))
    event_schedule.enter(time_between_checks, 1, bambu_monitoring, argument=(Printer8,))


    event_schedule.run()

time_between_checks = 60 # seconds
#Printer List
Printer4 = "iStartLab4"
Printer5 = "iStartLab5"
Printer6 = "iStartLab6"
Printer7 = "iStartLab7"
Printer8 = "iStartLab8"

Unify_Plugin()
prusa_monitoring_scheduler()
