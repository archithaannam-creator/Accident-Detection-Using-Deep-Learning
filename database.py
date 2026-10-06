import sqlite3
import hashlib
import datetime
import MySQLdb
from flask import session
from flask import Flask, request, send_file
import io
import plotly.graph_objs as go
def db_connect():
    _conn = MySQLdb.connect(host="localhost", user="root",
                            passwd="root", db="cpro")
    c = _conn.cursor()

    return c, _conn



# -------------------------------Registration-----------------------------------------------------------------



 
def inc_reg(username,password,email,mobile,address):
    try:
        c, conn = db_connect()
        print(username,password,email,mobile)
        id="0"
        status = "pending"
        j = c.execute("insert into user (id,username,password,email,mobile,address) values ('"+id +
                      "','"+username+"','"+password+"','"+email+"','"+mobile+"','"+address+"')")
        conn.commit()
        conn.close()
        print(j)
        return j
    except Exception as e:
        print(e)
        return(str(e))   



def ins_loginact(username, password):
    try:
        c, conn = db_connect()
        
        j = c.execute("select * from user where username='" +
                      username+"' and password='"+password+"' "  )
        c.fetchall()
        
        conn.close()
        return j
    except Exception as e:
        return(str(e))
    



def upload(image_path,current_location,our_location):
    try:
        c, conn = db_connect()
        print(image_path,current_location,our_location)
        id="0"
        status = "pending"
        j = c.execute("insert into upload (id,image_data,current_location,our_location) values ('"+id +
                      "','"+image_path+"','"+current_location+"','"+our_location+"')")
        conn.commit()
        conn.close()
        print(j)
        return j
    except Exception as e:
        print(e)
        return(str(e))
    

def vcact2():
    c, conn = db_connect()
    c.execute("select * from upload  ")
    result = c.fetchall()
    conn.close()
    print("result")
    return result


if __name__ == "__main__":
    print(db_connect())
