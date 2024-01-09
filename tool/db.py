import mysql.connector
from mysql.connector.cursor import MySQLCursorDict
import os

import psycopg2
import pandas as pd
import urllib.parse as urlparse
import time

from funcion import get_table_data
from funcion import get_a_link
from dotenv import load_dotenv


load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))



# 根目錄的網址
url1 = os.getenv("CCU_COURSE_URL")
usingDB = os.getenv("USING_DATABASE")

try:
    conn = None
    if(usingDB == "mysql"):
        conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            port=os.getenv("MYSQL_PORT"),
            user=os.getenv("MYSQL_USER"),
            passwd=os.getenv("MYSQL_PASSWORD"),
            db=os.getenv("MYSQL_DATABASE"),
        )
    elif(usingDB == "postgre"):
        conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')
    cur = conn.cursor()
    if(usingDB == "mysql"):
        cur.execute("use ccu;")
except Exception as ex:
    print("connect error",end=" ")
    print(ex)

totally_correct = 0
totally_error = 0
error_message = []

links = get_a_link(url1)

cur.execute("update course112_2 set deprecated = true where id > 0;")
conn.commit()

# 在所有的子網址上爬取資料
for j in links:
    url = url1 + str(j)
    data = get_table_data(url)
    departement = "'" + data['department'] + "'";
    data = data['data']
    correct_num = int(0)
    error_num = int(0)
    for row in data:
        grade = "'" + row[0] + "'";
        a = "'" + row[1] + "'";
        b = "'" + row[3] + "'";
        c = "'" + row[4] + "'";
        d = "'" + row[8] + "'";
        e = "'" + row[9] + "'";
        credit = "'" + row[6] + "'";
        if j == "I001.html":
            grade = "'" + row[1] + "'";
            a = "'" + row[2] + "'";
            b = "'" + row[4] + "'";
            c = "'" + row[5] + "'";
            d = "'" + row[9] + "'";
            e = "'" + row[10] + "'";
            credit = "'" + row[7] + "'";
        try:
            '''
            create table `course112_2`(
                `id` INT not null,
                `department` nvarchar(100) not NULL default "未知",
                `grade` nvarchar(100) not NULL default "未知",
                `class_name` nvarchar(100) not null,
                `teacher` nvarchar(70) not null,
                `class_time` nvarchar(40) not null,
                `class_room` nvarchar(50) not null,
                `credit` int not null,
                `selection_count` INT default 0,
                `deprecated`boolean default false,
                primary key(id, department, grade,class_name,teacher,class_time,class_room, credit)
            );
            '''
            #若有id,class_name,class_time,class_room相同的資料，則不新增
            cur.execute(f"select * from {os.getenv('MYSQL_COURSE_TABLE')} where id = {a} and class_name = {b} and class_time = {d} and class_room = {e} and credit = {credit} and department = {departement} and grade = {grade};")
            dd = cur.fetchone()
            if dd != None:
                command = f"UPDATE {os.getenv('MYSQL_COURSE_TABLE')} SET deprecated = false where id = {a} and class_name = {b} and class_time = {d} and class_room = {e} and credit = {credit} and department = {departement} and grade = {grade};"
                cur.execute(command)
                conn.commit()
                continue
            command = f"INSERT INTO {os.getenv('MYSQL_COURSE_TABLE')} (department, grade, id, class_name, teacher, class_time, class_room, credit) VALUES ({departement}, {grade}, {a}, {b}, {c}, {d}, {e}, {credit});"
            cur.execute(command)
            conn.commit()
            # print新增成功的資料
            print(command)
            correct_num += 1
        except Exception as ex:
            print("except:",end=" ")
            print(ex)
            error_num += 1
    print(f"link:{j}",end=" ")
    print(f"correct_num:{correct_num} error_num:{error_num}",end=" ")
    totally_correct += correct_num
    totally_error += error_num
    if(error_num > 0):
        print(f"   error link {url}")
        error_message.append([url,error_num])
    else:
        print("")
cur.close()

print(f"totally_correct:{totally_correct} totally_error:{totally_error}")
for num,i in enumerate(error_message):
    print(f"{num + 1}: error_link:{i[0]} error_num:{i[1]}")
