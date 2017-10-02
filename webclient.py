import http.client, urllib.parse, urllib.request, time, json, argparse, sys, random, datetime
from pprint import pprint



'''
def getTask(conn,taskID):
    for x in range(3):
        print('x = %d\n' % (x)) 
        data = {'TaskID' : taskID,
             'Progress' : x
        }

        url_values = urllib.parse.urlencode(data)
        print(url_values)  # The order may differ from below.  
        full_url = '/' + '?' + url_values
        #data = urllib.request.urlopen(full_url)

        conn.request("GET", "/task/get", urllib.parse.urlencode(data))
        response = conn.getresponse()
        print(response.status, response.reason)
        pprint(vars(response))
        data = response.read()  # This will return entire content.
        try:
            json_object = json.loads(str(data, "utf-8"))
            print(json_object)
        except ValueError:
            print("It is a direct command")
        #print(data)
        time.sleep(6)
    else:
        print('Final x = %d\n' % (x))
        conn.close()
'''

def process_task(data):
    time.sleep(10)
    result_id = random.randrange(1000,9999)
    return result_id, data

def send(url, data_id, data):
    global conn
    data_structure = {'instance_id': instance_id, 'task_id': task_id, 'data_id': data_id, 'data': data}  
    params = urllib.parse.urlencode(data_structure)
    headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
    conn.request("POST", url, params, headers)
    response = conn.getresponse()
    response_data = response.read()  # This will return entire content.
    print(response.status, response.reason)
    return response_data

def send_result(result_id, result):
    return send("/task/result",result_id, result)

def send_finished():
    finished_at = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return send("/task/finished",0, finished_at)

def send_log(result):
    return 

def get_task():
    global conn, task_id
    data = None
    task_data = None
    try:
        conn.request("GET", "/task/get")
        response = conn.getresponse()
        print(response.status, response.reason)
        data = response.read()  # This will return entire content.
    except:
        return False, "reconnect"
    print("data:" + str(data))


    try:
        data_as_json = json.loads(str(data, "utf-8"))
        print("data_as_json : " + str(data_as_json))
        task_id = data_as_json["task_id"]
        print("TaskID:" + task_id)
        task_data = data_as_json["data"]
        print("task_data : " + str(task_data))
        json_object = json.loads(task_data)
        print("I got a new task:")
        print(json_object)
        print("-----------------------------------------------------")
        return True, json_object
        #do the task

    except ValueError:
        task_data_str = str(data, "utf-8")
        print("It is a direct command :" + task_data_str  + ":")
        print("-----------------------------------------------------")
        return False, task_data_str

def post(taskID):
    global conn
    headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}  
    for x in range(5):
        print('x = %d\n' % (x)) 

        params = urllib.parse.urlencode({'TaskID': taskID, 'Progress': x})
        conn.request("POST", "", params, headers)
        response = conn.getresponse()
        data = response.read()  # This will return entire content.
        print(response.status, response.reason)
        print(data)
        time.sleep(6)
    else:
        print('Final x = %d\n' % (x))
        conn.close()

def process_command(data):
    if (data == "shutdown_now"):
        print("No more tasks, good ni.....Zzzz :)")
        conn.close()
        sys.exit()
    elif (data == "reconnect"):
        print("Connection lost, trying to reconnect to server ...)")
        connect()
    return

def connect():
    global server, port
    url =  server + ":" + str(port)
    print("Trying to connect to " + url)
    index = 0
    global conn
    while True:
        try:
            conn = http.client.HTTPConnection(url)
            conn.connect()
            print(conn)
            break
        except:
            print("Try " + str(index) + ": Connection failed to the server's URL " + url)
            index += 1
            time.sleep(5)
    print("Connected to " + url + " successfully !")

def run():
    connect() 
    while True:      
        is_task, data = get_task()
        if (is_task):
            result_id, result = process_task(data)
            send_result(result_id, result)
            send_finished()
        else:
            result = process_command(data)

def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
         raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue

def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server"  , help="HTTP Server Address", required=True)
    parser.add_argument("--port"  , help="HTTP Server port, default = 8777",  type=check_positive)
    parser.add_argument("--instance"  , help="The instance ID, it will be to identify this instance ", required=True)
    return parser.parse_args()

if __name__ == "__main__":
    server = None
    port = 8777
    conn = None
    instance_id = None
    task_id = None
    args = getArgs()
    print(args)
    server = args.server
    port = args.port if (args.port != None) else 8777
    instance_id = args.instance
    run()




