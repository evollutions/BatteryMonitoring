import os
import json
from datetime import datetime

class JsonFileHandler:
    def _convert(self, obj):
        if isinstance(obj, datetime):
            # Convert datetime objects to ISO string
            return obj.isoformat()     
        return json.JSONEncoder.default(self, obj)

    # Reads file from disk
    def read_file(self, file_name, folder_name = None):
        if folder_name is None:
            # Set path without folder when not specified
            full_path = f"{file_name}.json"
        else:
            # Set path with folder
            full_path = f"{folder_name}/{file_name}.json"
               
        if not os.path.exists(full_path):
            raise Exception(f"File '{full_path}' does not exist")
        
        try:
            file = open(full_path, "r")    
            file_content = json.loads(file.read())
        except json.JSONDecodeError as exception:
            print(f"Exception while reading file '{full_path}' occurred:")
            raise exception

        return file_content

    # Writes file to disk
    def write_file(self, content, file_name, folder_name = None):
        if folder_name is None:
            # Set path without folder when not specified
            full_path = f"{file_name}.json"
        else:
            if not os.path.exists(folder_name):
                # Create folder if it does not already exist
                os.makedirs(folder_name)
            
            # Set path with folder
            full_path = f"{folder_name}/{file_name}.json"
        
        # Create and write json file
        with open(full_path, 'w') as out:
            json.dump(content, out, default = self._convert)