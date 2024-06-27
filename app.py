from flask import Flask, render_template, request, session
from sklearn.ensemble import GradientBoostingRegressor
import pandas as pd
import pickle
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor,GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor

# function preprocessing app data and return predicted score
def preprocess_data(data):
    
    columns = ['Medu', 'Fedu','Mjob_health', 'Mjob_services', 'Mjob_teacher',
               'Mjob_other','Fjob_health', 'Fjob_services', 'Fjob_teacher', 
               'Fjob_other', 'studytime', 'failures', 'Dalc', 'absences','reason_home',
               'reason_other', 'reason_reputation', 'internet_yes', 'G1', 'G2']
    df = pd.DataFrame([data])
    
    X_test = pd.DataFrame(columns=columns)
    
    # Medu feature
    X_test['Medu'] = df['Medu']
    
    # Fedu feature
    X_test['Fedu'] = df['Fedu']
    
    # Mjob feature
    if df['Mjob'].iloc[0] == 'teacher':
        X_test['Mjob_teacher']=[1]
    elif df['Mjob'].iloc[0] == 'health':
        X_test['Mjob_health']=[1]
    elif df['Mjob'].iloc[0] == 'services':
        X_test['Mjob_services']=[1]
    else: X_test['Mjob_other']=[1]
    
    # Fjob feature
    if df['Fjob'].iloc[0] == 'teacher':
        X_test['Fjob_teacher']=[1]
    elif df['Fjob'].iloc[0] == 'health':
        X_test['Fjob_health']=[1]
    elif df['Fjob'].iloc[0] == 'services':
        X_test['Fjob_services']=[1]
    else: X_test['Fjob_other']=[1]
    
    # studytime feature
    X_test['studytime'] = df['studytime']
    
    # failures feature
    X_test['failures'] = df['failures']
    
    # Dalc feature
    X_test['Dalc'] = df['Dalc']
    
    # absences feature
    X_test['absences'] = df['absences']
    
    # reason feature
    if df['reason'].iloc[0] == '1':
        X_test['reason_home']=[1]
    elif df['reason'].iloc[0] == '2':
        X_test['reason_reputation']=[1]
    else: 
        X_test['reason_other']=[1]
        
    # internet feature
    if df['internet'].iloc[0] == '1':
        X_test['internet_yes']=[1]
    else: X_test['internet_yes']=[0]
    
    # G1 feature
    X_test['G1']=df['G1']
    
    # G2 feature
    X_test['G2']=df['G2']
    
    # fill Nan with 0
    X_test.fillna(0, inplace=True)
    print('******************************************')
    print (X_test)
    print('******************************************')
    
    app_data = pd.read_csv('./dataset/student/app_train_data.csv')
    
    X_train = app_data[['Medu', 'Fedu','Mjob_health', 'Mjob_services', 'Mjob_teacher', 'Mjob_other',
                        'Fjob_health', 'Fjob_services', 'Fjob_teacher', 'Fjob_other', 'studytime', 
                        'failures', 'Dalc', 'absences','reason_home', 'reason_other', 
                        'reason_reputation', 'internet_yes', 'G1', 'G2']]
    y_train = app_data['G3']
    
    # dictionary for prediction
    predict_dict = {}
        
    model1 = KNeighborsRegressor()
    model2 = SVR()
    model3 = RandomForestRegressor()
    model4 = GradientBoostingRegressor(loss="huber", n_estimators=50)
    model5 = DecisionTreeRegressor()

    models = [model1, model2, model3, model4, model5]
    model_name_list = ['KNeighborsRegressor', 'SupportVectorRegression', 'RandomForestRegressor', 'GradientBoostingRegressor',
                        'DecisionTreeRegressor']

    for i, model in enumerate(models):
        
        # traning model
        app_model = model.fit(X_train, y_train)
        
        # make predictions on the test set
        y_test_pred = app_model.predict(X_test)

        # add predict to dictionary
        predict_dict[model_name_list[i]]=f'{y_test_pred[0]:.2f}'
    
    print(predict_dict)
    return predict_dict

app = Flask(__name__)
app.config['SECRET_KEY'] = '@lethanhhiep'

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/result', methods = ['POST', 'GET'])
def result():
    if request.method == 'POST':
        to_predict_list = request.form.to_dict()
        result = preprocess_data(to_predict_list)
        session['result_data'] = result
        return render_template("index.html", more = '<button class="btn btn-3" id="moreResults">Dự đoán khác</button>', 
                               prediction = f'Điểm dự đoán: {result["GradientBoostingRegressor"]} điểm')
    if request.method == 'GET':
        result = session['result_data']
        return render_template("index.html", more = '<button class="btn btn-3" id="moreResults">Dự đoán khác</button>', 
                               prediction = f'Điểm dự đoán: {result["GradientBoostingRegressor"]} điểm')
@app.route('/more_result', methods = ['GET'])
def more_result():
    if 'result_data' in session:
        result = session['result_data']
        return render_template("more.html", more_result=result)
    else:
        return render_template("index.html")
    
if __name__ == "__main__":
    app.run(debug=True)  