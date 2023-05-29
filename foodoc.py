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
from math import ceil
import random
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
    # 폼에서 데이터를 가져옴

    sql_check = "select exists(select user_id from user where user_id=%s);"
    curs.execute(sql_check, user_id)
    result = curs.fetchone()
    if result[0] == 1:
        return render_template('join1.html',status = 1)
    # 이미 존재하는 아이디라면 오류 페이지 출력
    sql = "insert into user(name,user_id,pw,phone,email) values(%s,%s,%s,%s,%s)"
    curs.execute(sql, (name, user_id, pw,phone,email))

    db.commit();
    # user 테이블에 insert
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
    model_youtube = keras.models.load_model("yotube_class/model_load.h5")
    # 폼에서 데이터를 가져옴

    if(none != 6) :
        if(high == '1') :
            a = 1
        else :
            a = 0
        if (diabetes == '2'):
            b = 1
        else:
            b = 0
        if (obe == '3'):
            c = 1
        else:
            c = 0
        if (fitness == '4'):
            d = 1
        else:
            d = 0
        if (pregnant == '5'):
            e = 1
        else:
            e = 0
        abcde = np.array([[a, b, c, d, e]])
        # 관심사 선택 사항을 array로 변환

        output = model_youtube.predict(abcde)

        for i in range(len(output[0])):
            if (np.max(output) == output[0][i]).all():
                result_youtube = i
    else :
        result_youtube = 0
    # 유튜브 추천 클래스 반환
    model = keras.models.load_model("class_model/model_load.h5")
    xt = np.array([[float(age), float(gender)]])
    output = model.predict(xt)
    for i in range(len(output[0])):
        if (np.max(output) == output[0][i]).all():
            result_class = i
            # 모델을 불러와서 나이 성별에 맞는 클래스를 불어와서 DB에 저장
            # 권장 섭취량 클래스 반환
    curs.execute("SELECT LAST_INSERT_ID() AS reviewIdx");
    idx = curs.fetchone()
    sql = "update user set age=%s,gender=%s,class_num=%s,youtube_class=%s where id=%s;"
    curs.execute(sql, (age,gender,result_class,result_youtube,idx))
    # 앞에 추가 했던 회원 정보에 부가 정보 추가
    db.commit();

    return redirect(url_for('logIn'))


#메인 페이지
@app.route('/main')
def main():
    if 'user_id' in session:
        user_id = escape(session['user_id'])
        sql_name = "select user.name,class_num,youtube_class,(case when score is null then 0 else score end) from user " \
                   "left join (select name,score from score " \
                   "where month(date)= month(now()) and day(date) = day(now())) score on score.name = user.user_id where user_id= %s;"
        curs.execute(sql_name, str(user_id))
        row = curs.fetchone()
        user_name = row[0]
        class_num = row[1]
        youtube_class = row[2]
        user_score = row[3]

        # 메인페이지에 출력할 기본 정보들을 가져옴 (유저 정보 , 권장 섭취량 , 유튜브 추천 클래스)


        sql_kal_day1 = "SELECT sum(energy) as energy FROM eat_food " \
                       "WHERE month(date) = month(now()) AND day(date) = day(now())  AND user_id = %s group by day(date);"

        sql_kal_day2 = "SELECT sum(energy) as energy FROM eat_food " \
                       "WHERE month(date) = month(now()) AND day(date) = day(now())-1  AND user_id = %s group by day(date);"

        sql_kal_day3 = "SELECT sum(energy) as energy FROM eat_food " \
                       "WHERE month(date) = month(now()) AND day(date) = day(now())-2  AND user_id = %s group by day(date);"

        sql_kal_day4 = "SELECT sum(energy) as energy FROM eat_food " \
                       "WHERE month(date) = month(now()) AND day(date) = day(now())-3  AND user_id = %s group by day(date);"

        sql_kal_day5 = "SELECT sum(energy) as energy FROM eat_food " \
                       "WHERE month(date) = month(now()) AND day(date) = day(now())-4  AND user_id = %s group by day(date);"

        sql_kal_day6 = "SELECT sum(energy) as energy FROM eat_food " \
                       "WHERE month(date) = month(now()) AND day(date) = day(now())-5  AND user_id = %s group by day(date);"

        sql_kal_day7 = "SELECT sum(energy) as energy FROM eat_food " \
                       "WHERE month(date) = month(now()) AND day(date) = day(now())-6  AND user_id = %s group by day(date);"

        # 일주일 간의 칼로리 섭취량을 DB에서 가져옴

        curs.execute(sql_kal_day1,str(user_id))
        kal_info_day1 = curs.fetchone()

        curs.execute(sql_kal_day2, str(user_id))
        kal_info_day2 = curs.fetchone()

        curs.execute(sql_kal_day3, str(user_id))
        kal_info_day3 = curs.fetchone()

        curs.execute(sql_kal_day4, str(user_id))
        kal_info_day4 = curs.fetchone()

        curs.execute(sql_kal_day5, str(user_id))
        kal_info_day5 = curs.fetchone()

        curs.execute(sql_kal_day6, str(user_id))
        kal_info_day6 = curs.fetchone()

        curs.execute(sql_kal_day7, str(user_id))
        kal_info_day7 = curs.fetchone()

        # 일주일 간의 열량 섭취량을 가져옴

        kal_list = [0 for i in range(7)]

        if(kal_info_day1 == None):
            kal_list[0] = 0
        else:
            kal_list[0] = kal_info_day1[0];
        if (kal_info_day2 == None):
            kal_list[1] = 0
        else:
            kal_list[1] = kal_info_day2[0];
        if (kal_info_day3 == None):
            kal_list[2] = 0
        else:
            kal_list[2] = kal_info_day3[0];
        if (kal_info_day4 == None):
            kal_list[3] = 0
        else:
            kal_list[3] = kal_info_day4[0];
        if (kal_info_day5 == None):
            kal_list[4] = 0
        else:
            kal_list[4] = kal_info_day5[0];
        if (kal_info_day6 == None):
            kal_list[5] = 0
        else:
            kal_list[5] = kal_info_day6[0];
        if (kal_info_day7 == None):
            kal_list[6] = 0
        else:
            kal_list[6] = kal_info_day7[0];

        # 일주일 간의 칼로리 섭취량을 가져와서 배열에 넣음

        sql_food = "select (case when sum(water) is null then 0 else sum(water) end) AS water,(case when sum(protein) is null then 0 else sum(protein) end) AS protein, " \
                   "(case when sum(water) is null then 0 else sum(water) end) AS water,(case when sum(tansu) is null then 0 else sum(tansu) end) AS tansu," \
                   "(case when sum(vitaminA) is null then 0 else sum(vitaminA) end) AS vitaminA,(case when sum(vitaminB) is null then 0 else sum(vitaminB) end) AS vitaminB," \
                   "(case when sum(vitaminC) is null then 0 else sum(vitaminC) end) AS vitaminC,(case when sum(vitaminD) is null then 0 else sum(vitaminD) end) AS vitaminD " \
                   "from eat_food where user_id = %s and month(date) = month(now()) and day(date) = day(now());"

        curs.execute(sql_food, str(user_id))
        food_info = curs.fetchone()

        sql_class = "select kcal,tansu,protein,water,vitaminA,vitaminB,vitaminC,vitaminD from class " \
                    "where class_num = %s"

        curs.execute(sql_class, class_num)
        class_result = curs.fetchone()

        # 금일 영양소 섭취량을 가져옴

        sql_class = "select video1,video2,video3,video4,video5 from youtube_list " \
                    "where class_id = %s"

        curs.execute(sql_class, youtube_class)
        youtube_list = curs.fetchone()

        # 추천 동영상 링크들을 가져옴

        date_list = [0 for i in range(7)]



        date_list[0] = datetime.today().strftime('%m/%d')
        date_list[1] = (datetime.today() - timedelta(1)).strftime('%m/%d')
        date_list[2] = (datetime.today() - timedelta(2)).strftime('%m/%d')
        date_list[3] = (datetime.today() - timedelta(3)).strftime('%m/%d')
        date_list[4] = (datetime.today() - timedelta(4)).strftime('%m/%d')
        date_list[5] = (datetime.today() - timedelta(5)).strftime('%m/%d')
        date_list[6] = (datetime.today() - timedelta(6)).strftime('%m/%d')

        sql_rank = "select name from score where month(date) = month(now()) and day(date) = day(now()- INTERVAL 1 DAY) order by score desc,name limit 3;"


        curs.execute(sql_rank)
        rank_info = curs.fetchall()

        # 랭킹 순위를 가져옴

        return render_template('index.html', name=user_name,user_score = user_score,rank_info = rank_info ,food_info = food_info,kal_list = kal_list,class_result = class_result,date_list = date_list,youtube_list = youtube_list)
    else:
        return "로그인 해주세요 redirect(url_for('logIn'))"

@app.route('/list')
def analyze():
    user_id = escape(session['user_id'])
    page = request.args.get('page', type=int, default=1)

    # 세션에서 유저 id 추출

    sql_all = "select count(food_name) as date from eat_food where user_id=%s order by date desc;"

    curs.execute(sql_all, str(user_id))

    idx = curs.fetchone()

    idx = int(ceil(idx[0] / 6))

    # 페이지 수를 계산함 (전체 게시글 / 6)

    if page != 1:
        page = (page-1) * 6;
    else :
        page = 0
    sql_food = "select food_name,concat(tansu,\"/\",protein,\"/\",fat),date_format(date,'%%Y-%%m-%%d') as date from eat_food where user_id= %s " \
               "order by date desc limit 6 offset %s;"

    # 페이징 sql

    curs.execute(sql_food, (str(user_id),page))

    food_lists = curs.fetchall()

    sql_name = "select class_num from user where user_id= %s"
    curs.execute(sql_name, str(user_id))
    row = curs.fetchone()
    class_num = row[0]
    # 클래스 정보를 가져옴

    sql_kal_day1 = "SELECT sum(energy) as energy FROM eat_food " \
                   "WHERE month(date) = month(now()) AND day(date) = day(now())  AND user_id = %s group by day(date);"

    sql_kal_day2 = "SELECT sum(energy) as energy FROM eat_food " \
                   "WHERE month(date) = month(now()) AND day(date) = day(now())-1  AND user_id = %s group by day(date);"

    sql_kal_day3 = "SELECT sum(energy) as energy FROM eat_food " \
                   "WHERE month(date) = month(now()) AND day(date) = day(now())-2  AND user_id = %s group by day(date);"

    sql_kal_day4 = "SELECT sum(energy) as energy FROM eat_food " \
                   "WHERE month(date) = month(now()) AND day(date) = day(now())-3  AND user_id = %s group by day(date);"

    sql_kal_day5 = "SELECT sum(energy) as energy FROM eat_food " \
                   "WHERE month(date) = month(now()) AND day(date) = day(now())-4  AND user_id = %s group by day(date);"

    sql_kal_day6 = "SELECT sum(energy) as energy FROM eat_food " \
                   "WHERE month(date) = month(now()) AND day(date) = day(now())-5  AND user_id = %s group by day(date);"

    sql_kal_day7 = "SELECT sum(energy) as energy FROM eat_food " \
                   "WHERE month(date) = month(now()) AND day(date) = day(now())-6  AND user_id = %s group by day(date);"

    curs.execute(sql_kal_day1, str(user_id))
    kal_info_day1 = curs.fetchone()

    curs.execute(sql_kal_day2, str(user_id))
    kal_info_day2 = curs.fetchone()

    curs.execute(sql_kal_day3, str(user_id))
    kal_info_day3 = curs.fetchone()

    curs.execute(sql_kal_day4, str(user_id))
    kal_info_day4 = curs.fetchone()

    curs.execute(sql_kal_day5, str(user_id))
    kal_info_day5 = curs.fetchone()

    curs.execute(sql_kal_day6, str(user_id))
    kal_info_day6 = curs.fetchone()

    curs.execute(sql_kal_day7, str(user_id))
    kal_info_day7 = curs.fetchone()

    kal_list = [0 for i in range(7)]

    if (kal_info_day1 == None):
        kal_list[0] = 0
    else:
        kal_list[0] = kal_info_day1[0];
    if (kal_info_day2 == None):
        kal_list[1] = 0
    else:
        kal_list[1] = kal_info_day2[0];
    if (kal_info_day3 == None):
        kal_list[2] = 0
    else:
        kal_list[2] = kal_info_day3[0];
    if (kal_info_day4 == None):
        kal_list[3] = 0
    else:
        kal_list[3] = kal_info_day4[0];
    if (kal_info_day5 == None):
        kal_list[4] = 0
    else:
        kal_list[4] = kal_info_day5[0];
    if (kal_info_day6 == None):
        kal_list[5] = 0
    else:
        kal_list[5] = kal_info_day6[0];
    if (kal_info_day7 == None):
        kal_list[6] = 0
    else:
        kal_list[6] = kal_info_day7[0];

    # 일주일 간 칼로리 정보들을 배열에 넣음

    date_list = [0 for i in range(7)]

    date_list[0] = datetime.today().strftime('%m/%d')
    date_list[1] = (datetime.today() - timedelta(1)).strftime('%m/%d')
    date_list[2] = (datetime.today() - timedelta(2)).strftime('%m/%d')
    date_list[3] = (datetime.today() - timedelta(3)).strftime('%m/%d')
    date_list[4] = (datetime.today() - timedelta(4)).strftime('%m/%d')
    date_list[5] = (datetime.today() - timedelta(5)).strftime('%m/%d')
    date_list[6] = (datetime.today() - timedelta(6)).strftime('%m/%d')

    # 날짜 배열을 생성함

    sql_food = "select (case when sum(energy) is null then 0 else sum(energy) end) AS energy,(case when sum(protein) is null then 0 else sum(protein) end) AS protein," \
               "(case when sum(water) is null then 0 else sum(water) end) AS water,(case when sum(tansu) is null then 0 else sum(tansu) end) AS tansu from eat_food " \
               "where user_id = %s and month(date) = month(now()) and day(date) = day(now());"

    curs.execute(sql_food, str(user_id))
    food_info = curs.fetchone()

    # 섭취 영양소 총량 정보를 가져옴

    sql_class = "select kcal,tansu,protein,water,vitaminA,vitaminB,vitaminC,vitaminD from class " \
                "where class_num = %s"

    curs.execute(sql_class, class_num)
    class_result = curs.fetchone()

    # 권장 섭취량 정보를 가져옴

    food_info_lack = {}
    # 부족 영양소
    food_info_max = {}
    # 과잉 영양소


    sql = "select round(avg(food.energy)),round(avg(food.protein)),round(avg(food.water)),round(avg(food.tansu)),round(avg(food.vitaminA)),round(avg(food.vitaminB)),round(avg(food.vitaminC)),round(avg(food.vitaminD)) from user inner join (select " \
          "sum(energy) AS energy,sum(protein) AS protein,sum(water) AS water,sum(tansu) AS tansu,sum(vitaminA) AS vitaminA,sum(vitaminB) AS vitaminB,sum(vitaminC) AS vitaminC,sum(vitaminD) AS vitaminD,user_id AS id from eat_food where user_id=%s " \
          "and date <now()-7 group by day(date)) food on food.id = user.user_id where user.user_id=%s"

    curs.execute(sql, (str(user_id), str(user_id)))
    result = curs.fetchone()

    if result[4] < class_result[4] :
        food_info_lack["비타민A"] = "야맹증 , 안구 건조증"

    elif result[4] > class_result[4] :
        food_info_max["비타민A"] = "탈모 , 입술 갈라짐 , 두통"

    if result[5] < class_result[5] :
        food_info_lack["비타민B"] = "쇠약 , 피로 , 숨가쁨 , 현기증 , 신경 손상"

    elif result[5] > class_result[5] :
        food_info_max["비타민B"] = "울렁거림 , 두통 , 메스꺼움"

    if result[6] < class_result[6] :
        food_info_lack["비타민C"] = "피로감 , 쇠약감 , 과민감 , 괴혈병"

    elif result[6] > class_result[6] :
        food_info_max["비타민C"] = "삼투성 설사 , 위장 장애 , 오심 , 구토"

    if result[7] < class_result[7] :
        food_info_lack["비타민D"] = "성장 장애 , 구루병 , 골연화증"

    elif result[7] > class_result[7] :
        food_info_max["비타민D"] = "식욕 상실 , 메스꺼움 , 구토"

    if result[3] < class_result[1] :
        food_info_lack["탄수화물"] = "뇌 기능 저하, 피로감 "

    elif result[3] > class_result[1] :
        food_info_max["탄수화물"] = "지방간 , 고지혈증"

    if result[1] < class_result[2] :
        food_info_lack["단백질"] = "머리카락 얇아짐 , 피부 갈라짐 , 골격 약화"

    elif result[1] > class_result[2] :
        food_info_max["단백질"] = "소화 장애 , 신장 이상"

    if result[2] < class_result[3] :
        food_info_lack["수분"] = "소화 불량 , 가슴 쓰림"

    elif result[2] > class_result[3] :
        food_info_max["수분"] = "신장 기능 약화 , 저나트륨혈증 , 심부적증 약화"

    # 부족 영양소와 과잉 영양소 질병 정보를 삽입

    food_idx = random.randrange(0,len(food_info_lack))
    food_rack =list(food_info_lack.keys())
    lack_food = food_rack[food_idx]
    # 부족 영양소 중에서 아무거나 하나 가져옴

    sql_food = "select food1_name , img1_path , food2_name , img2_path , food3_name , img3_path , food4_name , img4_path from food_load where nutrient = %s"
    # 부족 영양소 보충 식단 sql문

    curs.execute(sql_food, lack_food)
    food_load = curs.fetchone()

    return render_template('analyze.html',result = result,food_lists=food_lists,idx = idx, kal_list = kal_list
                           ,date_list = date_list,class_result = class_result,food_info = food_info,food_info_lack = food_info_lack
                           ,food_info_max = food_info_max,food_idx = food_idx,lack_food = lack_food,food_load = food_load)

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
    print(food_name)
    sql = "select food_name,energy,protein,fat,water,tansu,sugar,vitaminA,vitaminB,vitaminC,vitaminD from food where eng_name = %s"
    # 해당 식품에 맞는 영양소 정보를 DB에서 불러옴
    curs.execute(sql, food_name)
    rows = curs.fetchone()

    food_list = list(rows)
    user_id = escape(session['user_id'])

    now = datetime.now().hour
    hour = int(now)


    if hour >= 5 and hour < 10:
        meal = '아침식사'
        sql = "insert into eat_food(user_id,food_name,energy,protein,fat,water,tansu,sugar,vitaminA,vitaminB,vitaminC,vitaminD,meal) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        curs.execute(sql, (str(user_id), rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6],rows[7],rows[8],rows[9],rows[10], meal))

        db.commit();
    elif hour >= 10 and hour < 11:
        meal = '간식'
        sql = "insert into eat_food(user_id,food_name,energy,protein,fat,water,tansu,sugar,vitaminA,vitaminB,vitaminC,vitaminD,meal) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        curs.execute(sql, (str(user_id), rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6],rows[7],rows[8],rows[9],rows[10], meal))

        db.commit();
    elif hour >= 11 and hour < 14:
        meal = '점심식사'
        sql = "insert into eat_food(user_id,food_name,energy,protein,fat,water,tansu,sugar,vitaminA,vitaminB,vitaminC,vitaminD,meal) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        curs.execute(sql, (str(user_id), rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6],rows[7],rows[8],rows[9],rows[10], meal))

        db.commit();
    elif hour >= 14 and hour < 17:
        meal = '간식'
        sql = "insert into eat_food(user_id,food_name,energy,protein,fat,water,tansu,sugar,vitaminA,vitaminB,vitaminC,vitaminD,meal) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        curs.execute(sql, (str(user_id), rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6],rows[7],rows[8],rows[9],rows[10], meal))

        db.commit();
    elif hour >= 17 and hour < 19:
        meal = '저녁식사'
        sql = "insert into eat_food(user_id,food_name,energy,protein,fat,water,tansu,sugar,vitaminA,vitaminB,vitaminC,vitaminD,meal) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        curs.execute(sql, (str(user_id), rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6],rows[7],rows[8],rows[9],rows[10], meal))

        db.commit();
    else:
        meal = '야식'
        sql = "insert into eat_food(user_id,food_name,energy,protein,fat,water,tansu,sugar,vitaminA,vitaminB,vitaminC,vitaminD,meal) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        curs.execute(sql, (str(user_id), rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6],rows[7],rows[8],rows[9],rows[10], meal))

        db.commit();

    sql_class = "select max(class_num) as class_num,sum(energy) as energy,sum(protein) as protein,sum(water) as water,sum(tansu) as tansu from user " \
                    "inner join eat_food on eat_food.user_id = user.user_id where user.user_id = %s and month(date) = month(now()) and day(date) = day(now());"

    curs.execute(sql_class, str(user_id))
    class_num = curs.fetchone()

    # 시간에 따라 식사 종류를 구분에서 유저 정보에 삽입

    sql_class = "select kcal,tansu,protein,water from class " \
                    "where class_num = %s"

    curs.execute(sql_class, class_num[0])
    class_result = curs.fetchone()

    # 권장 섭취량 정보를 가져옴

    health_score = ((((class_result[0] - class_num[1]) / class_result[0]) * 100) + (((class_result[1] - class_num[4]) / class_result[1]) * 100)
              + (((class_result[2] - class_num[2]) / class_result[2]) * 100) + (((class_result[3] - class_num[3]) /class_result[3]) * 100)) / 4
    print(health_score)
    if health_score >= 100:
        health_score = 100
    if health_score <= 0:
        health_score = 0

    # 건강 점수를 계산

    sql_exist = "select exists(select name from score where name=%s and month(date)= month(now()) and day(date) = day(now())) as exsits;"
    curs.execute(sql_exist, str(user_id))
    exist = curs.fetchone()

    if exist[0] == 0 :
        sql = "insert into score(name,score) values(%s,%s)"
        curs.execute(sql, (str(user_id), health_score))

        db.commit();
    else :
        sql = "update score set score = %s where name= %s"
        curs.execute(sql, (health_score,str(user_id)))

        db.commit();

    # 건강 점수가 없다면 새로 계산 , 없다면 기존 점수 수정

    return redirect(url_for('main'))



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
        # 로그인 정보를 가져오고 패스워드 일치 확인
    else:
        return render_template('logIn.html',status = 0)



@app.route('/modify', methods=['GET'])
def modify():
    user_id = escape(session['user_id'])
    sql = "select name,pw,phone,email from user where user_id = %s"
    # 회원 정보들을 가져옴 (이름, 폰번호 , 이메일 등등 ...)
    curs.execute(sql, str(user_id))
    info = curs.fetchone()
    return render_template('info_modify.html',info = info)

@app.route('/modify_process', methods=['POST'])
def modify_process():
    user_id = escape(session['user_id'])

    pw = request.form.get('pw')
    name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email')
    high = request.form.get('high')
    diabetes = request.form.get('diabetes')
    face = request.form.get('face')
    fitness = request.form.get('fitness')
    pregnant = request.form.get('pregnant')
    none = request.form.get('none')
    model_youtube = keras.models.load_model("yotube_class/model_load.h5")

    # 수정 정보들을 가져옴 (유저가 수정 페이지에서 적은 이름이나 비밀번호 , 관심사 선택사항)

    if (none != 1):
        if (pregnant == None):
            a = 1
        else:
            a = 0
        if (diabetes == None):
            b = 1
        else:
            b = 0
        if (high == None):
            c = 1
        else:
            c = 0
        if (face == None):
            d = 1
        else:
            d = 0
        if (fitness == None):
            e = 1
        else:
            e = 0
        abcde = np.array([[a, b, c, d, e]])

        output = model_youtube.predict(abcde)

        for i in range(len(output[0])):
            if (np.max(output) == output[0][i]).all():
                result_youtube = i
    else:
        result_youtube = 0

    # 유튜브 관심 클래스 분류 (텐서플로우 코드)

    user_id = escape(session['user_id'])

    # 세션에서 유저 id 가져옴

    sql = "update user set name=%s,phone=%s,email=%s,pw=%s,youtube_class=%s where user_id = %s"
    curs.execute(sql, (name,phone,email,pw,result_youtube,str(user_id)))
    db.commit();

    # 수정 사항 유저 정보에 삽입

    return redirect(url_for('main'))
@app.route('/')
def logIn():
    return render_template('Login.html')
