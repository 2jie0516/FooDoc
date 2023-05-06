import json
from flask import Flask, render_template, request, url_for, session, redirect, escape
import os
import torch
import io
from PIL import Image
import pymysql
from tensorflow import keras
from datetime import datetime
import numpy as np
from datetime import date, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from keras import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.layers.convolutional import Conv2D, MaxPooling2D




app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = "lN[k9_aU2VTT#wpfrU'I55\VX"
models = {}

db = pymysql.connect(host='localhost', user='root', db='foodoc', password='2002duck!!', charset='utf8')
curs = db.cursor()

#회원가입 처리
@app.route('/join_process1', methods=['POST'])
def join_process():
    user_id = request.form.get('user_id')
    pw = request.form.get('pw')
    name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email')

    sql_check = "select exists(select user_id from user where user_id=%s);"
    curs.execute(sql_check, user_id)
    result = curs.fetchone()
    if result[0] == 1:
        return render_template('join1.html',status = 1)

    sql = "insert into user(name,user_id,pw) values(%s,%s,%s)"
    curs.execute(sql, (name, user_id, pw))

    db.commit();

    return render_template('join2.html')

@app.route('/join_process2', methods=['POST'])
def join_process_info():
    age = int(request.form.get('age'))
    gender = request.form.get('gender')
    high = request.form.get('high')
    diabetes = request.form.get('diabetes')
    obe = request.form.get('obe')
    fitness = request.form.get('fitness')
    pregnant = request.form.get('pregnant')
    none = request.form.get('none')
    print(high)
    model_youtube = keras.models.load_model("yotube_class/model_load.h5")
    if(none != 6) :
        if(high == 1) :
            a = int(high)
        else :
            a = 0
        if (diabetes == 2):
            b = int(diabetes)
        else:
            b = 0
        if (obe == 3):
            c = int(obe)
        else:
            c = 0
        if (fitness == 4):
            d = int(fitness)
        else:
            d = 0
        if (pregnant == 5):
            e = int(pregnant)
        else:
            e = 0
        abcde = np.array([[a, b, c, d, e]])

        output = model_youtube.predict(abcde)

        for i in range(len(output[0])):
            if (np.max(output) == output[0][i]).all():
                result_youtube = i
    else :
        result_youtube = 0

    model = keras.models.load_model("class_model/model_load.h5")
    xt = np.array([[float(age), float(gender)]])
    output = model.predict(xt)
    for i in range(len(output[0])):
        if (np.max(output) == output[0][i]).all():
            result_class = i
            # 모델을 불러와서 나이 성별에 맞는 클래스를 불어와서 DB에 저장

    curs.execute("SELECT LAST_INSERT_ID() AS reviewIdx");
    idx = curs.fetchone()
    sql = "update user set age=%s,gender=%s,class_num=%s,youtube_class=%s where id=%s;"
    curs.execute(sql, (age,gender,result_class,result_youtube,idx))

    db.commit();

    return redirect(url_for('logIn'))


#메인 페이지
@app.route('/main')
def main():
    if 'user_id' in session:
        user_id = escape(session['user_id'])
        sql_name = "select name,class_num,youtube_class from user where user_id= %s"
        curs.execute(sql_name, str(user_id))
        row = curs.fetchone()
        user_name = row[0]
        class_num = row[1]
        youtube_class = row[2]

        print(user_id)

        sql_kal = "SELECT sum(energy) as energy FROM eat_food WHERE date BETWEEN DATE_ADD(NOW(),INTERVAL -1 WEEK)" \
                  " AND NOW() AND user_id = %s group by day(date)"

        curs.execute(sql_kal,str(user_id))
        kal_info = curs.fetchall()

        idx = 0;

        kal_list = [0 for i in range(7)]

        for i in kal_info:
            kal_list[idx] = i[0]
            idx += 1

        sql_food = "select sum(energy) AS energy,sum(protein) AS protein,sum(water) AS water,sum(tansu) AS tansu,user_id AS id from eat_food " \
                   "where user_id = %s and month(date) = month(now()) and day(date) = day(now());"


        curs.execute(sql_food, str(user_id))
        food_info = curs.fetchone()




        sql_class = "select kcal,tansu,protein,water from class " \
                    "where class_num = %s"

        curs.execute(sql_class, class_num)
        class_result = curs.fetchone()

        sql_class = "select video1,video2,video3,video4,video5 from youtube_list " \
                    "where class_id = %s"

        curs.execute(sql_class, youtube_class)
        youtube_list = curs.fetchone()
        print(youtube_list[0])
        date_list = [0 for i in range(7)]



        date_list[0] = datetime.today().strftime('%m/%d')
        date_list[1] = (datetime.today() - timedelta(1)).strftime('%m/%d')
        date_list[2] = (datetime.today() - timedelta(2)).strftime('%m/%d')
        date_list[3] = (datetime.today() - timedelta(3)).strftime('%m/%d')
        date_list[4] = (datetime.today() - timedelta(4)).strftime('%m/%d')
        date_list[5] = (datetime.today() - timedelta(5)).strftime('%m/%d')
        date_list[6] = (datetime.today() - timedelta(6)).strftime('%m/%d')

        for i in date_list:
            print(i)

        return render_template('index.html', name=user_name ,food_info = food_info,kal_list = kal_list,class_result = class_result,date_list = date_list,youtube_list = youtube_list)
    else:
        return "로그인 해주세요 redirect(url_for('logIn'))"

@app.route('/list')
def analyze():
    return render_template('analyze.html')

@app.route('/pic_upload')
def pic():
    return render_template('pic_upload.html')

@app.route('/test_main')
def test_main():
    if 'user_id' in session:
        user_id = escape(session['user_id'])

        sql_name = "select name,id from user where user_id= %s"
        curs.execute(sql_name, str(user_id))
        row = curs.fetchone()
        user_name = row[0]
        user_id = row[1]

        # sql_class = "select kcal,protein,water,tansu from class " \
        #             "where class_num = %s"

        # curs.execute(sql_class, class_num)


        return render_template('test_index.html', name=user_name,user_id = user_id)

    else:
        return "로그인 해주세요 redirect(url_for('logIn'))"

#사진업로드
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    im_bytes = file.read()
    im = Image.open(io.BytesIO(im_bytes))
    filename = file.filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    img_src = url_for('static', filename='uploads/' + filename)

    model = torch.hub.load('ultralytics/yolov5', 'custom',
                           path='/home/osh/Downloads/FooDoc-main(1)/FooDoc-main/FOOD5_best7.pt', force_reload=True,
                           skip_validation=True)
    #커스텀 모델을 불러옴

    results = model(im, size=640)


    results_json = results.pandas().xyxy[0].to_json(orient='records')
    json_Object = json.loads(results_json)
    # yoloV5 메뉴얼에 있는 코드 , 정확히 뭘 하는지는 모름
    food_name = json_Object[0].get("name")
    #식품 이름 결과값을 저장

    sql = "select food_name,energy,protein,fat,water,tansu,sugar from food where eng_name = %s"
    # 해당 식품에 맞는 영양소 정보를 DB에서 불러옴
    curs.execute(sql, food_name)
    rows = curs.fetchone()

    food_list = list(rows)
    user_id = escape(session['user_id'])

    now = datetime.now().hour
    hour = int(now)

    if hour >= 5 and hour < 10:
        meal = '아침식사'
        sql = "insert into eat_food(user_id,food_name,energy,protein,fat,water,tansu,sugar,meal) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        curs.execute(sql, (str(user_id), rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], meal))

        db.commit();
    elif hour >= 10 and hour < 11:
        meal = '간식'
        sql = "insert into eat_food(user_id,food_name,energy,protein,fat,water,tansu,sugar,meal) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        curs.execute(sql, (str(user_id), rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], meal))

        db.commit();
    elif hour >= 11 and hour < 14:
        meal = '점심식사'
        sql = "insert into eat_food(user_id,food_name,energy,protein,fat,water,tansu,sugar,meal) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        curs.execute(sql, (str(user_id), rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], meal))

        db.commit();
    elif hour >= 14 and hour < 17:
        meal = '간식'
        sql = "insert into eat_food(user_id,food_name,energy,protein,fat,water,tansu,sugar,meal) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        curs.execute(sql, (str(user_id), rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], meal))

        db.commit();
    elif hour >= 17 and hour < 19:
        meal = '저녁식사'
        sql = "insert into eat_food(user_id,food_name,energy,protein,fat,water,tansu,sugar,meal) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        curs.execute(sql, (str(user_id), rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], meal))

        db.commit();
    else:
        meal = '야식'
        sql = "insert into eat_food(user_id,food_name,energy,protein,fat,water,tansu,sugar,meal) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        curs.execute(sql, (str(user_id), rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], meal))

        db.commit();

    return redirect(url_for('main'))
#
# #회원가입,이거 지금 안씀
# @app.route('/class', methods=['POST'])
# def join():
#     name = request.form.get('name')
#     age = float(request.form.get('age'))
#     sex = float(request.form.get('sex'))
#     model = keras.models.load_model("class_model/model_load.h5")
#     xt = np.array([[age, sex]])
#     output = model.predict(xt)
#
#     for i in range(len(output[0])):
#         if (np.max(output) == output[0][i]).all():
#             result = i
#
#     return render_template('test_index.html', name=name, result=result)


@app.route('/join')
def join_main():
    return render_template('join1.html',status = 0)

@app.route('/join_info')
def join_info():
     return render_template('join2.html')

@app.route('/logIn_process', methods=['POST'])
def logIn_process():
    sql = "select user_id,pw from user where user_id = %s"
    curs.execute(sql, request.form.get('user_id'))
    result = curs.fetchone()
    if (request.form.get('pw') == result[1]):
        session['user_id'] = request.form.get('user_id')
        return redirect(url_for('main'))


@app.route('/eat_list', methods=['GET'])
def eat_list():
    user_id = escape(session['user_id'])
    sql = "select meal,food_name,energy,protein,fat,water,tansu,sugar,date,time(date) from eat_food " \
          "where user_id = %s and year(date) = year(CURRENT_TIMESTAMP) and month(date) = month(CURRENT_TIMESTAMP) " \
          "and day(date) = day(CURRENT_TIMESTAMP)"

    curs.execute(sql, str(user_id))
    result = curs.fetchall()
    return render_template('user_food_list.html', food_list=result)

#하루 영양소 계산
@app.route('/cal', methods=['GET'])
def cal():
    user_id = escape(session['user_id'])
    sql = "select sum(energy) as energy,sum(protein) as protein,sum(water) as water,sum(tansu) as tansu,max(class_num) from eat_food " \
          "left join user on user.user_id = eat_food.user_id " \
          "where eat_food.user_id = %s and year(date) = year(CURRENT_TIMESTAMP) and month(date) = month(CURRENT_TIMESTAMP) " \
          "and day(date) = day(CURRENT_TIMESTAMP)"

    curs.execute(sql, str(user_id))
    result = curs.fetchone()
    print(result[0])
    print(result[1])
    print(result[2])
    print(result[3])

    class_num = result[4]

    sql_class = "select kcal,protein,water,tansu from class " \
                "where class_num = %s"
    curs.execute(sql_class,class_num)
    standard = curs.fetchone();#유저 클래스에 맞는 권장 영양소를 불러옴

    return render_template('health_cal.html', health_list=result, standard=standard)

#식단 추천
@app.route('/recommend', methods=['GET'])
def recommend():
    user_id = escape(session['user_id'])
    sql = "select avg(food.energy),avg(food.protein),avg(food.water),avg(food.tansu),max(class_num) from user inner join (select " \
          "sum(energy) AS energy,sum(protein) AS protein,sum(water) AS water,sum(tansu) AS tansu,user_id AS id from eat_food where user_id=%s " \
          "and date <now()-7 group by day(date)) food on food.id = user.user_id where user.user_id=%s"


    curs.execute(sql, (str(user_id), str(user_id)))
    result = curs.fetchone()
    class_num = result[4]

    sql_class = "select kcal,protein,water,tansu from class " \
                "where class_num = %s"

    curs.execute(sql_class, class_num)
    standard = curs.fetchone();
    recommend_list = []
    for i in range(4):
        if(standard[i] - result[i] > 0):
            recommend_list.append(i)


    return render_template('recommend.html',recommend_list = recommend_list)



@app.route('/')
def logIn():
    return render_template('Login.html')
