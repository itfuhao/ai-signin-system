from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime
import face_recognition
import numpy as np
import base64
import cv2
from io import BytesIO
from PIL import Image

app = Flask(__name__)
CORS(app)

# 模拟用户数据库
USER_DATA = {
    "admin": "123456"
}

# 提前录入的管理员人脸特征（需替换为你自己的人脸编码，运行一次录入代码生成）
ADMIN_FACE_ENCODING = None  # 后续通过录入接口生成
# 存储人脸特征的文件路径
FACE_FEATURE_FILE = "admin_face_encoding.npy"

# 登录接口（原逻辑保留）
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"code": 400, "msg": "缺少账号或密码"}), 400
        
        if USER_DATA.get(username) == password:
            return jsonify({
                "code": 200,
                "msg": "登录成功",
                "data": {
                    "username": username,
                    "login_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }), 200
        else:
            return jsonify({"code": 401, "msg": "账号或密码错误"}), 401
    except Exception as e:
        print(f"登录接口异常：{str(e)}")
        return jsonify({"code": 500, "msg": "服务器内部错误"}), 500

# 人脸录入接口（首次使用需调用，录入管理员人脸）
@app.route('/register_face', methods=['POST'])
def register_face():
    try:
        data = request.get_json()
        face_base64 = data.get('face_image')  # 前端传的Base64人脸图像

        if not face_base64:
            return jsonify({"code": 400, "msg": "缺少人脸图像"}), 400

        # 解码Base64图像
        img_data = base64.b64decode(face_base64.split(',')[1])
        img = Image.open(BytesIO(img_data)).convert('RGB')
        img_np = np.array(img)

        # 提取人脸特征
        face_encodings = face_recognition.face_encodings(img_np)
        if len(face_encodings) == 0:
            return jsonify({"code": 400, "msg": "未检测到人脸，请重新采集"}), 400

        # 保存人脸特征到文件
        global ADMIN_FACE_ENCODING
        ADMIN_FACE_ENCODING = face_encodings[0]
        np.save(FACE_FEATURE_FILE, ADMIN_FACE_ENCODING)

        return jsonify({"code": 200, "msg": "人脸录入成功"}), 200
    except Exception as e:
        print(f"人脸录入异常：{str(e)}")
        return jsonify({"code": 500, "msg": "服务器内部错误"}), 500

# 人脸识别签到接口
@app.route('/face_signin', methods=['POST'])
def face_signin():
    try:
        # 加载已录入的人脸特征
        global ADMIN_FACE_ENCODING
        if ADMIN_FACE_ENCODING is None:
            try:
                ADMIN_FACE_ENCODING = np.load(FACE_FEATURE_FILE)
            except:
                return jsonify({"code": 400, "msg": "未录入管理员人脸，请先录入"}), 400

        # 获取前端传的人脸图像
        data = request.get_json()
        face_base64 = data.get('face_image')
        if not face_base64:
            return jsonify({"code": 400, "msg": "缺少人脸图像"}), 400

        # 解码Base64图像
        img_data = base64.b64decode(face_base64.split(',')[1])
        img = Image.open(BytesIO(img_data)).convert('RGB')
        img_np = np.array(img)

        # 提取实时人脸特征
        face_encodings = face_recognition.face_encodings(img_np)
        if len(face_encodings) == 0:
            return jsonify({"code": 400, "msg": "未检测到人脸，请重新采集"}), 400

        # 人脸比对
        match = face_recognition.compare_faces([ADMIN_FACE_ENCODING], face_encodings[0])[0]
        if match:
            signin_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return jsonify({
                "code": 200,
                "msg": "人脸识别成功，签到完成！",
                "data": {"signin_time": signin_time}
            }), 200
        else:
            return jsonify({"code": 401, "msg": "人脸识别失败，非管理员人脸"}), 401
    except Exception as e:
        print(f"人脸识别异常：{str(e)}")
        return jsonify({"code": 500, "msg": "服务器内部错误"}), 500

# 普通签到接口（保留原接口）
@app.route('/signin', methods=['POST'])
def signin():
    try:
        signin_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return jsonify({
            "code": 200,
            "msg": "Sign-in Success",
            "data": {"signin_time": signin_time}
        }), 200
    except Exception as e:
        print(f"签到接口异常：{str(e)}")
        return jsonify({"code": 500, "msg": "服务器内部错误"}), 500

# 测试接口
@app.route('/test', methods=['GET'])
def test():
    return jsonify({"code": 200, "msg": "后端服务正常运行"}), 200

if __name__ == '__main__':
    app.run(debug=False)
