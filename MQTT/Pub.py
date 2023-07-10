import paho.mqtt.client as paho
#config Completer.use_jedi = False
import time

broker = "localhost"
port = 1883

publisher = paho.Client("MQTT PYTHON PUBLISHER")
publisher.connect(broker,port)

Value = 0
while True:
    publisher.publish("house/Room_Temp",Value)
    time.sleep(5)
    Value = Value + 1