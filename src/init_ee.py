import os
import ee

# Copy the token to the container
def ee_Initialize():
    ee_token = os.environ['EARTHENGINE_TOKEN']
    credential = '{"refresh_token":"%s"}' % ee_token
    credential_file_path = os.path.expanduser("~/.config/earthengine/")
    os.makedirs(credential_file_path,exist_ok=True)
    with open(credential_file_path + 'credentials', 'w') as file:
        file.write(credential)
    try:
        ee.Initialize()        
    except Exception as e:
        print(e)
        return False    
    return True