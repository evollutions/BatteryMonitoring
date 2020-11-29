import time
import pyttsx3
from datetime import datetime, timezone
from jsonFileHandler import JsonFileHandler
from batteryService import BatteryService

# Returns value of mandatory attribute in object
def get_mandatory_attribute(obj, attribute_name):
    if not attribute_name in obj:
        raise Exception(f"Object '{obj}' is missing attribute '{attribute_name}'")
    
    attribute_value = obj[attribute_name]
    if attribute_value is None:
        raise Exception(f"Object '{obj}' has empty attribute '{attribute_name}'")
    
    return attribute_value

# Returns value of optional attribute in object
def get_optional_attribute(obj, attribute_name):
    if attribute_name in obj:
        return obj[attribute_name]
    else:
        return None

# Creates instance of pyttsx3 engine with desired parameters
def initialize_speech_engine():
    engine = pyttsx3.init()
    
    # Get system available voices
    available_voices = engine.getProperty("voices")    
    speech_language_id = None
    
    # Try to find voice with desired language
    for voice in available_voices:
        if voice.id == speech_language:
            # Language found
            speech_language_id = voice.id
            break
        
    if speech_language_id is None:
        print(f"Speech language {speech_language} is not available, using default")
    else:
        engine.setProperty("voice", voice.id)
    
    return engine

# Says device alert via pyttsx3
def say_device_alert(alert_id, device_name):
    # Get current time
    now = datetime.now()
        
    if night_mode and (now.hour <= 8 or now.hour >= 22):
        # Do not alert early in the morning and late night if night mode is turned on
        print(f"Night mode is enabled and current time is {now.strftime('%H:%M')}, voice alert is disabled")
        return
    
    # Get language section
    language = get_mandatory_attribute(localization, speech_language)
    # Get alerts section
    alerts = get_mandatory_attribute(language, "alerts")
    # Get specific alert
    alert = get_mandatory_attribute(alerts, alert_id)
    
    # Replace device name in alert
    device_alert = alert.replace("#device_name#", device_name)

    # Say alert and wait till end
    speech_engine.say(device_alert)
    speech_engine.runAndWait() 

# Create instance to handle JSON files
file_handler = JsonFileHandler()

# Read config file
config = file_handler.read_file("config")

# Get parameters of config
speech_language = get_mandatory_attribute(config, "speechLanguage")
monitoring_mode = get_mandatory_attribute(config, "autoMonitoringMode")
monitoring_frequency = get_mandatory_attribute(config, "monitoringFrequency")
battery_level_alert = get_mandatory_attribute(config, "batteryLevelAlert")
night_mode = get_mandatory_attribute(config, "nightMode")

# Read localization file
localization = file_handler.read_file("localization")

# Initialize speech engine used for alerts
speech_engine = initialize_speech_engine()

# Initialize instance to get battery level
battery_service = BatteryService()

# Object that holds history of battery levels
history = {}

# Main function
def run_monitoring():
    # Read devices file
    devices_file_content = file_handler.read_file("devices3")
    # Get devices from file content
    devices = get_mandatory_attribute(devices_file_content, "devices")
    
    if len(devices) == 0:
        print(f"No devices to monitor, please modify devices.json")
        return
    
    monitoring_start_timestamp = datetime.now(timezone.utc)
    print(f"Monitoring of {len(devices)} device(s) started ({monitoring_start_timestamp})")
    
    for device in devices:
        # Get parameters of device
        address = get_mandatory_attribute(device, "address")
        address_type = get_mandatory_attribute(device, "addressType")
        friendly_name = get_mandatory_attribute(device, "friendlyName")
        battery_service_uuid = get_optional_attribute(device, "batteryServiceUuid")
        battery_characteristic_uuid = get_optional_attribute(device, "batteryCharacteristicUuid")
        
        # Get current battery level
        current_battery_level = battery_service.get_battery_level(address, address_type, battery_service_uuid, battery_characteristic_uuid)
        
        if current_battery_level == -1:
            # Battery level could not be fetched, continue to next device
            continue
        
        current_timestamp = datetime.now(timezone.utc)
        
        last_battery_level = 999
        
        if address in history:
            if len(history[address]) > 0:
                # Get last saved battery level
                last = history[address][-1]
                last_battery_level = last["batteryLevel"]
        else:
            history[address] = []
        
        if current_battery_level > last_battery_level:
            # Device is charging
            if current_battery_level <= battery_level_alert:
                # Battery level is low, but device is being charged, no need to alert user
                print(f"{address} - device has insufficient battery level of {current_battery_level}% (charging)")
            elif current_battery_level >= 95:
                # Battery level is high, but device is being charged, alert user to disconnect device from charger
                print(f"{address} - device has sufficient battery level of {current_battery_level}% (fully charged)")    
                say_device_alert("charged_alert", friendly_name)
            else:
                #  Battery level is normal, but device is being charged, no need to alert user
                print(f"{address} - device has sufficient battery level of {current_battery_level}% (charging)")
        else:
            # Device is not charging    
            if current_battery_level <= battery_level_alert:
                # Battery level is low and device is not being charged, alert user to charge device
                print(f"{address} - device has insufficient battery level of {current_battery_level}% (needs charging)")
                say_device_alert("charge_alert", friendly_name)
            else:
                # Battery level is normal, no need to alert user
                print(f"{address} - device has sufficient battery level of {current_battery_level}%")
                
        # Add battery level to history
        history[address].append({
            "batteryLevel": current_battery_level,
            "timestamp": current_timestamp
        })

    monitoring_end_timestamp = datetime.now(timezone.utc)
    print(f"Monitoring ended ({monitoring_end_timestamp})\n")

# Monitor devices in endless loop
while True:
    run_monitoring()
    
    # Sleep until next monitoring
    time.sleep(monitoring_frequency)