import datetime
import json
import cv2
import os

from flask import Flask, request, render_template, url_for
from shutil import copyfile

from lpr.recognize import recognize

sever = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

scan_dir = './static/images/scan.jpg'


@sever.route("/", methods=["GET", "POST"])
def upload():
    if request.method == "GET":
        return render_template('index.html',
                               img_url=url_for(
                                   'static', filename='images/background.jpg'),
                               plates=[''],
                               plates_num=1,
                               )
    elif request.method == "POST":
        f = request.files.get('upload_image', None)
        if f:  # 如果文件不为空
            cur_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            filename = str(f.filename)
            name = filename[:filename.rfind('.')]
            suffix = filename[filename.rfind('.'):]

            new_file_name = name + cur_time + suffix
            # print('new_file_name', new_file_name)

            file_dir = os.path.join('./cars', new_file_name)
            f.save(file_dir)
            copyfile(file_dir, scan_dir)

            result = scan_image(scan_dir)
            return render_template('index.html',
                                   img_url=url_for(
                                       'static', filename='images/scan.jpg'),
                                   plates=result,
                                   plates_num=len(result),
                                   )
        else:   # 如果文件为空
            res = {"msg": "没有上传文件"}
            return json.dumps(res, ensure_ascii=False)  # 防止出现乱码


def scan_image(file_path):
    img = cv2.imread(file_path)
    # 识别结果
    char_result, confidence_result = recognize(img)
    return char_result


sever.run(port=8888)
