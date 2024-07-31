import json

import pyfimptoha.fimp as fimp
import pyfimptoha.homeassistant as homeassistant


class Client:
    _devices = [] # discovered fimp devices
    _mqtt = None
    _selected_devices = None
    _topic_discover = "pt:j1/mt:rsp/rt:app/rn:homeassistant/ad:flow1"
    _topic_fimp_event = "pt:j1/mt:evt/rt:dev/rn:zw/ad:1/"
    _topic_ha = "homeassistant/"
    _verbose = False

    def __init__(
            self,
            mqtt=None,
            selected_devices=None,
            debug=False
    ):
        self._selected_devices = selected_devices
        self._verbose = debug

        if mqtt:
            self._mqtt = mqtt
            mqtt.on_message = self.on_message

        self.start()

    def start(self):
        mqtt = self._mqtt

        # Request FIMP devices
        topic_discover = "pt:j1/mt:rsp/rt:app/rn:homeassistant/ad:flow1"
        mqtt.subscribe(topic_discover)
        fimp.send_discovery_request(mqtt)

        # Subscribe to Home Assistant status where Home Assistant announces restarts
        self._mqtt.subscribe("homeassistant/status")

    def on_message(self, client, userdata, msg):
        """
        The callback for when a message is received from the server.
        """
        payload = str(msg.payload.decode("utf-8"))

        # Discover FIMP devices, shortcuts, mode and create Home Aassistant components out of them
        if msg.topic == self._topic_discover:
            data = json.loads(payload)
            homeassistant.create_components(
                devices=data["val"]["param"]["device"],
                rooms=data["val"]["param"]["room"],
                shortcuts=data["val"]["param"]["shortcut"],
                mode=data["val"]["param"]["house"]["mode"],
                mqtt=self._mqtt,
                selected_devices=self._selected_devices,
            )
        elif msg.topic == "homeassistant/status" and payload == "online":
            # Home Assistant was restarted - Push everything again
            self.start()
