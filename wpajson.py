"""this file provides read and write capability for wpa_supplicant.conf with json as interface"""

from collections import OrderedDict
from systemmgt.wpasupplicantconf.wpasupplicantconf import WpaSupplicantConf
import json

DEFAULT_FILE = './test_wpa_supplicant.conf'
DEFAULT_NW_NAME = 'duid_hotspot'

class WPAJson:
    def __init__(self, wpa_file=DEFAULT_FILE):
        self.wpa_file=wpa_file
        self.curr_json_dict = {}
    
    # transforrms a dict like 
    # OrderedDict([('uido', OrderedDict([('psk', '"netdeemak19"'), ('key_mgmt', 'WPA-PSK')]))])
    # OrderedDict([('ctrl_interface', 'DIR=/var/run/wpa_supplicant GROUP=netdev'), ('update_config', '1'), ('country', 'IN')])
    # to json of the form required by aperture
    def read(self):
        if not self.curr_json_dict:
            with open(self.wpa_file, 'r') as wpafile:
                lines = wpafile.readlines()
                wpc = WpaSupplicantConf(lines)
                self.curr_json_dict['fields'] = wpc.fields()
                networks_list = []
                for key, value in wpc.networks().items():
                    json_nw = {}
                    json_nw['category'] = "Hub"
                    json_nw["ssid"] = key
                    for nkey, nvalue in value.items():
                        json_nw[nkey] = nvalue
                    json_nw['default'] = (key == DEFAULT_NW_NAME)
                    networks_list.append(json_nw)
                self.curr_json_dict['networks'] = networks_list
                # print(self.curr_json_dict)
        return self.curr_json_dict

    # take json from aperture and write the file
    def write(self, config_json: dict):
        self.curr_json_dict = config_json
        with open(self.wpa_file, 'w+') as wpafile:
            wpc = WpaSupplicantConf(wpafile.readlines())
            wpc.set_fields(self.curr_json_dict["fields"])
            # network dict needs mesaging
            networks = self.curr_json_dict['networks']
            wpa_nws = OrderedDict()
            for nw in networks:
                wpanw = OrderedDict()
                wpanw['psk'] = nw['psk']
                wpanw['key_mgmt'] = nw['key_mgmt']
                # top level dict
                wpa_nws[nw['ssid']] = wpanw
            wpc.set_networks(wpa_nws)
            wpafile.seek(0)
            wpc.write(wpafile)
                
    
if __name__ == '__main__':
    config = WPAJson()
    config_json = config.read()
    print(config_json)
    config.write(config_json)
