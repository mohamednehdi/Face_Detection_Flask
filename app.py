from flask import Flask,  request, jsonify
import sqlite3
from flask import Flask, render_template



app = Flask(__name__)


@app.route('/')

def index():
    return render_template('index.html')
    

@app.route('/get_person_data', methods=['GET'])
def get_person_data():
    try:
        conn = sqlite3.connect('age_gender.db')
        cursor = conn.cursor()
        cursor.execute("SELECT age, gender , created_at FROM person_data")
        data = cursor.fetchall()
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/get_person_data_by_date', methods=['GET'])
def get_person_data_by_date():
    try:
        date = request.args.get('date')
        conn = sqlite3.connect('age_gender.db')
        cursor = conn.cursor()
        cursor.execute("SELECT age, gender , created_at FROM person_data where created_at like ?", (date+" %",))
        data = cursor.fetchall()
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)})
    

@app.route('/get_person_data_filter', methods=['GET'])
def get_person_data_filter():
    try:
        date = request.args.get('date')
        age = request.args.get('age')
        gender = request.args.get('gender')
        conn = sqlite3.connect('age_gender.db')
        cursor = conn.cursor()
        cursor.execute("SELECT age, gender , created_at FROM person_data where created_at like ? and  age like ? and gender like ?  ", ("%"+date+" %" , "%"+age+"%", gender+"%",))
        data = cursor.fetchall()
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/delete_all_data', methods=['DELETE'])
def delete_all_data():
    try:
        conn = sqlite3.connect('age_gender.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM person_data")
        conn.commit()
        conn.close()
        return jsonify({'message': 'All data deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)

