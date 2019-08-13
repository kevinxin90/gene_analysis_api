import hashlib
import os
import json
from pathlib import Path


def hashInput(input):
    return hashlib.md5(input.encode('utf-8')).hexdigest()


def check_job_status(hash):
    file_path = os.path.abspath(os.path.join(*['files', hash]))
    if Path(file_path).is_file():
        with open(file_path, 'r') as f:
            contents = f.read()
            if contents == "In processing!":
                return ("In processing", None)
            else:
                data = json.loads(contents)
                return ("Completed", data)
    else:
        with open(file_path, "w") as f:
            f.write('In processing!')
        return ("New job started", None)


def write_result_to_file(hash, result):
    file_path = os.path.abspath(os.path.join(*['files', hash]))
    with open(file_path, "w") as f:
        f.write(json.dumps(result))

