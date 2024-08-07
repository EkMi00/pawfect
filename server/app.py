from flask_cors import CORS, cross_origin
import json
import sqlalchemy
from flask_bcrypt import Bcrypt
from flask import Flask, request, Response, flash, jsonify, session, render_template, send_from_directory, redirect, url_for
from typing import Dict
import os

app = Flask(__name__, static_url_path='')  # Setup the flask app by creating an instance of Flask
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
# Eenabling the flask app to be able to communicate with any request source
CORS(app)


YOUR_POSTGRES_PASSWORD = "postgres"
connection_string = f"postgresql://postgres:{YOUR_POSTGRES_PASSWORD}@localhost/petcare"
engine = sqlalchemy.create_engine(connection_string)

db = engine.connect()

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/sign-up', methods=['GET', 'POST'])
def signUp():
    try:
        data = request.data.decode()
        user = json.loads(data)
        statement, checkEmail, checkUser = newUser(user)
        emailRes = db.execute(checkEmail).fetchone()
        userRes = db.execute(checkUser).fetchone()
        if emailRes and userRes:
            return Response("Account with this email and username already exists.", 403)
        elif userRes:
            return Response("Account with this username already exists.", 403)
        elif emailRes:
            return Response("Account with this email already exists.", 403)
        db.execute(statement)
        db.commit()
        session['username'] = user['username']
        return Response(statement.text, 200)
    except Exception as e:
        db.rollback()
        return Response("Server problem.", 403)

def newUser(user: Dict):
    username = user['username']
    email = user['email']
    hashed_password = bcrypt.generate_password_hash(user['password'])
    password = hashed_password.decode('ascii')
    statement = sqlalchemy.text(f"INSERT INTO users (username, email, password) VALUES ('{username}','{email}','{password}')")
    checkEmail = sqlalchemy.text(f"SELECT * FROM users WHERE email LIKE '{email}'")
    checkUser = sqlalchemy.text(f"SELECT * FROM users WHERE username LIKE '{username}'")
    return statement, checkEmail, checkUser

@app.route('/login', methods=['GET'])
def signIn():
    try:
        email = request.args.get('email', default="", type=str)
        password = request.args.get('password', default="", type=str)
        statement = sqlalchemy.text(f"SELECT * FROM users WHERE email LIKE '{email}'")
        checkUser = db.execute(statement).fetchone()
        if checkUser and bcrypt.check_password_hash(checkUser[2], password):
            session['username'] = checkUser[0]
            session['login'] = True
            userDetails = {'username': checkUser[0], 'email': checkUser[1]} #username and email
            return userDetails
        else:
            return Response("Incorrect username/password", 403)
    except Exception as e:
        db.rollback()
        return Response("Server problem.", 403)

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    print(session)
    return 'Session cleared', 200

@app.route('/pet-sitters', methods=['GET', 'POST'])
def createProfile():
    try:
        data = request.data.decode()
        petSitter = json.loads(data)
        sitterUname = petSitter['username']
        sitterSDate = petSitter['startDate']
        sitterEDate = petSitter['endDate']
        sitterPrice = petSitter['price']
        sitterDog = petSitter['dog']
        sitterCat = petSitter['cat']
        sitterPetBoarding = petSitter['petBoarding']
        sitterDogWalking = petSitter['dogWalking']
        sitterPetGrooming = petSitter['petGrooming']
        sitterPetDaycare = petSitter['petDaycare']
        sitterPetSitting = petSitter['petSitting']
        sitterPetTaxi = petSitter['petTaxi']
        checkExistQuery = sqlalchemy.text(f"SELECT username "
                                          f"FROM petsitters "
                                          f"WHERE username LIKE '{sitterUname}';")
        checkExistRes = db.execute(checkExistQuery).fetchone()
        print(checkExistRes)
        if checkExistRes:
            statement = sqlalchemy.text(f"UPDATE petsitters "
                                        f"SET startDate = '{sitterSDate}', "
                                        f"endDate = '{sitterEDate}', "
                                        f"price = '{sitterPrice}', "
                                        f"dog = '{sitterDog}', "
                                        f"cat = '{sitterCat}', "
                                        f"petBoarding = '{sitterPetBoarding}', "
                                        f"dogWalking = '{sitterDogWalking}', "
                                        f"petGrooming = '{sitterPetGrooming}', "
                                        f"petDaycare = '{sitterPetDaycare}', "
                                        f"petSitting = '{sitterPetSitting}', "
                                        f"petTaxi = '{sitterPetTaxi}' "
                                        f"WHERE username LIKE '{sitterUname}';")
            db.execute(statement)
            db.commit()
            return Response("Form Updated", 200)
        else:
            statement = sqlalchemy.text(f"INSERT INTO petsitters (username, startDate, endDate, price, dog, cat, petBoarding, dogWalking, petGrooming, petDaycare, petSitting, petTaxi) "
                                        f"VALUES ('{sitterUname}','{sitterSDate}','{sitterEDate}','{sitterPrice}','{sitterDog}','{sitterCat}','{sitterPetBoarding}','{sitterDogWalking}','{sitterPetGrooming}','{sitterPetDaycare}','{sitterPetSitting}','{sitterPetTaxi}');"
                                        )
            db.execute(statement)
            db.commit()
            return Response("Form Submitted", 200)
    except Exception as e:
        db.rollback()
        return Response("Server problem.", 403)

@app.route('/deleteSitterProfile', methods=['POST'])
def deleteProfile():
    try:
        username = session['username']
        statement = sqlalchemy.text(f"DELETE FROM petsitters "
                                    f"WHERE username LIKE '{username}';")
        db.execute(statement)
        db.commit()
        return Response("Profile deleted", 200)
    except Exception as e:
        db.rollback()
        return Response("Server problem.", 403)
    
@app.route('/find-services', methods=['GET','POST'])
def findServices():
    try:
        if request.method == "GET":
            statement = sqlalchemy.text(f"SELECT * FROM petsitters;")
            res = db.execute(statement).fetchall()
            db.commit()
            petSitters = []
            data = {}
            for result in res:
                data = {'username':result[0], 
                        'startDate':result[1], 
                        'endDate':result[2], 
                        'price':result[3], 
                        'dog':result[4], 
                        'cat':result[5], 
                        'petBoarding':result[6], 
                        'dogWalking':result[7], 
                        'petGrooming':result[8], 
                        'petDaycare':result[9], 
                        'petSitting':result[10],
                        'petTaxi':result[11]}
                petSitters.append(data)
                data = {}
            existing = []
            statement2 = sqlalchemy.text(f"SELECT * FROM jobs;")
            res2 = db.execute(statement2).fetchall()
            db.commit()
            data = {}
            for result in res2:
                data = {result[1]:result[2]}
                existing.append(data)
                data = {}
            dict = { 0: petSitters, 1:  existing }
            return jsonify(dict), 200
        if request.method == "POST":
            data = request.data.decode()
            hiring = json.loads(data)
            # print(hiring)
            hirerUname = hiring['hirerUsername']
            sitterUname = hiring['sitterUsername']
            statement = sqlalchemy.text(f"INSERT INTO jobs (hirer_username, sitter_username) "
                                        f"VALUES ('{hirerUname}','{sitterUname}');")
            db.execute(statement)
            db.commit()
            return Response("Hire success", 200)
    except Exception as e:
        print(e)
        return Response("Server problem.", 403)
    
@app.route('/hiredJobs', methods=['GET'])
def hiredJobs():
    try:
        if request.method == 'GET':
            username = session['username']
            # print(username)
            statement = sqlalchemy.text(f"SELECT id, sitter_username, email, status FROM jobs "
                                        f"INNER JOIN users "
                                        f"ON sitter_username = username "
                                        f"WHERE hirer_username LIKE '{username}'"
                                        f"ORDER BY status DESC, id  ;")
            res = db.execute(statement).fetchall()
            print("res:")
            print(res)
            jobs = []
            data = {}
            for result in res:
                data = {'id':result[0], 
                        'sitter':result[1], 
                        'sitterEmail':result[2], 
                        'jobStatus':result[3]}
                jobs.append(data)
                data = {}
            print("jsonified jobs")
            print(jsonify(jobs))
            return jsonify(jobs), 200
    except Exception as e:
        return Response("Something went wrong", 403)

@app.route('/jobs/complete/<int:job_id>', methods=['POST'])
def complete_job(job_id):
    try:
        statement = sqlalchemy.text(f"UPDATE jobs SET status = 'Completed' WHERE id = :job_id")
        db.execute(statement, {'job_id': job_id})
        db.commit()
        return jsonify({'message': 'Job completed successfully'}), 200
    except Exception as e:
        return Response("Something went wrong", 403)
    
@app.route('/jobs/cancel/<int:job_id>', methods=['POST'])
def cancel_job(job_id):
    try:
        statement = sqlalchemy.text(f"UPDATE jobs SET status = 'Cancelled' WHERE id = :job_id")
        db.execute(statement, {'job_id': job_id})
        db.commit()
        return jsonify({'message': 'Job cancelled successfully'}), 200
    except Exception as e:
        return Response("Something went wrong", 403)
    
@app.route('/jobs/inProgress/<int:job_id>', methods=['POST'])
def inProgress_job(job_id):
    try:
        statement = sqlalchemy.text(f"UPDATE jobs SET status = 'In Progress' WHERE id = :job_id")
        db.execute(statement, {'job_id': job_id})
        db.commit()
        return jsonify({'message': 'Job now in progress'}), 200
    except Exception as e:
        return Response("Something went wrong", 403)

@app.route('/myJobs', methods=['GET'])
def myJobs():
    try:
        if request.method == 'GET':
            username = session['username']
            statement = sqlalchemy.text(f"SELECT id, hirer_username, email, status FROM jobs "
                                        f"INNER JOIN users "
                                        f"ON hirer_username = username "
                                        f"WHERE sitter_username LIKE '{username}';")
            res = db.execute(statement).fetchall()
            print("res:")
            print(res)
            jobs = []
            data = {}
            for result in res:
                data = {'id':result[0], 
                        'hirer':result[1], 
                        'hirerEmail':result[2], 
                        'jobStatus':result[3]}
                jobs.append(data)
                data = {}
            print("jsonified jobs")
            print(jsonify(jobs))
            return jsonify(jobs), 200
    except Exception as e:
        return Response("Something went wrong", 403)
    
@app.route('/dashboard', methods = ['GET'])
def dashboard():
    try:
        #number of users
        statement1= sqlalchemy.text(f"SELECT COUNT(*) FROM users")
        res1= db.execute(statement1).fetchone()
        print(f"res1 is {res1}")

        #number of petsitters
        statement2= sqlalchemy.text(f"SELECT COUNT(*) FROM petsitters")
        res2= db.execute(statement2).fetchone()
        print(f"res2 is {res2}")

        #percentage of users who are petsitters
        statement3= sqlalchemy.text(f"SELECT ROUND(((SELECT COUNT(*) * 100.0 FROM petsitters) / COUNT(*) ), 2) as percentage_petsitters "
                                    f"FROM users;")
        res3= db.execute(statement3).fetchone()
        print(f"res3 is {res3}")

        #top 5 most expensive petsitters who offer petboarding services
        statement4= sqlalchemy.text(f"SELECT username, price FROM petsitters "
                                    f"WHERE petBoarding = true "
                                    f"ORDER BY price "
                                    f"DESC LIMIT 5;")
        res4= db.execute(statement4).fetchall()
        print(f"res4 is {res4[0]}")

        #number of users who have not made any bookings with petsitters
        statement5= sqlalchemy.text(f"SELECT COUNT(username) "
                                    f"FROM users " 
                                    f"WHERE username NOT IN ( "
                                    f"SELECT DISTINCT hirer_username "
                                    f"FROM jobs);")
        res5= db.execute(statement5).fetchone()
        print(f"res5 is {res5}")

        #average price rate of petsitters who have completed jobs
        statement6= sqlalchemy.text(f"SELECT ROUND(AVG(price),2) "
                                    f"FROM petsitters "
                                    f"WHERE username IN ( "
                                    f"SELECT sitter_username "
                                    f"FROM jobs " 
                                    f"WHERE status = 'Completed');")
        res6= db.execute(statement6).fetchone()
        print(f"res5 is {res6}")
        
        #top 3 most popular services offered by petsitters
        statement7= sqlalchemy.text(f"SELECT 'petBoarding' AS service, "
                                    f"SUM(CASE WHEN petBoarding = 'TRUE' THEN 1 ELSE 0 END) AS count "
                                    f"FROM petsitters "
                                    f"UNION ALL "
                                    f"SELECT 'dogWalking' AS service, "
                                    f"SUM(CASE WHEN dogWalking = 'TRUE' THEN 1 ELSE 0 END) AS count "
                                    f"FROM petsitters "
                                    f"UNION ALL "
                                    f"SELECT 'petGrooming' AS service, "
                                    f"SUM(CASE WHEN petGrooming = 'TRUE' THEN 1 ELSE 0 END) AS count "
                                    f"FROM petsitters "
                                    f"UNION ALL "
                                    f"SELECT 'petDaycare' AS service, "
                                    f"SUM(CASE WHEN petDaycare = 'TRUE' THEN 1 ELSE 0 END) AS count "
                                    f"FROM petsitters "
                                    f"UNION ALL "
                                    f"SELECT 'petSitting' AS service, "
                                    f"SUM(CASE WHEN petSitting = 'TRUE' THEN 1 ELSE 0 END) AS count "
                                    f"FROM petsitters "
                                    f"UNION ALL "
                                    f"SELECT 'petTaxi' AS service, "
                                    f"SUM(CASE WHEN petTaxi = 'TRUE' THEN 1 ELSE 0 END) AS count "
                                    f"FROM petsitters "
                                    f"ORDER BY count DESC "
                                    f"LIMIT 3;")

        res7= db.execute(statement7).fetchall()
        print(f"res7 is {res7}")

        adminItems=[]
        data = {
            "totalUsers": res1[0],
            "totalPetsitters": res2[0],
            "percentageSitters": res3[0],
            "top5ExpSitters": [{"username": res4[0][0], "price": float(res4[0][1])},
                               {"username": res4[1][0], "price": float(res4[1][1])},
                               {"username": res4[2][0], "price": float(res4[2][1])},
                               {"username": res4[3][0], "price": float(res4[3][1])},
                               {"username": res4[4][0], "price": float(res4[4][1])}
                              ],
            "numUsersWoBooking": res5[0],
            "avgPriceRateComp": res6[0],
            "top3Services": [{"service": res7[0][0], "count": res7[0][1]},
                             {"service": res7[1][0], "count": res7[1][1]},
                             {"service": res7[2][0], "count": res7[2][1]}]
            }
        adminItems.append(data)
        return jsonify(adminItems), 200
    except Exception as e:
        print(e)
        return Response("Something went wrong", 403)

@app.route('/adminSettings', methods=['GET'])
def adminSettings():
    try:
        statement = sqlalchemy.text(f"SELECT username, email "
                                    f"FROM users "
                                    f"EXCEPT "
                                    f"SELECT username, email "
                                    f"FROM users "
                                    f"WHERE username LIKE 'admin';")
        res = db.execute(statement).fetchall()
        print("res:")
        print(res)
        userData= []
        data = {}
        for result in res:
            data = {'username':result[0], 
                    'email':result[1]}
            userData.append(data)
            data = {}
        return jsonify(userData), 200
    except Exception as e:
        return Response("Something went wrong", 403)
    
@app.route('/adminSettings/deleteUser/<string:username>', methods=['POST'])
def deleteUsers(username):
    try:
        statement = sqlalchemy.text(f"DELETE FROM petsitters WHERE username = :username")
        db.execute(statement, {'username': username})
        db.commit()
        statement = sqlalchemy.text(f"DELETE FROM users WHERE username = :username")
        db.execute(statement, {'username': username})
        db.commit()
        return Response("User deleted", 200)
    except Exception as e:
        return Response("Something went wrong", 403)


if __name__ == '__main__':  # If the script that was run is this script (we have not been imported)
    # app.run(host='172.25.77.198', debug=True)  # Start the server
    app.run(debug=True) 
