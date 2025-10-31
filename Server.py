from flask import Flask, request, jsonify
import requests
import json
import time
import pyrebase

first_layer_verification = False



global TB_Token
global token_gen_time
global attention_counter

# Prusalink API
prusalink_printer_info_path = "/api/v1/info"
prusalink_printer_status_path = "/api/v1/status"
prusalink_printer_job_path = "/api/v1/job"
prusalink_printer_cameras_path = "/api/v1/cameras"




# Printer Example
global iStartLab6_df
global iStartLab6_nr_of_consecutive_empty_json
global iStartLab6_monitoring_status
global iStartLab6_curr_job_name
global iStartLab6_curr_job_file_path
global iStartLab6_printer_name
global iStartLab6_printer_type
global iStartLab6_API_key
global iStartLab6_host
global iStartLab6_printer_serial

iStartLab6_host = "192.168.88.239"
iStartLab6_printer_serial = "SERIAL_HERE"
iStartLab6_API_key = ""
iStartLab6_printer_name = "iStartLab6"
iStartLab6_printer_type = "Prusa"
iStartLab6_curr_job_name = ""
iStartLab6_curr_job_file_path = ""
iStartLab6_monitoring_status = 0 
iStartLab6_nr_of_consecutive_empty_json = 0
iStartLab6_printer_tb_id = "ID_HERE"
iStartLab6_printer_tb_access_token = "TOKEN_HERE"

#switch Example
switch1_switch_name = "Switch1"
switch1_switch_tb_id = "ID_HERE"
switch1_switch_tb_access_token = "TOKEN_HERE"


class Printer:
    def __init__(self, printer_name, printer_type, printer_tb_id, printer_host,printer_serial, API_key,access_token = None):
        self.printer_name = printer_name
        self.printer_type = printer_type
        self.printer_tb_id = printer_tb_id
        self.printer_host = printer_host
        self.printer_serial = printer_serial
        self.API_key = API_key
        self.curr_job_name = ""
        self.curr_job_file_path = ""
        self.monitoring_status = 0
        self.nr_of_consecutive_empty_json = 0
        self.access_token = access_token



iStartLab6 = Printer(iStartLab6_printer_name, iStartLab6_printer_type, iStartLab6_printer_tb_id, iStartLab6_host, iStartLab6_printer_serial, iStartLab6_API_key, iStartLab6_printer_tb_access_token)



class Switch:
    def __init__(self, switch_name, switch_tb_id, access_token):
        self.switch_name = switch_name
        self.switch_tb_id = switch_tb_id
        self.access_token = access_token

Switch1 = Switch(switch1_switch_name, switch1_switch_tb_id, switch1_switch_tb_access_token)
# Create a list of switches
switch_list = [Switch1]
# Create a list of printers
printer_list = [ iStartLab6]

#Make sure to set the Unify variable to True if you want to use the Unify Plugin
Unify = True

# Firebase configuration
config = {
  "apiKey": "",
  "authDomain": "",
  "databaseURL": "",
  "storageBucket": ""
}

# Initialize Firebase
firebase = pyrebase.initialize_app(config)
db = firebase.database()

# Get the Thingsboard token

#Thingsboard token generator
def getToken():
    username = ""
    password = ""
    
    url = ""
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    loginJSON = {"username": username, "password": password}
    #print(loginJSON)
    tokenAuthResp = requests.post(url, headers=headers, json=loginJSON)
    #print(tokenAuthResp)
    data = tokenAuthResp.json()
    token = data['token']
    #print(token)
    return token


TB_Token = getToken()
token_gen_time = time.time()  # Initialize token generation time

app = Flask(__name__) # create an instance of the Flask class

#Route to get printer current status
@app.route('/api/post_printer_info', methods=['POST'])
def post_printer_info():
    global TB_Token
    global token_gen_time
    global attention_counter

    if (time.time() - token_gen_time) > 600:
        TB_Token = getToken()
        token_gen_time = time.time()

    printerID = None
    # Get the printer information from the request
    printerName = request.json['printerName']

    print(f"PRINTER: {printerName} \n")

    #Check if printer is in the list to extract TB ID
    for printer in printer_list:
        if printer.printer_name == printerName:
            printerID = printer.printer_tb_id
            printer_host = printer.printer_host
            API_key = printer.API_key
            TB_Access_Token = printer.access_token
            printer_type = printer.printer_type


    if printerID == None:
        return jsonify({"status": "failure", "message": "Printer not found"}), 404

    #Check current status of the printer
    printerStatus = request.json['printerStatus']
    currentJob = request.json['currentJob']
    jobID = request.json['jobID']
    jobProgress = request.json['jobProgress']
    TimeRemaining = request.json['TimeRemaining']

    

    #"https://iot.istartlab.tecnico.ulisboa.pt/api/v1/"+TB_Access_Token+"/telemetry"
    #"https://iot.istartlab.tecnico.ulisboa.pt/api/plugins/telemetry/DEVICE/"+printerID+"/timeseries/ANY"


    #Create TB URL with printer ID to post telemetry
    deviceurl = "https://iot.istartlab.tecnico.ulisboa.pt/api/v1/"+TB_Access_Token+"/telemetry"

    #Store in Thingsboard
    tkn = TB_Token
    my_headers = {"X-Authorization": "Bearer " + tkn, "Content-Type": "application/json"}

    TB_Response = requests.post(deviceurl, headers=my_headers, json={"DEAD": False})

    tburl = "https://iot.istartlab.tecnico.ulisboa.pt/api/plugins/telemetry/DEVICE/"+printerID+"/values/timeseries?keys={,UID,printerStatus,jobStatus,First_Layer,Job_Owner_Name,Job_Owner_ID,Job_Owner_Phone,}"
    # Get the printer information from the request 
    json = requests.get(tburl, headers=my_headers)
    data = json.json()

    

    reset = reset_validity(printerID,currentJob,printerStatus,TB_Access_Token)
    print(printerStatus)

    get_telemetry_url = "https://iot.istartlab.tecnico.ulisboa.pt/api/plugins/telemetry/DEVICE/"+printerID+"/values/timeseries?keys=Job_Owner_ID,Job_Owner_Name,Job_Owner_Phone,"
    try:
        telemetry_response = requests.get(get_telemetry_url, headers=my_headers)
        telemetry_data = telemetry_response.json()
        user_id = telemetry_data['Job_Owner_ID'][0]['value'] if 'Job_Owner_ID' in telemetry_data else ""
        user_name = telemetry_data['Job_Owner_Name'][0]['value'] if 'Job_Owner_Name' in telemetry_data else ""
    except Exception as e:
        print(f"Error fetching telemetry data: {e}")
        user_id = ""
        user_name = ""

    if printerStatus == "IDLE":
        attention_counter = 0
        currentJob = ""
        

        json = { 
        "printerStatus" : printerStatus,
        "currentJob" : currentJob,
        "jobProgress" : jobProgress,
        "Estimated Finish Time" : "N/A",
        "Job_Owner_ID" : data['Job_Owner_ID'][0]['value'],
        "Job_Owner_Name" : data['Job_Owner_Name'][0]['value'],
        "Job_Owner_Phone" : data['Job_Owner_Phone'][0]['value'],
        }
        
        try:
            response = requests.post(deviceurl,headers=my_headers,json=json)
        except:
            return jsonify({"status": "Failure", "message": "Printer Status Update Failed"}), 500
        
        return jsonify({"status": "Success", "message": "Printer Status Updated"}), 200


    elif printerStatus == "ERROR":
        attention_counter = 0

        json = { 
        "printerStatus" : printerStatus,
        "currentJob" : currentJob,
        "jobProgress" : jobProgress,
        "Job_Owner_ID" : data['Job_Owner_ID'][0]['value'],
        "Job_Owner_Name" : data['Job_Owner_Name'][0]['value'],
        "Job_Owner_Phone" : data['Job_Owner_Phone'][0]['value'],
        "Estimated Finish Time" : "N/A",
        }
        
        try:
            response = requests.post(deviceurl,headers=my_headers,json=json)
        except:
            return jsonify({"status": "Authentication Failure", "message": "Printer Status Update Failed"}), 500
        
        return jsonify({"status": "Authentication Failure", "message": "Printer Error"}), 200

    elif printerStatus == "ATTENTION":

        prev_state = requests.get("https://iot.istartlab.tecnico.ulisboa.pt/api/plugins/telemetry/DEVICE/"+printerID+"/values/timeseries?keys=printerStatus", headers=my_headers)

        if prev_state.json()['printerStatus'][0]['value'] == "ATTENTION":
            attention_counter += 1 if attention_counter != 0 else 1
        else:
            attention_counter = 1

        

        
        if attention_counter == 480:


            json = { 
            "printerStatus" : printerStatus,
            "currentJob" : currentJob,
            "jobProgress" : jobProgress,
            "Job_Owner_ID" : data['Job_Owner_ID'][0]['value'],
            "Job_Owner_Name" : data['Job_Owner_Name'][0]['value'],
            "Job_Owner_Phone" : data['Job_Owner_Phone'][0]['value'],
            "Estimated Finish Time" : "N/A",
            }
            
            try:
                response = requests.post(deviceurl,headers=my_headers,json=json)
            except:
                return jsonify({"status": "Failure", "message": "Printer Status Update Failed"}), 500


            return jsonify({"status": "Authentication Failure", "message": "Printer Status Updated, but Attention Counter Exceeded"}), 500
        
        elif attention_counter == 481:
            
            json = { 
            "printerStatus" : "ERROR",
            "currentJob" : currentJob,
            "jobProgress" : jobProgress,
            "Job_Owner_ID" : data['Job_Owner_ID'][0]['value'],
            "Job_Owner_Name" : data['Job_Owner_Name'][0]['value'],
            "Job_Owner_Phone" : data['Job_Owner_Phone'][0]['value'],
            "Estimated Finish Time" : "N/A",
            }

            attention_counter = 0
            
            try:
                response = requests.post(deviceurl,headers=my_headers,json=json)
            except:
                return jsonify({"status": "Failure", "message": "Printer Status Update Failed"}), 500

            return jsonify({"status": "Authentication Failure", "message": "Printer Status Updated, but Attention Counter Exceeded"}), 200
        
        else:

            json = { 
            "printerStatus" : printerStatus,
            "currentJob" : currentJob,
            "jobProgress" : jobProgress,
            "Job_Owner_ID" : data['Job_Owner_ID'][0]['value'],
            "Job_Owner_Name" : data['Job_Owner_Name'][0]['value'],
            "Job_Owner_Phone" : data['Job_Owner_Phone'][0]['value'],
            "Estimated Finish Time" : "N/A",
            }            

            try:
                response = requests.post(deviceurl,headers=my_headers,json=json)
            except:
                return jsonify({"status": " Failure", "message": "Printer Status Update Failed"}), 500

            return jsonify({"status": "Success", "message": "Printer Status Updated"}), 200
        
    elif printerStatus == "STOPPED":

        attention_counter = 0

        json = { 
        "printerStatus" : printerStatus,
        "currentJob" : currentJob,
        "jobProgress" : jobProgress,
        "Job_Owner_ID" : data['Job_Owner_ID'][0]['value'],
        "Job_Owner_Name" : data['Job_Owner_Name'][0]['value'],
        "Job_Owner_Phone" : data['Job_Owner_Phone'][0]['value'],
        "Estimated Finish Time" : "N/A",
        }
        
        try:
            response = requests.post(deviceurl,headers=my_headers,json=json)
        except:
            return jsonify({"status": "Failure", "message": "Printer Status Update Failed"}), 500
        
        return jsonify({"status": "Success", "message": "Printer Status Updated"}), 200
        
    if printerStatus == "PAUSED":
        attention_counter = 0

        

        

        json = {
        "printerStatus" : printerStatus,
        "jobProgress" : jobProgress,
        "currentJob" : currentJob,
        "Job_Owner_ID" : data['Job_Owner_ID'][0]['value'],
        "Job_Owner_Name" : data['Job_Owner_Name'][0]['value'],
        "Job_Owner_Phone" : data['Job_Owner_Phone'][0]['value'],
        "Estimated Finish Time" : "N/A",
        }

        try:
            response = requests.post(deviceurl,headers=my_headers,json=json)

        except:

            return jsonify({"status": "Failure", "message": "Printer Status Update Failed"}), 500
        
        return jsonify({"status": "Success", "message": "Printer Status Updated"}), 200

    if printerStatus != "PRINTING" and printer_type == "BambuLabs":

        json = { 
        "printerStatus" : printerStatus,
        "currentJob" : currentJob,
        "jobProgress" : jobProgress,
        "Estimated Finish Time" : "N/A",
        "Job_Owner_ID" : data['Job_Owner_ID'][0]['value'],
        "Job_Owner_Name" : data['Job_Owner_Name'][0]['value'],
        }
        
        try:
            response = requests.post(deviceurl,headers=my_headers,json=json)
        except:
            return jsonify({"status": "Failure", "message": "Printer Status Update Failed"}), 500
        
        return jsonify({"status": "Success", "message": "Printer Status Updated"}), 200

        
        return

    validation,user_id,user_name = validate_job(printerID,printerStatus,TB_Access_Token,printer_type)
    if validation == False:
        currentJob = ""
        printerStatus = "IDLE due to Authentication Failure" if printer_type == "Prusa" else "PRINTING"
        user_id = "NO ID"
        user_name = "INVALID USER"
  

    if TimeRemaining != -1:
        estimated_finish_time = time.localtime((time.time() + int(TimeRemaining)))
        estimated_finish_time = time.asctime(estimated_finish_time)
        time_params = str(estimated_finish_time).split(" ")

        if "" in time_params:
            time_params.remove("")
        hours_min = time_params[3].split(":")
        print(estimated_finish_time)
        print(time_params)
        print(hours_min)

        estimated_finish_time = time_params[0] +" "+ time_params[1]+" " + time_params[2]+" " + hours_min[0] + ":" + hours_min[1]


    id = user_id.split("-")[0] if "-" in user_id else user_id
    user_phone = user_id.split("-")[1] if "-" in user_id else "No Phone Number"

    attention_counter = 0
    
    json = { 
        "printerStatus" : printerStatus,
        "currentJob" : currentJob,
        "jobProgress" : jobProgress,
        "Job_Owner_ID" :id,
        "Job_Owner_Phone" : user_phone,
        "Job_Owner_Name" : user_name if user_name != "" else "IStartLab",
        "Estimated Finish Time" : estimated_finish_time if TimeRemaining != -1 else "N/A",
        }

    response = requests.post(deviceurl,headers=my_headers,json=json)

    #print(f"RESET for {printerName}:{reset}  Validation: {validation}\n")

    for printer in printer_list:
        if printer.printer_name == printerName:
            printer.curr_job_name = currentJob




    if reset == True and validation == True:
        return jsonify({"status": "Success", "message": "Job Validated and Printer Status Updated"}), 200
    
    elif reset == True and validation == False:
        return jsonify({"status": "Authentication Failure", "message": "Job Invalidated and Printer Status Updated"}), 200

    elif validation == False and reset == False:
        return jsonify({"status": "Authentication Failure", "message": "Authentication Failed"}),200

    else:
        return jsonify({"status": "Success", "message": "Authentication Succeeded"}), 200

#Route to get printer information
@app.route('/api/get_printer_info/<printerName>', methods=['GET'])
def get_printer_info(printerName):

    #Check if printer is in the list to extract TB ID
    for printer in printer_list:
        if printer.printer_name == printerName:
            if printer.printer_type == "Prusa":
                return jsonify({"printerHost": printer.printer_host, "API_key": printer.API_key, "Prusalink_Status_Path": prusalink_printer_status_path, "Prusalink_Job_Path": prusalink_printer_job_path}), 200
            elif printer.printer_type == "BambuLabs":
                return jsonify({"printerHost": printer.printer_host, "API_key": printer.API_key, "printerSerial": printer.printer_serial}), 200

    return jsonify({"status": "failure", "message": "Printer not found"}), 404

#Route to declare a printer as dead
@app.route('/api/declare_dead/<printerName>', methods=['POST'])
def declare_dead(printerName):
    for printer in printer_list:
        if printer.printer_name == printerName:
            printerID = printer.printer_tb_id
            TB_Access_Token = printer.access_token
            
    tkn = TB_Token

    json = { 
            "printerStatus" : "OFFLINE",
            "currentJob" : "No Job",
            "jobProgress" : 0,
            "Job_Owner_ID" : "N/A",
            "Job_Owner_Name" : "N/A",
            "Job_Owner_Phone" : "N/A",
            "Estimated Finish Time" : "N/A",
            "DEAD" : True,
            }
    
    my_headers = {"X-Authorization": "Bearer " + tkn, "Content-Type": "application/json"}
    TB_Response = requests.post("https://iot.istartlab.tecnico.ulisboa.pt/api/v1/"+TB_Access_Token+"/telemetry", headers=my_headers, json=json)
    if TB_Response.status_code == 200:
        return jsonify({"status": "Success", "message": "Printer Declared Dead"})

#Route to get Thingsboard Info for printer
@app.route('/api/get_printer_tb_info/<printerName>', methods=['GET'])
def get_printer_tb_info(printerName):
        #Check if printer is in the list to extract TB ID
    for printer in printer_list:
        if printer.printer_name == printerName:
            return jsonify({"tb_id":printer.printer_tb_id}), 200


    return jsonify({"status": "failure", "message": "Printer not found"}), 404

#Route where the ESP32 will send the UID
@app.route('/api/post_UID/<printerName>', methods=['POST'])
def post_UID(printerName):
    # Get the UID from the request
    UID = request.data
    strUID = str(UID, encoding='utf-8')
    params = strUID.split(" ")
    final_UID = ""
    final_UID += params[1]
    final_UID += params[2]
    final_UID += params[3]
    final_UID += params[4]
    #print(final_UID.upper())
    json = { "UID" : final_UID.upper()}
    first_layer = False

    #Check if printer is in the list to extract TB ID
    for printer in printer_list:
        if printer.printer_name == printerName:
            printerID = printer.printer_tb_id
            TB_Access_Token = printer.access_token
    if printerID == None:
        return jsonify({"status": "failure", "message": "Printer not found"}), 404


    validation,user_id,user_name = Unify_Plugin(final_UID.upper())

    deviceurl = "https://iot.istartlab.tecnico.ulisboa.pt/api/v1/"+TB_Access_Token+"/telemetry"
   
    #Store in Thingsboard
    tkn = TB_Token
    my_headers = {"X-Authorization": "Bearer " + tkn, "Content-Type": "application/json"}

    response_post = requests.post(deviceurl,headers=my_headers,json=json)




    if(validation == True):
        return jsonify({"status": "success", "message": "UID stored successfully"}), 200
    else:
        return jsonify({"status": "failure", "message": "UID not valid"}), 404



@app.route('/api/post_UID_switch/<switch_name>', methods=['POST'])
def post_UID_switch(switch_name):
# Get the UID from the request
    UID = request.data
    strUID = str(UID, encoding='utf-8')



    #Check if printer is in the list to extract TB ID
    for switch in switch_list:
        if switch.switch_name == switch_name:
            switchID = switch.switch_tb_id
            TB_Access_Token = switch.access_token
    if switch == None:
        return jsonify({"status": "failure", "message": "Switch not found"}), 404

    if strUID == "OFF":
        try: 
            deviceurl = "https://iot.istartlab.tecnico.ulisboa.pt/api/v1/"+TB_Access_Token+"/telemetry"
   
            #Store in Thingsboard
            tkn = TB_Token
            my_headers = {"X-Authorization": "Bearer " + tkn, "Content-Type": "application/json"}
            json = {"UID": "", "switchStatus": "OFF"}
            response_post = requests.post(deviceurl,headers=my_headers,json=json)
            return jsonify({"status": "success", "message": "Switch turned OFF"}), 200
        except:
            return jsonify({"status": "failure", "message": "Switch OFF failed"}), 500


    
    params = strUID.split(" ")
    final_UID = ""
    final_UID += params[1]
    final_UID += params[2]
    final_UID += params[3]
    final_UID += params[4]
    #print(final_UID.upper())
    
    first_layer = False

    


    validation,user_id,user_name = Unify_Plugin(final_UID.upper())

    id = user_id.split("-")[0] if "-" in user_id else user_id
    user_phone = user_id.split("-")[1] if "-" in user_id else "No Phone Number"

    deviceurl = "https://iot.istartlab.tecnico.ulisboa.pt/api/v1/"+TB_Access_Token+"/telemetry"
   
    #Store in Thingsboard
    tkn = TB_Token
    my_headers = {"X-Authorization": "Bearer " + tkn, "Content-Type": "application/json"}
    json = { "UID" : final_UID.upper(), "switchStatus": "ON", "User_ID": id, "User_Name": user_name, "Job_Owner_Phone": user_phone}
    response_post = requests.post(deviceurl,headers=my_headers,json=json)




    if(validation == True):
        return jsonify({"status": "success", "message": "UID stored successfully"}), 200
    else:
        return jsonify({"status": "failure", "message": "UID not valid"}), 404

#Function to check if the UID is valid using the Unify Plugin
def Unify_Plugin(UID):

    #Check local Unify Table
    with open('cards.txt','r') as cards_file:
        cards = cards_file.read()
        cards = json.loads(cards)
        cards_file.close()

    #Check local Unify Table
    with open('users.txt','r') as users_file:
        users = users_file.read()
        users = json.loads(users)
        users_file.close()

    

    #Check if UID is in the Unify Table
    for card in cards['data']:
        if card['nfc_id'] == UID:
            for user in users['data']:
                if user['id'] == card['user_id']:
                    user_id = user['employee_number']
                    user_name = user['full_name']
                    return True,user_id,user_name
    return False,"",""

#Route to post the unify registered cards table
@app.route('/api/post_unify_info/<data_type>', methods=['POST'])
def post_unify_info(data_type):
    json_ = request.json
    json_ = json.dumps(json_)

    with open(data_type+'.txt', 'w') as data_file:
        data_file.write(json_)
        data_file.close()
    return jsonify({"status": "success", "message": "Unify Table updated successfully"}), 200



#Reset the validity of the job
def reset_validity(printerID,currentJob,printerStatus,TB_Access_Token):

    tkn = TB_Token
    my_headers = {"X-Authorization": "Bearer " + tkn, "Content-Type": "application/json"}
    tburl = "https://iot.istartlab.tecnico.ulisboa.pt/api/plugins/telemetry/DEVICE/"+printerID+"/values/timeseries?keys={UID,printerStatus,jobStatus,currentJob,}"
    # Get the printer information from the request 
    json = requests.get(tburl, headers=my_headers)
    data = json.json()


    
    if printerStatus == "IDLE":
        response = requests.post("https://iot.istartlab.tecnico.ulisboa.pt/api/v1/"+TB_Access_Token+"/telemetry", headers=my_headers, json={"jobStatus": "INVALID"})
        return True
    

    if data['currentJob'][0]['value'] != currentJob:
        response = requests.post("https://iot.istartlab.tecnico.ulisboa.pt/api/v1/"+TB_Access_Token+"/telemetry", headers=my_headers, json={"jobStatus": "INVALID"})
        return True

    return False
#Function to validate the job
def validate_job(printerID,printerStatus,TB_Access_Token,printer_type):

    
    tkn = TB_Token
    my_headers = {"X-Authorization": "Bearer " + tkn, "Content-Type": "application/json"}
    tburl = "https://iot.istartlab.tecnico.ulisboa.pt/api/plugins/telemetry/DEVICE/"+printerID+"/values/timeseries?keys={,UID,printerStatus,jobStatus,First_Layer,Job_Owner_Name,Job_Owner_ID,Job_Owner_Phone,}"
    # Get the printer information from the request 
    json = requests.get(tburl, headers=my_headers)
    data = json.json()

    '''print(data['jobStatus'][0]['ts'])
    print((time.time() - 1200)*1000)
    print(data['First_Layer'][0]['value'])'''

    if data['First_Layer'][0]['value'] == "false" and data['jobStatus'][0]['ts'] < (time.time() - 900)*1000 and data['jobStatus'][0]['value'] == "VALID" and first_layer_verification == True:
        print("Fisrt LAYER NOT WATCHED")
        return False,"",""
        
    #Check if current job has been previously validated
    if data['jobStatus'][0]['value'] == "VALID":
        if (data['UID'][0]['ts'] - data['jobStatus'][0]['ts']) > 600*1000 and data['First_Layer'][0]['value'] == False and first_layer_verification == True:
            Check_First_Layer = request.post("https://iot.istartlab.tecnico.ulisboa.pt/api/v1/"+TB_Access_Token+"/telemetry", headers=my_headers, json={"First_Layer": True})
            return True,data['Job_Owner_ID'][0]['value']+'-'+data["Job_Owner_Phone"][0]['value'],data['Job_Owner_Name'][0]['value']
        
        return True,data['Job_Owner_ID'][0]['value']+"-"+data["Job_Owner_Phone"][0]['value'],data['Job_Owner_Name'][0]['value']

    # Check if the printer is in a valid state
    elif printerStatus == "PRINTING" or printerStatus == "BUSY":
        # Check if the UID is valid
        if data['UID'][0]['ts'] > (time.time() - 300)*1000:

            #Check if UID is valid
            if Unify == True:
                validation,user_id,user_name = Unify_Plugin(data['UID'][0]['value'])
                if validation == True:
                    TB_Response = requests.post("https://iot.istartlab.tecnico.ulisboa.pt/api/v1/"+TB_Access_Token+"/telemetry", headers=my_headers, json={"jobStatus": "VALID"})
                    if TB_Response.status_code == 200:
                        return True,user_id,user_name

            else:
                if db.child("Users").child(data['UID'][0]['value']).get() == True:
                    user_id = db.child("Users").child(data['UID'][0]['value']).child("employee_number").get().val()
                    user_name = db.child("Users").child(data['UID'][0]['value']).child("full_name").get().val()
                    TB_Response = requests.post("https://iot.istartlab.tecnico.ulisboa.pt/api/v1/"+TB_Access_Token+"/telemetry", headers=my_headers, json={"jobStatus": "VALID"})
                    if TB_Response.status_code == 200:
                        return True,user_id,user_name
            
            
            
            return False,"",""

        else:
            return False,"",""
        

        
    else:
        return False,"",""

#Route to get all users
@app.route('/api/get_users', methods=['GET'])
def get_users():
    return 

@app.route('/api/get_user/<istid>', methods=['GET'])
def get_user(istid):
    # Check if the user exists in the database
    return
    

#Route to check if user is inside the room
@app.route('/api/user_in_room', methods=['GET'])
def user_in_room():
    return

@app.route('/api/thingsboard_info/<printerName>', methods=['GET'])
def get_thingsboard_info(printerName):
    # Get the Thingsboard token
    global TB_Token
    global token_gen_time

    if (time.time() - token_gen_time) > 600:
        TB_Token = getToken()
        token_gen_time = time.time()

    for printer in printer_list:
        if printer.printer_name == printerName:
            return jsonify({
                "TB_Token": TB_Token,
                "printer_tb_id": printer.printer_tb_id,
                "printer_tb_access_token": printer.access_token
            }), 200
        
    return jsonify({"status": "failure", "message": "Printer not found"}), 404

    

if __name__ == '__main__':
    app.run(host='192.168.88.16',port=5000,debug=True)