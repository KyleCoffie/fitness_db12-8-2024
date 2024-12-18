from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
import mysql.connector
from mysql.connector import Error
import secret
app = Flask(__name__)
ma = Marshmallow(app)

class MembersSchema(ma.Schema):
    id = fields.Int()
    name = fields.String(required=True)
    age = fields.Int(required=True)
    
    class Meta:
        fields = ("id", "name", "age")
        
member_schema = MembersSchema()
members_schema = MembersSchema(many=True)
            
class WorkoutSessionSchema(ma.Schema):
    members_id = fields.Int()
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True)
    calories_burned = fields.Int(required=True)
    session_id = fields.Int(dump_only=True)
    
    class Meta:
        fields = ("members_id", "date", "duration_minutes", "calories_burned","session_id")
        
session_schema = WorkoutSessionSchema()
sessions_schema = WorkoutSessionSchema(many=True)
            
            
def get_db_connection():
    db_name = "fitness_db"
    user = "root"
    password = secret.my_password
    host = "localhost"


    try:
        conn = mysql.connector.connect(
            database = db_name,
            user = user,
            password = password,
            host = host
        )
        
        print("Connected to MySQL database successfully")
        return conn
            
    except Error as e:
        print(f"Error: {e}")
        return None

@app.route('/members', methods=['POST'])
def add_member():
    # Logic to add a member
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify({e.messages}),400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}),500
        cursor = conn.cursor()
        new_member = (member_data['id'], member_data['name'], member_data['age'])
        query = "INSERT INTO Members (id, name, age) VALUES (%s,%s,%s)"
        cursor.execute(query,new_member)
        conn.commit()
        return jsonify({"message": "New member added successfully "}),201
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"Error": "Internal server error"}), 500
        
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/members/<int:id>', methods=['GET'])
def get_member(id):
    # Logic to retrieve a member
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}),500
        cursor = conn.cursor(dictionary=True)
               
        cursor.execute("SELECT * FROM Members where id = %s",(id,))
        member = cursor.fetchone()
        if not member:
            return jsonify({"Error": "Member not found"}),404
        return member_schema.jsonify(member)
        
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}),500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
        
        
        
@app.route("/members/<int:id>", methods=['PUT'])
def update_member(id):
    # Logic to update a member
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify({e.messages}),400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}),500
        cursor = conn.cursor()
        
        updated_member = (member_data['name'], member_data['age'], id)
        query = "UPDATE Members SET name = %s, age = %s WHERE id = %s"
        cursor.execute(query,updated_member)
        conn.commit()
        
        return jsonify({"message": "New member updated successfully "}),201
    except Error as e:
        print(f"Error: {e}")
        
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()



@app.route("/members/<int:id>", methods=['DELETE'])
def delete_member(id):
    # Logic to update a member
        
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}),500
        cursor = conn.cursor()
        member_to_remove = (id,)
        
        cursor.execute("SELECT * FROM Members where id = %s", member_to_remove)
        member = cursor.fetchone()
        if not member:
            return jsonify({"Error": "Member not found"}),404
        query = "DELETE FROM Members WHERE id = %s"
        cursor.execute(query,member_to_remove)
        conn.commit()
        
                
        return jsonify({"message": "Member removed successfully "}),200
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"Error":"Internal server Error"}),500
        
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()




@app.route('/workoutsessions', methods=['POST'])
def add_session():
    # Logic to schedule a workout session
    try:
        session_data = session_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify({e.messages}),400
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}),500
        cursor = conn.cursor()
        new_workoutsession = (session_data['members_id'], session_data['date'], session_data['duration_minutes'], session_data['calories_burned'])
        query = "INSERT INTO workoutsessions (members_id, date, duration_minutes, calories_burned) VALUES (%s,%s,%s,%s)"
        cursor.execute(query,new_workoutsession)
        conn.commit()
        return jsonify({"message": "New session added successfully "}),201
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"Error": "Internal server error"}), 500
        
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/workoutsessions/<int:id>', methods=['GET'])
def get_session(id):
    # Logic to view workout sessions
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}),500
        cursor = conn.cursor(dictionary=True)
               
        cursor.execute("SELECT * FROM workoutsessions where members_id = %s", (id,))
        member = cursor.fetchall()
        if not member:
            return jsonify({"Error": "Member not found"}),404
        return sessions_schema.jsonify(member)
        
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}),500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route("/workoutsessions/<int:session_id>", methods=['PUT'])
def update_session(session_id):
    # Logic to update a session
    try:
        session_data = session_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify({e.messages}),400
    try:
    
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}),500
        cursor = conn.cursor()
        updated_session =  (session_data['date'],session_data['duration_minutes'],session_data['calories_burned'], session_id) 
        query = "UPDATE workoutsessions SET date = %s, duration_minutes = %s, calories_burned = %s WHERE session_id = %s"
        cursor.execute(query,updated_session)
        conn.commit()
#         UPDATE Customers
# SET ContactName = 'Alfred Schmidt', City = 'Frankfurt'
# WHERE CustomerID = 1;
        return jsonify({"message": "Session updated successfully "}),201
    except Error as e:
        print(f"Error: {e}")
        
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route("/workoutsessions/<int:session_id>", methods=['DELETE'])
def delete_session(session_id):
    # Logic to delete a workoutsession
        
    try: 
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}),500
        cursor = conn.cursor()
        remove_session = (session_id,)    
        cursor.execute("SELECT * FROM workoutsessions where session_id = %s", remove_session)
        session = cursor.fetchone()
        
        if not session:
            return jsonify({"Error": "Session notfound"}),404
        query = "DELETE FROM workoutsessions WHERE session_id = %s"
        cursor.execute(query,remove_session)    
        conn.commit()
            
        return jsonify({"message": "Workout Session removed successfully "}),200
                    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"Error:Internal server Error": str(e)}),500
        
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()



if __name__ == '__main__':
    app.run(debug=True)