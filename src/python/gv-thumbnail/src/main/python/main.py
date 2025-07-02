import io
import os
import shutil
import tempfile
import time
import urllib.request

#import requests
from PIL import Image

# Global variables.
WIDTH = 100
HEIGHT = 100

# Util methods.
def current_milli_time():
    return round(time.time() * 1000)


# Workload.
def thumbnail(img_url, tmp_dir):
    with urllib.request.urlopen(img_url) as response:
        with tempfile.NamedTemporaryFile(dir=tmp_dir, delete=False) as tmp_file:
            shutil.copyfileobj(response, tmp_file)

        img_filename = "{dir}/img-{timestamp}.png".format(dir=tmp_dir, timestamp=current_milli_time())
        with open(tmp_file.name, 'rb') as encoded_img:
            data = encoded_img.read()
            img = Image.open(io.BytesIO(data))
            img = img.resize((WIDTH, HEIGHT))
            img.save(img_filename, 'png')

#        with open(img_filename, 'rb') as img:
#            requests.post(img_url, headers={'Content-Type': 'image/jpeg'}, data=img)

#        os.remove(img_filename)
        return img_filename


def main(args):
    try:
        url, tmp_dir = args.split(";")
        return {"result": thumbnail(url, tmp_dir)}
    except Exception as e:
        return {"result": str(e)}
