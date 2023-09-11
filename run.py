import threading
from flask import Flask, request, jsonify, render_template
import cv2
import sqlite3

app = Flask(__name__)

# ... Define your Flask routes and functions ...

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


# Define your OpenCV functions (face detection, age, gender) here.

def is_new_face(bbox, faces_set, tolerance=30):
    x_center = (bbox[0] + bbox[2]) / 2
    y_center = (bbox[1] + bbox[3]) / 2

    for face in faces_set:
        x_diff = abs(x_center - (face[0] + face[2]) / 2)
        y_diff = abs(y_center - (face[1] + face[3]) / 2)

        if x_diff < tolerance and y_diff < tolerance:
            return False

    return True

def faceBox(faceNet,frame):
    frameHeight=frame.shape[0]
    frameWidth=frame.shape[1]
    blob=cv2.dnn.blobFromImage(frame, 1.0, (300,300), [104,117,123], swapRB=False)
    faceNet.setInput(blob)
    detection=faceNet.forward()
    bboxs=[]
    for i in range(detection.shape[2]):
        confidence=detection[0,0,i,2]
        if confidence>0.7:
            x1=int(detection[0,0,i,3]*frameWidth)
            y1=int(detection[0,0,i,4]*frameHeight)
            x2=int(detection[0,0,i,5]*frameWidth)
            y2=int(detection[0,0,i,6]*frameHeight)
            bboxs.append([x1,y1,x2,y2])
            cv2.rectangle(frame, (x1,y1),(x2,y2),(0,255,0), 1)
    return frame, bboxs


def camera_thread():
    # Initialize OpenCV
    faceProto = "opencv_face_detector.pbtxt"
    faceModel = "opencv_face_detector_uint8.pb"
    faceNet = cv2.dnn.readNet(faceModel, faceProto)

    ageProto = "age_deploy.prototxt"
    ageModel = "age_net.caffemodel"
    ageNet = cv2.dnn.readNet(ageModel, ageProto)

    genderProto = "gender_deploy.prototxt"
    genderModel = "gender_net.caffemodel"
    genderNet = cv2.dnn.readNet(genderModel, genderProto)

    MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
    ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
    genderList = ['Male', 'Female']

    video = cv2.VideoCapture(0)
    padding = 20
    processed_faces = set()

    while True:
        ret, frame = video.read()
        frame, bboxs = faceBox(faceNet, frame)

        for bbox in bboxs:
            if is_new_face(bbox, processed_faces):
                processed_faces.add(tuple(bbox))

                face = frame[max(0, bbox[1] - padding):min(bbox[3] + padding, frame.shape[0] - 1),
                            max(0, bbox[0] - padding):min(bbox[2] + padding, frame.shape[1] - 1)]

                blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False)

                ageNet.setInput(blob)
                agePred = ageNet.forward()
                age = ageList[agePred[0].argmax()]

                genderNet.setInput(blob)
                genderPred = genderNet.forward()
                gender = genderList[genderPred[0].argmax()]

                # Insert the age and gender values into the database
                conn = sqlite3.connect('age_gender.db')
                c = conn.cursor()
                c.execute("INSERT INTO person_data (age, gender) VALUES (?, ?)", (age, gender))
                conn.commit()
                conn.close()

            label = "{},{}".format(gender, age)
            cv2.rectangle(frame, (bbox[0], bbox[1] - 30), (bbox[2], bbox[1]), (0, 255, 0), -1)
            cv2.putText(frame, label, (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow("Age-Gender", frame)
        k = cv2.waitKey(1)
        if k == ord('q'):
            break

    # Release the video capture
    video.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    # Create a thread for the camera
    camera_thread = threading.Thread(target=camera_thread)
    camera_thread.daemon = True  # Make the camera thread a daemon so it exits when the main thread exits

    # Start the camera thread
    camera_thread.start()

    # Start the Flask app
    app.run(debug=True)