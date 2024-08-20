from flask import Flask, render_template, request, session
import pandas as pd
import pickle
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor

# Load pre-trained models from disk
def load_models():
    models = {}
    for model_name in ['KNeighborsRegressor', 'SupportVectorRegression', 
                       'RandomForestRegressor', 'GradientBoostingRegressor', 
                       'DecisionTreeRegressor']:
        with open(f'models/{model_name}.pkl', 'rb') as f:
            models[model_name] = pickle.load(f)
    return models

# Function to preprocess input data and return predicted scores
def preprocess_data(data, models):
    # Define the columns and process the input data
    columns = [
        'Medu', 'Fedu', 'Mjob', 'Fjob', 'studytime', 'failures', 
        'Dalc', 'absences', 'reason', 'internet', 'G1', 'G2'
    ]
    
    # Convert input data into DataFrame and one-hot encode categorical variables
    df = pd.DataFrame([data], columns=columns)
    
    # One-hot encode the categorical variables
    df = pd.get_dummies(df, columns=['Mjob', 'Fjob', 'reason', 'internet'], drop_first=True)
    
    # Ensure all necessary columns are present (fill missing ones with 0)
    expected_columns = [
        'Medu', 'Fedu', 'studytime', 'failures', 'Dalc', 'absences', 'G1', 'G2', 
        'Mjob_health', 'Mjob_services', 'Mjob_teacher', 'Mjob_other', 
        'Fjob_health', 'Fjob_services', 'Fjob_teacher', 'Fjob_other', 
        'reason_home', 'reason_other', 'reason_reputation', 'internet_yes'
    ]
    X_test = pd.DataFrame(columns=expected_columns)
    X_test = X_test.append(df, ignore_index=True).fillna(0)
    
    # Dictionary to store predictions from each model
    predict_dict = {}
    
    # Generate predictions for each model
    for model_name, model in models.items():
        y_test_pred = model.predict(X_test)
        predict_dict[model_name] = f'{y_test_pred[0]:.2f}'
    
    return predict_dict

# Initialize the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = '@lethanhhiep'

# Load models once when the application starts
models = load_models()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/result', methods=['POST', 'GET'])
def result():
    if request.method == 'POST':
        to_predict_list = request.form.to_dict()
        result = preprocess_data(to_predict_list, models)
        session['result_data'] = result
        return render_template("index.html", more='<button class="btn btn-3" id="moreResults">Dự đoán khác</button>', 
                               prediction=f'Điểm dự đoán: {result["GradientBoostingRegressor"]} điểm')
    elif request.method == 'GET':
        result = session.get('result_data', {})
        return render_template("index.html", more='<button class="btn btn-3" id="moreResults">Dự đoán khác</button>', 
                               prediction=f'Điểm dự đoán: {result.get("GradientBoostingRegressor", "")} điểm')

@app.route('/more_result', methods=['GET'])
def more_result():
    result = session.get('result_data', {})
    if result:
        return render_template("more.html", more_result=result)
    return render_template("index.html")

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
