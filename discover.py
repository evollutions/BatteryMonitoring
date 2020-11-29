from datetime import datetime, timezone
from bluepy import btle
from bluepy.btle import Scanner, DefaultDelegate
from jsonFileHandler import JsonFileHandler

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    # Prints information about new device or data
    def handleDiscovery(self, device, is_new_device, is_new_data):
        if is_new_device:
            print(f"{device.addr} - device discovered")
        elif is_new_data:
            print(f"{device.addr} - received new data")

class DeviceService():
    # Returns device information in dictionary form
    def get_info(self, device):
        print(f"{device.addr} - getting information")
        
        # Get basic attributes of device
        device_dict = {
            "address": device.addr,
            "addressType": device.addrType,
            "rssi": device.rssi,
            "connectable": device.connectable,
            "advertising_data": [],
            "services": self.get_services(device)
        }
    
        # Get advertising data of device
        advertising_data = device.getScanData() 
        if advertising_data is not None:
            for (adtype, description, value) in advertising_data:
                device_dict["advertising_data"].append({
                    "adtype": adtype,
                    "description": description,
                    "value": value,
                })
            
        return device_dict
    
    # Returns array of services from device
    # Empty array is returned if services could not be fetched
    def get_services(self, device):
        print(f"{device.addr} - attempting to fetch services")
        
        if not device.connectable:
            # Device is not currently in connectable state
            print(f"{device.addr} - services could not be fetched (not connectable)")
            return []
        
        try:
            # Connect to the device and fetch services
            peripheral = btle.Peripheral(device)
            services = peripheral.getServices()
            
            if services is None:
                # Device has no services
                print(f"{device.addr} - has no services")
                return []
            
            services_dict = []
            for service in services:
                # Get characteristics of service
                services_dict.append({
                    "uuid": service.uuid.getCommonName(),
                    "characteristics": self.get_characteristics(service)
                })
                
            print(f"{device.addr} - fetched {len(services_dict)} services")              
            return services_dict
        except btle.BTLEDisconnectError as exception:
            print(f"{device.addr} - services could not be fetched ({exception})")
            return []
    
    # Returns array of characteristics from service
    # Empty array is returned if characteristics could not be fetched
    def get_characteristics(self, service):
        characteristics = service.getCharacteristics()      
        if characteristics is None:
            # Service has no characteristics
            return []
        
        characteristics_dict = []      
        for characteristic in characteristics:
            # Get attributes of characteristic
            characteristics_dict.append({
                "uuid": characteristic.uuid.getCommonName(),
                "properties": characteristic.properties,
                "propertiesString": characteristic.propertiesToString(),
                "supportsRead": characteristic.supportsRead()
            })
            
        return characteristics_dict

# Create instance of BLE scanner with delegate
scanner = Scanner().withDelegate(ScanDelegate())

# Create instance to get info about discovered device
device_service = DeviceService()

# Create instance to handle JSON files
file_handler = JsonFileHandler()

# Save current timestamp as discovery start
discovery_start = datetime.now(timezone.utc)
print(f"Discovery started ({discovery_start})")

# Initialize result dictionary
discovery_result = {
    "devices": []
}

try:
    # Start discovery and save discovered devices
    devices = scanner.scan(10.0)
except Exception as exception:
    print("Discovery failed")
    raise exception

for device in devices:
    # Get information about discovered device
    device_info = device_service.get_info(device)

    # Append discovered device
    discovery_result["devices"].append(device_info)

# Save current timestamp of end
discovery_end = datetime.now(timezone.utc)
print(f"Discovery ended ({discovery_end})")

discovery_result["startTimestamp"] = discovery_start
discovery_result["endTimestamp"] = discovery_end

# Create file name of discovery
discovery_result_file_name = f"discovery-{discovery_start.strftime('%d-%m-%Y-%H-%M-%S')}"

# Write file
file_handler.write_file(discovery_result, discovery_result_file_name, "discoveries")
print(f"Discovery result saved in file '{discovery_result_file_name}'")