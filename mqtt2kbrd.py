import os
import json
from paho.mqtt import client as mqtt_client


broker = 'homeassistant.local'
port = 1883
topics = [
    ('zigbee2mqtt/Button1/action', 0),
    ('zigbee2mqtt/Button2/action', 0),
    ('zigbee2mqtt/Button3/action', 0),
]
client_id = 'sigame-buttons'
username = 'mosquitto'
password = 'public'

def notify(message, title=None, subtitle=None, soundname=None):
	"""
		Display an OSX notification with message title an subtitle
		sounds are located in /System/Library/Sounds or ~/Library/Sounds
	"""
	titlePart = ''
	if(not title is None):
		titlePart = f'with title "{title}"'
	subtitlePart = ''
	if(not subtitle is None):
		subtitlePart = f'subtitle "{subtitle}"'
	soundnamePart = ''
	if(not soundname is None):
		soundnamePart = f'sound name "{soundname}"'

	appleScriptNotification = f'display notification "{message}" {titlePart} {subtitlePart} {soundnamePart}'
	os.system(f"osascript -e '{appleScriptNotification}'")

def press(key):
    tellAapplication = f'tell application "System Events" to keystroke "{key}"'
    os.system(f"osascript -e '{tellAapplication}'")

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print('Connected to MQTT Broker!')
        else:
            print(f'Failed to connect, return code {rc}\n')

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode()
        print(f'Received `{payload}` from `{topic}` topic')

        if topic == 'zigbee2mqtt/Button1/action':
            press('a')
        elif topic == 'zigbee2mqtt/Button2/action':
            press('b')
        elif topic == 'zigbee2mqtt/Button3/action':
            press('c')

    client.subscribe(topics)
    client.on_message = on_message

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
