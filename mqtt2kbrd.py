import os
import keyboard
import json
from paho.mqtt import client as mqtt_client


broker = '192.168.1.14'
port = 1883
topics = [
    ('zigbee2mqtt/SwitchD1', 0),
    ('zigbee2mqtt/SwitchD2', 0),
]
client_id = 'sigame-buttons'
# username = 'emqx'
# password = 'public'

def notify(message,title=None,subtitle=None,soundname=None):
	"""
		Display an OSX notification with message title an subtitle
		sounds are located in /System/Library/Sounds or ~/Library/Sounds
	"""
	titlePart = ''
	if(not title is None):
		titlePart = 'with title "{0}"'.format(title)
	subtitlePart = ''
	if(not subtitle is None):
		subtitlePart = 'subtitle "{0}"'.format(subtitle)
	soundnamePart = ''
	if(not soundname is None):
		soundnamePart = 'sound name "{0}"'.format(soundname)

	appleScriptNotification = 'display notification "{0}" {1} {2} {3}'.format(message,titlePart,subtitlePart,soundnamePart)
	os.system("osascript -e '{0}'".format(appleScriptNotification))


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print('Connected to MQTT Broker!')
        else:
            print(f'Failed to connect, return code {rc}\n')

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        topic = msg.topic
        payload = json.loads(msg.payload.decode())
        print(f'Received `{payload}` from `{topic}` topic')
        if payload['action'] == 'single_left':
            keyboard.send('k')
            notify('Left player', title='mqtt2kbrd', soundname='Basso')
        elif payload['action'] == 'single_right':
            keyboard.send('k')
            notify('Right player', title='mqtt2kbrd', soundname='Blow')

    client.subscribe(topics)
    client.on_message = on_message

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
