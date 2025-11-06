try:
    import requests
except:
    print("install requests package (pip install requests)")
import os
import sys
import json
import datetime
import random
import mimetypes
if len(sys.argv) < 2:
    print("Usage: python script.py <url>")
    sys.exit(1)
url = sys.argv[1]
script_name = os.path.basename(sys.argv[0])
file_path = os.path.join(os.path.dirname(__file__), "errorlog.json")
def isUniqueErrorId(error_id):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return True
    with open(file_path, "r") as f:
        data = json.load(f)
    existing_ids = {entry["error id"] for entry in data.values()}
    return error_id not in existing_ids
def writeJson(error):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    while True:
        characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()-_+=;:|/<>,.`~'
        error_id = "errid<" + ''.join(random.choice(characters) for _ in range(30)) + ">"
        if isUniqueErrorId(error_id):
            break
        else:
            pass
    new_data = {
            "error": {
                "error id": error_id,
                "time": current_time,
                "error": str(error),
                "url": url,
                "script name": script_name
            }
        }
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, "r") as f:
            data = json.load(f)
    else:
        data = {}
    next_id = len(data) + 1
    data[f"error{next_id}"] = new_data["error"]
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
    print(f"error log created successfully: {error_id}")
try:
    response = requests.get(url, stream=True)
    print(f"\nrequesting {url}...")
    response.raise_for_status()
    content_type = response.headers.get('Content-Type', 'application/octet-stream')
    print("\nguessing file type...")
    extension = mimetypes.guess_extension(content_type)
    print(f"\nfile type guessed: {extension}")
    filename = f'downloaded_file{extension}'
    if 'Content-Disposition' in response.headers:
        content_disposition = response.headers['Content-Disposition']
        if 'filename=' in content_disposition:
            filename = content_disposition.split('filename=')[1].strip('"')
    is_binary = not content_type.startswith('text/')
    mode = 'wb' if is_binary else 'w'
    print("\ndetermining write type...")
    with open(filename, mode) as f:
        if is_binary:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        else:
            f.write(response.text)
    print(f"download successful: {filename}")
except requests.exceptions.Timeout as e:
    print(f"request timed out: {e}")
    writeJson(e)
except requests.exceptions.RequestException as e:
    print(f"request error: {e}")
    writeJson(e)
except Exception as e:
    print(f"unkown error: {e}")
    writeJson(e)
