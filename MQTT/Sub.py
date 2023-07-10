import paho.mqtt.client as mqtt

host = "broker.mqttdashboard.com"
port = 8000

def on_connect(self, client, userdata, rc):
    print("MQTT Connected.")
    self.subscribe("MQTT Connect.")
    self.subscribe("TEST/MQTT")

def on_message(client, userdata,msg):
    print(msg.playload.decode("utf-8", "strict"))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(host)
client.loop_forever()

