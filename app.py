import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os

st.set_page_config(page_title="Prediksi Dropout Mahasiswa", layout="centered")

# Load model
try:
    model = joblib.load("model/rdf_model.joblib")
    pca = joblib.load('model/pca_1.joblib')
except FileNotFoundError:
    st.error("Model file not found. Please check the model path.")
    st.stop()

# Load encoders and scalers
def load_encoder(feature):
    encoder_path = f"model/encoder_{feature}.joblib"
    if os.path.exists(encoder_path):
        return joblib.load(encoder_path)
    else:
        st.error(f"Encoder for {feature} not found.")
        st.stop()

def load_scaler(feature):
    scaler_path = f"model/scaler_{feature}.joblib"
    if os.path.exists(scaler_path):
        return joblib.load(scaler_path)
    else:
        st.error(f"Scaler for {feature} not found.")
        st.stop()

categorical_features = [
    "Marital_status", "Displaced", "Educational_special_needs", "Debtor",
    "Tuition_fees_up_to_date", "Gender", "Scholarship_holder", "International"
]

numerical_features = [
    "Admission_grade", "Age_at_enrollment",
    "Curricular_units_1st_sem_credited", "Curricular_units_1st_sem_enrolled",
    "Curricular_units_1st_sem_evaluations", "Curricular_units_1st_sem_approved",
    "Curricular_units_1st_sem_grade", "Curricular_units_1st_sem_without_evaluations",
    "Curricular_units_2nd_sem_credited", "Curricular_units_2nd_sem_enrolled",
    "Curricular_units_2nd_sem_evaluations", "Curricular_units_2nd_sem_approved",
    "Curricular_units_2nd_sem_grade", "Curricular_units_2nd_sem_without_evaluations"
]

rule_max_input = {
    "Admission_grade": 200,
    "Age_at_enrollment": 70,
}

st.title("🎓 Prediksi Dropout Mahasiswa")

# Input form
with st.form("form"):
    st.subheader("📋 Masukkan Data Mahasiswa")
    user_input = {}

    # Categorical features input
    for col in categorical_features:
        if col == "Marital_status":
            value = st.selectbox(f"{col}", ["Single", "Married", "Widower", "Divorced", "Facto Union", "Legally Separated"])
        elif col == "Gender":
            value = st.selectbox(f"{col}", ["Male", "Female"])
        else:
            value = st.selectbox(f"{col}", ["Yes", "No"])
        user_input[col] = value

    # Numerical features input
    for col in numerical_features:
        max_value = rule_max_input.get(col, None)
        user_input[col] = st.number_input(col, min_value=0, step=1, max_value=max_value)

    submitted = st.form_submit_button("Predict")

if submitted:
    input_df = pd.DataFrame()
    numerical_array = []

    # Encode categorical features
    print(categorical_features)
    for col in categorical_features:
        encoder = load_encoder(col)
        input_df[col] = encoder.transform([user_input[col]])

    # Scale numerical features
    for col in numerical_features:
        scaler = load_scaler(col)
        numerical_array.append(scaler.transform(np.array(user_input[col]).reshape(-1, 1)).flatten())

    numerical_df = pd.DataFrame([np.concatenate(numerical_array)], columns=numerical_features)
    input_df[["pc1_1", "pc1_2", "pc1_3", "pc1_4", "pc1_5"]] = pca.transform(numerical_df)

    # Predict
    prediction = model.predict(input_df)[0]
    label_map = {
        0: '🔴 Dropout',
        1: '🟢 Masih Kuliah',
        2: '🎓 Lulus'
    }
    st.success(f"Hasil Prediksi: {label_map.get(prediction, prediction)}")