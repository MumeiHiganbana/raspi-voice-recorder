import hashlib
import sys
import time
import paho.mqtt.client as mqtt
import threading
import time
import psutil
import signal
from hendi_logger import update_run_log
import sys

node_code='JJ-LF6Z'
MQTT_HOST = 'mqtt.nocola.co.id'
MQTT_PORT = 1883
MQTT_OUT_TOPIC = 'flux/general_json/'+node_code
MQTT_IN_TOPIC = 'flux/command/'+node_code
MQTT_FEEDBACK_TOPIC = 'flux/feedback/'+node_code
MQTT_UPDATE_FIRMWARE_TOPIC = 'flux/firmware/update/'+node_code
MQTT_UPDATE_FIRMWARE_FEEDBACK_TOPIC = 'flux/firmware/feedback/'+node_code
PAYLOAD_SIZE = 1024
mqtt_username = 'mqtt_nocola'
mqtt_password = "cinta123"
first_part = "{\"nodeCode\": \"JJ-LF6Z\", \"time\":"
second_part =  ",\"0\":1}"
third_part = "{\"status\":1}"

def get_system_info():
        cpu_load = psutil.cpu_percent(interval=1)
        cpu_temp = psutil.sensors_temperatures().get("coretemp")[0].current
        memory_usage = psutil.virtual_memory().percent
        storage_usage = psutil.disk_usage("/").percent
        return cpu_load, cpu_temp, memory_usage, storage_usage

def sendData():
        _a,_b,_c,_d = get_system_info()
        _data = "{\"nodeCode\": \"2Q-OQIW\",\"time\":"+ str(int(time.time()) * 1000) 

def onDataReceive(client, userdata, msg):
	global lastIndexProcess
	if (msg.topic == MQTT_IN_TOPIC):
		client.publish(MQTT_OUT_TOPIC, (first_part+ str(int(time.time()) * 1000) + second_part))
		client.publish(MQTT_FEEDBACK_TOPIC, (third_part))

def pingData():
        client.publish(MQTT_OUT_TOPIC, (first_part+str(int(time.time()) *1000) + second_part))

def onConnect(client, userdata, flags, rc):
	global lastIndexProcess
	print('broker connected')
	client.subscribe(MQTT_IN_TOPIC)
	client.publish(MQTT_OUT_TOPIC, (first_part+ str(int(time.time()) * 1000) + second_part))


print('preparing mqtt in a while')
client = mqtt.Client()
client.on_connect = onConnect
client.on_message = onDataReceive
client.username_pw_set(mqtt_username, mqtt_password)

client.connect(MQTT_HOST, MQTT_PORT, 60)

def mqttProcess():
	print('mqtt process is started')
	client.loop_forever()


mqttBackgroundThread = threading.Thread(target=mqttProcess)
mqttBackgroundThread.start()

def update_exc_log_mp(exc_code):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open("run_log.txt", "r") as existing_log:
        existing_entries = existing_log.read()
    with open("run_log.txt", "w") as log:
        new_entry = f"{timestamp} -  MQTT Ping is closed with exception code {exc_code}\n"
        log.write(new_entry + existing_entries)

def signal_handler(sig, frame):
    update_exc_log_mp(sig)
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # Handle termination signals

def main():
         while True:
                 pingData()
                 time.sleep(5)


if __name__ == "__main__":
    try:
        update_run_log("MQTT Ping")
        main()
    except Exception as e:
        print("Program terminated.")
        update_exc_log_vr(e)
