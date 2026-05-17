import numpy as np
import dlib
import face_recognition_models
from sklearn.svm import SVC
import streamlit as st

from src.database.db import get_all_students

@st.cache_resource
def load_dlib_model():
    detector = dlib.get_frontal_face_detector()
    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )
    face_rec = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )
    return detector, sp, face_rec


def get_face_embeddings(image_np):
    detector, sp, face_rec = load_dlib_model()
    faces = detector(image_np, 1)

    encodings = []
    for face in faces:
        shape = sp(image_np, face)
        face_descriptor = face_rec.compute_face_descriptor(image_np, shape, 1)
        encodings.append(np.array(face_descriptor))

    return encodings

@st.cache_resource
def get_trained_model():
    X = []
    y = []

    student_db = get_all_students()

    st.write(f"DEBUG MODEL → students in DB: {len(student_db) if student_db else 0}")
    for s in (student_db or []):
        st.write(f"  → id: {s.get('student_id')}, has_embedding: {bool(s.get('face_embedding'))}")

    if not student_db:
        return None

    for student in student_db:
        embedding = student.get('face_embedding')
        if embedding:
            X.append(np.array(embedding))
            y.append(str(student.get('student_id')))

    if len(X) == 0:
        return None

    # ✅ THIS WAS MISSING — skip SVC for single student
    if len(set(y)) < 2:
        st.write("DEBUG → only 1 student, skipping SVC")
        return {
            'clf': None,
            'X': X,
            'y': y
        }

    clf = SVC(kernel='linear', probability=True, class_weight='balanced')

    try:
        clf.fit(X, y)
    except ValueError as e:
        st.write(f"DEBUG → SVC fit failed: {e}")
        return None

    return {'clf': clf, 'X': X, 'y': y}


def train_classifier():
    # ✅ Clear cache first
    st.cache_resource.clear()
    
    # ✅ Small delay to ensure DB write is committed
    import time
    time.sleep(0.5)
    
    # ✅ Force fresh reload
    model_data = get_trained_model()
    
    return bool(model_data)


def predict_attendance(class_image_np):
    encodings = get_face_embeddings(class_image_np)
    detected_students = {}

    # ✅ Force clear cache every time (debug only)
    st.cache_resource.clear()

    model_data = get_trained_model()

    # ✅ Debug what model_data actually contains
    st.write(f"DEBUG MODEL DATA → {model_data}")

    if not model_data:
        st.write("DEBUG → model_data is None, returning early")
        return detected_students, [], len(encodings)

    clf = model_data['clf']
    X_train = model_data['X']
    y_train = model_data['y']

    all_students = sorted(list(set(y_train)))

    for encoding in encodings:

        if clf is None or len(all_students) < 2:
            # ✅ Single student mode
            predicted_id = all_students[0]
            best_match_score = np.linalg.norm(X_train[0] - encoding)
            resemblance_threshold = 0.5

        else:
            # ✅ Multi student mode — use SVC
            predicted_id = str(clf.predict([encoding])[0])

            best_match_score = float('inf')
            for i, stored_emb in enumerate(X_train):
                if y_train[i] == predicted_id:
                    dist = np.linalg.norm(stored_emb - encoding)
                    if dist < best_match_score:
                        best_match_score = dist

            resemblance_threshold = 0.6

        # ✅ Vector debug
        st.write(f"DEBUG → stored vector (first 5): {X_train[0][:5].tolist()}")
        st.write(f"DEBUG → live vector (first 5):   {encoding[:5].tolist()}")
        st.write(f"DEBUG → predicted_id: {predicted_id}, dist: {best_match_score:.4f}")

        if best_match_score <= resemblance_threshold:
            detected_students[predicted_id] = True

    return detected_students, all_students, len(encodings)