import http.client, urllib.parse, urllib.request, time, json, argparse, sys, random, datetime
from pprint import pprint
import netifaces
from threading import Thread, Lock


lock = Lock()

def get_ips():
    """load ip addresses with netifaces"""
    local_ips = []
    public_ips = []
    
    # list of iface names, 'lo0', 'eth0', etc.
    for iface in netifaces.interfaces():
        # list of ipv4 addrinfo dicts
        ipv4s = netifaces.ifaddresses(iface).get(netifaces.AF_INET, [])
        for entry in ipv4s:
            addr = entry.get('addr')
            #print("addr: " + addr)
            if not addr:
                continue
            if not (iface.startswith('lo') or addr.startswith('127.')):
                public_ips.append(addr)
            else:
                local_ips.append(addr)        
    return local_ips, public_ips


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

def send(url, *args):
    global conn, replica_id, task_id
    packet = {"replica_id": replica_id}
    data = {}
    for x in range(len(args)):
        print("****************************************")
        print(args[x])
        print("****************************************")
        for key in args[x]:
            #print(str(key) + ":" + str(args[x][key]))
            data[key] = args[x][key]
    #, 'task_id': task_id, 'data_id': data_id, 'data': data}
    packet["data"] = data 
    print("packet: " + str(packet))
    params = urllib.parse.urlencode(packet)
    #params = json.dumps(packet).encode('utf-8')
    headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
    lock.acquire()
    try:
        conn.request("POST", url, params, headers)
        response = conn.getresponse()
        response_data = response.read()  # This will return entire content.
        lock.release() #release lock
        print(response.status, response.reason)
        return response_data
    except:
        lock.release() #release lock
        print("Connection lost")
        return ""

def send_result(*args):
    return send("/task/result",*args)

def send_finished():
    global task_id
    finished_at = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return send("/task/finished",{"task_id": task_id, "finished_at": finished_at})

def send_log(result):
    return 

def get_task():
    global conn, task_id, replica_id
    data = None
    request_data = {'replica_id' : replica_id}
    try:
        #url_values = urllib.parse.urlencode(request_data)
        #print(url_values)  # The order may differ from below.  
        #full_url = '/' + '?' + url_values
        #data = urllib.request.urlopen(full_url)

        conn.request("GET", "/task/get", urllib.parse.urlencode(request_data))


        #conn.request("GET", "/task/get")
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

        params = urllib.parse.urlencode({"TaskID": taskID, "Progress": x})
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
    global finished, conn_status
    if (data == "shutdown_now"):
        print("No more tasks, good ni.....Zzzz :)")
        time.sleep(5)
        '''
        conn_status = 3 # connection terminated
        conn.close()
        sys.exit()
        '''
    elif (data == "reconnect"):
        print("Connection lost, trying to reconnect to server ...)")
        connect()
    return

def register():
    local, public = get_ips()
    global conn
    while True:
        try:
            conn.request("GET", "/replica/register")
            response = conn.getresponse()
            print(response.status, response.reason)
            data = response.read()  # This will return entire content.
            data_as_json = json.loads(str(data, "utf-8"))
            print("data_as_json : " + str(data_as_json))
            replica_id = data_as_json["replica_id"]
            print("replica_id:" + replica_id)
            print("-----------------------------------------------------")
            return replica_id
        except:
            connect()


def connect():
    global server, port, conn, conn_status
    url =  server + ":" + str(port)
    print("Trying to connect to " + url)
    index = 0
    while True:
        try:
            conn = http.client.HTTPConnection(url)
            conn.connect()
            print(conn)
            conn_status = 1 # Connected
            break
        except:
            print("Try " + str(index) + ": Connection failed to the server's URL " + url)
            index += 1
            conn_status = 0 # disconnected
            time.sleep(5)
    print("Connected to " + url + " successfully !")

def still_alive():
    global finished, conn_status
    while (conn_status != 3):
        print("conn_status = " + str(conn_status))
        if (conn_status == 1):
            url = "/replica/still_alive"
            print("Sending Still Alive Message " + url)
            response = send(url,{"still_alive": time.time()})
            print(response)
        time.sleep(10)

def run():
    global replica_id
    connect() 
    replica_id = register()
    still_alive_thread = Thread(target=still_alive)
    still_alive_thread.start()
    while True:      
        is_task, data = get_task()
        if (is_task):
            result_id, result = process_task(data)
            send_result({"task_id": task_id, "result_id": str(result_id), "result": result})
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
    #parser.add_argument("--replica"  , help="The instance ID, it will be to identify this instance ", required=True)
    return parser.parse_args()

if __name__ == "__main__":
    server = None
    port = 8777
    conn = None
    replica_id = None
    task_id = None
    finished = False
    conn_status = 0 # disconnected
    args = getArgs()
    print(args)
    server = args.server
    port = args.port if (args.port != None) else 8777
    run()




