from bluepy import btle

class BatteryService:
    # Returns battery level of a device, when battery level is not available -1 is returned
    def get_battery_level(self, device_address, device_address_type, battery_service_uuid, battery_characteristic_uuid):
        print(f"{device_address} - trying to fetch battery level")
        
        if device_address_type == "random":
            # Device requires random address type
            device_address_type = btle.ADDR_TYPE_RANDOM
        else:
            # Device requires public address type
            device_address_type = btle.ADDR_TYPE_PUBLIC
                
        if battery_service_uuid is None:
            # Set battery service UUID to default when not specified
            battery_service_uuid = "180f"
            
        if battery_characteristic_uuid is None:
            # Set battery characteristic UUID to default when not specified
            battery_characteristic_uuid = "2a19"
         
        try:
            device = btle.Peripheral(device_address, device_address_type, 0)
            battery_service = device.getServiceByUUID(battery_service_uuid)  
            battery_characteristic = battery_service.getCharacteristics(battery_characteristic_uuid);
            
            # Read raw battery level from characteristic
            raw_battery_level = battery_characteristic[0].read()
            
            # Convert raw battery level to number between 0 to 100
            battery_level = self._convert_raw_battery_level(raw_battery_level)
                
            # Disconnect from device 
            device.disconnect()
            
            return battery_level
        
        except btle.BTLEDisconnectError as exception:
            print(f"{device_address} - battery level could not be fetched, device is not in connectable state ({exception})")
            return -1
        except btle.BTLEGattError as exception:
            print(f"{device_address} - battery level could not be fetched, device does not have battery service ({exception})")
            return -1
        except BrokenPipeError as exception:
            print(f"{device_address} - battery level could not be fetched, connection has been terminated ({exception})")
            return -1
        except Exception as exception:
            print(f"{device_address} - battery level could not be fetched, unexpected error occurred")
            raise exception
    
    def _convert_battery_level(self, raw_value, is_string):
        try:
            value = int(raw_value) if is_string else int.from_bytes(raw_value, "little")
            if value < 0 or value > 100:
                # Invalid battery level value, return -1
                return -1
            return value
        except Exception:
            # Could not convert raw value, return -1
            return -1

    def _convert_raw_battery_level(self, raw_value):
        if raw_value.endswith(b"%"):
            # Raw value is string with percent sign
            value = self._convert_battery_level(raw_value.decode("utf-8")[:-1], True)
        else:
            # Raw value might be string or hex
            value = self._convert_battery_level(raw_value.decode("utf-8"), True)
            
            if value == -1:
                # Raw value is hex
                value = self._convert_battery_level(raw_value, False)
        
        return value