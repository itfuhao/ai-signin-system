# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2

app = Flask(__name__)
CORS(app)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if data.get('username') == 'admin' and data.get('password') == '123456':
        return jsonify({"code":200, "msg":"Login Success"})
    return jsonify({"code":401, "msg":"Username or Password Error"})

@app.route('/signin', methods=['POST'])
def signin():
    # 直接返回签到成功，跳过摄像头检测
    return jsonify({"code":200, "msg":"Sign-in Success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)