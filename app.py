from flask import Flask, request,render_template, jsonify
import pickle
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from fuzzywuzzy import process
import ast
import numpy as np
import gzip
import joblib
from flask import jsonify
from langchain_community.llms import HuggingFaceEndpoint
from chatbot_logic import get_bot_response







app = Flask(__name__)


# ============================= Load Model ===============================
heart_model = pickle.load(open('models/rf_classifier.pkl', 'rb'))
heart_scaler = pickle.load(open('models/scaler.pkl','rb'))
disease_model = pickle.load(open('models/disease_model.pkl','rb'))
medicine_dict = pickle.load(open('models/medicine_dict.pkl', 'rb'))
diabetes_model = pickle.load(open('models/diabetes_model.sav','rb'))
diabetes_scaler = pickle.load(open('models/diabetes_scaler.sav','rb'))

















# ================================ Load CSV Model==============
data = pd.read_csv('data_files/Training.csv')
description = pd.read_csv('data_files/description.csv')
precautions = pd.read_csv('data_files/precautions_df.csv')
medications = pd.read_csv('data_files/medications.csv')
diets = pd.read_csv('data_files/diets.csv')
workout = pd.read_csv('data_files/workout_df.csv')




# ===================== Disease Prediction Important ========

# Symptoms mapping
symptom_index = data.drop('prognosis', axis=1).columns.tolist()
symptom_map = {s.replace('_', ' ').lower(): i for i, s in enumerate(symptom_index)}


# Label encoding
label_encoder = LabelEncoder()
label_encoder.fit(data['prognosis'])


# Fuzzy match symptoms
def correct_symptom(symptom):
    match,score = process.extractOne(symptom.lower(), symptom_map.keys())
    return match if score >= 80 else None


# Predict disease from symptoms

def predict_disease(symptoms):
    input_vector = [0] * len(symptom_map)
    for symptom in symptoms:
        corrected = correct_symptom(symptom)
        if corrected:
            input_vector[symptom_map[corrected]] = 1
    predicted_code = disease_model.predict([input_vector])[0]
    return label_encoder.inverse_transform([predicted_code])[0]



# Recommendation info
def get_recommendation(disease):
    info = {}

    # Description
    if disease in description['Disease'].values:
        info['description'] = description[description['Disease'] == disease]['Description'].values[0]
    else:
        info['description'] = "No description found."

    # Precautions
    if disease in precautions['Disease'].values:
        prec = precautions[precautions['Disease'] == disease].iloc[:, 1:].values.flatten()
        info['precautions'] = [p for p in prec if str(p).lower() != 'nan']
    else:
        info['precautions'] = []

    # Medications
    meds = medications[medications['Disease'] == disease]['Medication'].tolist()
    if meds and isinstance(meds[0], str):
        try:
            meds = ast.literal_eval(meds[0])
        except:
            meds = [meds[0]]
    info['medications'] = meds

    # Workout
    info['workout'] = workout[workout['disease'] == disease]['workout'].tolist()

    # Diet
    info['diet'] = diets[diets['Disease'] == disease]['Diet'].tolist()

    return info





# ====================== Drug Prediction System ============




# Reconstruct the DataFrame
new_df = pd.DataFrame(medicine_dict)


# Load similarity matrix (you can use either one)
# similarity = pickle.load(gzip.open('similarity.pkl.gz','rb))
similarity = joblib.load('similarity.joblib')



# Recommendation function
def recommend(medicine_name):
    try:
        medicine_index = new_df[new_df['Drug_Name'] == medicine_name].index[0]
    except IndexError:
        return ["Medicine not found."]
    
    distances = similarity[medicine_index]
    medicines_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    recommendations = [new_df.iloc[i[0]].Drug_Name for i in medicines_list]
    return recommendations
















#================================  Routes ====================================================
@app.route("/")
def index():
    return render_template("index.html")




@app.route("/select_option")
def select_option():
    return render_template("select_option.html")





@app.route("/disease_pred", methods = ['GET','POST'])
def disease():
     if request.method == 'POST':
        user_input = request.form['symptoms']
        user_symptoms = [s.strip() for s in user_input.split(',')]
        predicted = predict_disease(user_symptoms)
        recommendation = get_recommendation(predicted)

        return render_template('disease.html',
                               disease=predicted,
                               description=recommendation['description'],
                               precautions=recommendation['precautions'],
                               medications=recommendation['medications'],
                               workout=recommendation['workout'],
                               diet=recommendation['diet'],
                               symptoms=user_input)
   
   
     return render_template('disease.html')




@app.route('/diabetes_pred',methods = ['GET','POST'])
def diabetes_pred():
    if request.method == "POST":
        try:
            # Extract data from form
            input_data = [float(request.form[feature]) for feature in [
                'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
                'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age'
            ]]

            # Convert to NumPy and scale
            input_array = np.asarray(input_data).reshape(1, -1)
            std_data = diabetes_scaler.transform(input_array)  # use correct scaler

            # Predict using diabetes model
            prediction = diabetes_model.predict(std_data)
            if prediction[0] == 1:
                result = "The person is diabetic"
                color = "red"
            else:
                result = "The person is not diabetic"
                color = "green"
            return render_template('diabetes.html', prediction=result,color=color)

        except Exception as e:
            return render_template('diabetes.html', prediction="Error: " + str(e), color="black")

    # For GET request
    return render_template('diabetes.html')
       












# ================ Drug prediction



@app.route("/drug_pred", methods = ['GET','POST'])
def drug():
       if request.method == 'POST':
        user_input = request.form['medicine']
        results = recommend(user_input)
        return render_template('drug.html', medicine=user_input, recommendations=results)
       

       return render_template('drug.html')








@app.route("/autocomplete")
def autocomplete():
    query = request.args.get("query", "").lower()
    suggestions = [name for name in new_df['Drug_Name'].tolist() if query in name.lower()]
    return jsonify(suggestions=suggestions[:5])






# ===================== Heart Prediction System ===============

@app.route("/heart", methods = ['GET','POST'])
def heart_predict():
    if request.method == 'POST':
        male = request.form.get('male')
        age = int(request.form['age'])
        currentSmoker = request.form['currentSmoker']
        cigsPerDay = float(request.form['cigsPerDay'])
        BPMeds = request.form['BPMeds']
        prevalentStroke = request.form['prevalentStroke']
        prevalentHyp = request.form['prevalentHyp']
        diabetes = request.form['diabetes']
        totChol = float(request.form['totChol'])
        sysBP = float(request.form['sysBP'])
        diaBP = float(request.form['diaBP'])
        BMI = float(request.form['BMI'])
        heartRate = float(request.form['heartRate'])
        glucose = float(request.form['glucose'])

        prediction = predict(heart_model, heart_scaler, male, age, currentSmoker, cigsPerDay, BPMeds,
                             prevalentStroke, prevalentHyp, diabetes,
                             totChol, sysBP, diaBP, BMI, heartRate, glucose)

        if prediction == 1:
            result_text = "Positive (High Risk)"
        else:
            result_text = "Negative (Low Risk)"

        return render_template("result.html", prediction=result_text)

    # If GET
    return render_template('step_predict_main.html')


    






#============================== Heart Prediction function============================================
def predict(model, scaler, male, age, currentSmoker, cigsPerDay, BPMeds, prevalentStroke, prevalentHyp, diabetes,
            totChol, sysBP, diaBP, BMI, heartRate, glucose):

    # Convert string inputs from HTML form to integers
    male_encoded = int(male)
    currentSmoker_encoded = int(currentSmoker)
    BPMeds_encoded = int(BPMeds)
    prevalentStroke_encoded = int(prevalentStroke)
    prevalentHyp_encoded = int(prevalentHyp)
    diabetes_encoded = int(diabetes)

    # Prepare the feature array
    features = np.array([[male_encoded, age, currentSmoker_encoded, cigsPerDay,
                          BPMeds_encoded, prevalentStroke_encoded, prevalentHyp_encoded,
                          diabetes_encoded, totChol, sysBP, diaBP, BMI, heartRate, glucose]])

    # Scale the features
    scaled_features = scaler.transform(features)

    # Make the prediction
    result = model.predict(scaled_features)

    return result[0]







# ======================================== ChatBot Code ==============================================





@app.route('/chatbot')
def chatbot():
    return render_template("chatbot.html")

@app.route('/chatbot', methods=["POST"])
def chatbot_response():
    user_msg = request.get_json().get("message")
    response = get_bot_response(user_msg)
    return jsonify({"response": response})















if __name__ == "__main__":
    app.run(debug=True)
