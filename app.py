import os
import MySQLdb
import smtplib
import random
import string
from datetime import datetime
from flask import Flask, session, url_for, redirect, render_template, request, abort, flash, send_file,Response,jsonify
from database import db_connect,vcact2,upload,ins_loginact,inc_reg
import base64
import io
import json
import re 
import tensorflow as tf
from collections import namedtuple
from collections import defaultdict
from io import StringIO
from PIL import Image
import numpy as np
import winsound
from geopy.geocoders import Nominatim

# def db_connect():
#     _conn = MySQLdb.connect(host="localhost", user="root",
#                             passwd="root", db="assigndb")
#     c = _conn.cursor()

#     return c, _conn
global filename
global detectionGraph
global msg

app = Flask(__name__)
app.secret_key = os.urandom(24)


def get_location_name(latitude, longitude):
    geolocator = Nominatim(user_agent="location_lookup")
    location = geolocator.reverse((latitude, longitude), language='en')
    return location.address

@app.route("/")
def FUN_root():
    return render_template("index.html")   

@app.route("/inceregact", methods = ['GET','POST'])
def inceregact():
   if request.method == 'POST':    
      
      status = inc_reg(request.form['username'],request.form['password'],request.form['email'],request.form['mobile'],request.form['address'])
      
      if status == 1:
       return render_template("login.html",m1="sucess")
      else:
       return render_template("reg.html",m1="failed")
      

@app.route("/inslogin", methods=['GET', 'POST'])       
def inslogin():
    if request.method == 'POST':
        status = ins_loginact(request.form['username'], request.form['password'])
        print(status)
        if status == 1:
            session['username'] = request.form['username']
            return render_template("uhome.html", m1="sucess")
        else:
            return render_template("login.html", m1="Login Failed")
        
@app.route("/admin.html")
def admin():
    return render_template("admin.html")

@app.route("/index.html")
def index():
    return render_template("index.html")

@app.route("/login.html")
def login():
    return render_template("login.html")

@app.route("/reg.html")
def reg():
    return render_template("reg.html")

@app.route("/uhome.html")
def uhome():
    return render_template("uhome.html")

@app.route("/vc.html")
def vc():
    data1 = vcact2()
    print(data1)
    return render_template("vc.html",data1 = data1)



import random
import string


from geopy.geocoders import Nominatim

def get_current_location():
    geolocator = Nominatim(user_agent="myGeocoder")
    location = geolocator.geocode("")

def generate_random_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

def rectArea(xmax, ymax, xmin, ymin):
    x = np.abs(xmax-xmin)
    y = np.abs(ymax-ymin)
    return x*y

def extract_street_name(location_name):
    # Use regular expression to find the street name pattern
    match = re.search(r'\b(\d+-\d+,?\s)?([\w\s]+),', location_name)
    if match:
        return match.group(2)
    else:
        return None
    
def area(a, b):  # returns None if rectangles don't intersect
    dx = min(a.xmax, b.xmax) - max(a.xmin, b.xmin)
    dy = min(a.ymax, b.ymax) - max(a.ymin, b.ymin)
    return dx*dy

def calculateCollision(boxes,classes,scores,image_np):
    global msg
    #cv2.putText(image_np, "NORMAL!", (230, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)
    for i, b in enumerate(boxes[0]):
        if classes[0][i] == 3 or classes[0][i] == 6 or classes[0][i] == 8:
            if scores[0][i] > 0.5:
                for j, c in enumerate(boxes[0]):
                    if (i != j) and (classes[0][j] == 3 or classes[0][j] == 6 or classes[0][j] == 8) and scores[0][j]> 0.5:
                        Rectangle = namedtuple('Rectangle', 'xmin ymin xmax ymax')
                        ra = Rectangle(boxes[0][i][3], boxes[0][i][2], boxes[0][i][1], boxes[0][i][3])
                        rb = Rectangle(boxes[0][j][3], boxes[0][j][2], boxes[0][j][1], boxes[0][j][3])
                        ar = rectArea(boxes[0][i][3], boxes[0][i][1],boxes[0][i][2],boxes[0][i][3])
                        col_threshold = 0.6*np.sqrt(ar)
                        area(ra, rb)
                        if (area(ra,rb)<col_threshold) :
                            print('accident')
                            msg = 'ACCIDENT'
                            beep()
                            return True
                        else:
                            return False
                        
@app.route("/showact", methods = ['GET','POST'])
def showact():
    c1 = request.args.get('c')
    d1 = request.args.get('d')
       
    return render_template("show.html",c1 = c1,d1=d1)      
                  
def beep():
    frequency = 2500  # Set Frequency To 2500 Hertz
    duration = 1000  # Set Duration To 1000 ms == 1 second
    winsound.Beep(frequency, duration)

import cv2
@app.route('/detect')
def detect():
    global msg
    msg = ''
    count=0
    global detectionGraph
    detectionGraph = tf.Graph()
    with detectionGraph.as_default():
        od_graphDef = tf.GraphDef()
        with tf.gfile.GFile('model/frozen_inference_graph.pb', 'rb') as file:
            serializedGraph = file.read()
            od_graphDef.ParseFromString(serializedGraph)
            tf.import_graph_def(od_graphDef, name='')
    
    cap = cv2.VideoCapture(0)  # Use the default camera (0)      
    with detectionGraph.as_default():
        with tf.Session(graph=detectionGraph) as sess:
            while True:
                ret, image_np = cap.read()
                image_np_expanded = np.expand_dims(image_np, axis=0)
                image_tensor = detectionGraph.get_tensor_by_name('image_tensor:0')
                boxes = detectionGraph.get_tensor_by_name('detection_boxes:0')
                scores = detectionGraph.get_tensor_by_name('detection_scores:0')
                classes = detectionGraph.get_tensor_by_name('detection_classes:0')
                num_detections = detectionGraph.get_tensor_by_name('num_detections:0')
                (boxes, scores, classes, num_detections) = sess.run([boxes, scores, classes, num_detections], feed_dict={image_tensor: image_np_expanded})
                calculateCollision(boxes, classes, scores, image_np)
                cv2.putText(image_np, msg, (230, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2, cv2.LINE_AA)
                cv2.imshow('Accident Detection', image_np)
                if msg == "ACCIDENT" and count==0:
                    random_string = generate_random_string(4)
                    cv2.imwrite("static/uploads/" +random_string+".jpg", image_np)
                    image_path = "static/uploads/" +random_string+".jpg"
                    import json
                    import json
                    from urllib.request import urlopen
                    url='http://ipinfo.io/json'
                    response=urlopen(url)
                    location=json.load(response)
                    print(location)
                    latitude, longitude = map(float, location['loc'].split(','))

                    print("Latitude:", latitude)
                    print("Longitude:", longitude)                                

                             
                    # Display
                    print(location)
                   
                    location_name = get_location_name(latitude, longitude)
                    street_name = extract_street_name(location_name)
                    if street_name:
                        print("Street Name:", street_name)
                    else:
                        print("Street Name not found.")      
                    print("Location Name:", location_name)
                    result = json.dumps(location)                    
                    upload(image_path,"ameerpet",street_name)
                    print("Accident detected! Image saved.")
                    count =1
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    break       

    return render_template("admin.html")

def is_accident(frame):
    # Placeholder for accident detection logic
    # Implement your own logic for accident detection here
    # This function should return True if an accident is detected in the frame, False otherwise
    return False  # Replace this with your accident detection logic
# # -------------------------------Loginact End-----------------------------------------------------------------


   
if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5000)
    
if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5001)