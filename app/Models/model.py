import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import pickle

# Load data 
data = pd.read_csv('Training.csv')

# Get scores to array
food = data['Food'].values
travel = data['Travel'].values
clothing = data['Clothing'].values
entertainment = data['Entertainment'].values
onlineshopping = data['Online Shopping'].values
electricity = data['Electricity Bill'].values
waterbill = data['Water Bill'].values
gas = data['Gas'].values
groceries  = data['Groceries'].values
month = data['Month'].values
total = data['total'].values

X = np.array([food, travel, clothing, entertainment, onlineshopping, electricity, waterbill, gas, groceries, month]).T
#X = np.array([month]).T
Y = np.array(total)

# Splitting training and testing data
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)

# Model Intialization
reg = LinearRegression()

reg.fit(X_train, y_train)
confidence = reg.score(X_test, y_test)

pickle.dump(reg, open('total.pkl','wb'))

#model = pickle.load( open('food.pkl','rb'))
#
#prediction = model.predict([[100]])
#a = str(prediction[0])
#print(a)

#print("Confidence : ", confidence)  # Confidence is accuracy of the model

#---------------------------------------------------------------------------model 2 FOOD
food_data = pd.read_csv('food.csv')
food = food_data['Food'].values
prediction2 = food_data['Prediction'].values

X = np.array([food]).T
#X = np.array([month]).T
Y = np.array(prediction2)

# Splitting training and testing data
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)

# Model Intialization
reg = LinearRegression()

reg.fit(X_train, y_train)
confidence = reg.score(X_test, y_test)

pickle.dump(reg, open('food.pkl','wb'))

#model2 = pickle.load( open('food.pkl','rb'))
#
#prediction2 = model2.predict([[100]])
#a = str(prediction2[0])
#print(a)

#---------------------------------------------------------------------------model 3 TRAVEL
travel_data = pd.read_csv('travel.csv')
travel = travel_data['Travel'].values
prediction3 = travel_data['Prediction'].values

X = np.array([travel]).T
#X = np.array([month]).T
Y = np.array(prediction3)

# Splitting training and testing data
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)

# Model Intialization
reg = LinearRegression()

reg.fit(X_train, y_train)
confidence = reg.score(X_test, y_test)

pickle.dump(reg, open('travel.pkl','wb'))

#model3 = pickle.load( open('travel.pkl','rb'))
#
#prediction3 = model3.predict([[100]])
#a = str(prediction3[0])
#print(a)

#---------------------------------------------------------------------------model 4 CLOTHING
clothing_data = pd.read_csv('clothing.csv')
clothing = clothing_data['Clothing'].values
prediction4 = clothing_data['Prediction'].values

X = np.array([clothing]).T
#X = np.array([month]).T
Y = np.array(prediction4)

# Splitting training and testing data
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)

# Model Intialization
reg = LinearRegression()

reg.fit(X_train, y_train)
confidence = reg.score(X_test, y_test)

pickle.dump(reg, open('clothing.pkl','wb'))

#model4 = pickle.load( open('clothing.pkl','rb'))
#
#prediction4 = model4.predict([[100]])
#a = str(prediction4[0])
#print(a)

#print("Confidence : ", confidence)  # Confidence is accuracy of the model

#---------------------------------------------------------------------------model 5 ENTERTAINMENT

entertainment_data = pd.read_csv('entertainment.csv')
entertainment = entertainment_data['Entertainment'].values
prediction5 = entertainment_data['Prediction'].values

X = np.array([entertainment]).T
#X = np.array([month]).T
Y = np.array(prediction5)

# Splitting training and testing data
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)

# Model Intialization
reg = LinearRegression()

reg.fit(X_train, y_train)
confidence = reg.score(X_test, y_test)

pickle.dump(reg, open('entertainment.pkl','wb'))

#model5 = pickle.load( open('entertainment.pkl','rb'))
#
#prediction5 = model5.predict([[100]])
#a = str(prediction5[0])
#print(a)

#print("Confidence : ", confidence)  # Confidence is accuracy of the model


#---------------------------------------------------------------------------model 6 ONLINE SHOPPING
onlineshopping_data = pd.read_csv('Online_Shopping.csv')
onlineshopping = onlineshopping_data['Online Shopping'].values
prediction6 = onlineshopping_data['Prediction'].values

X = np.array([onlineshopping]).T
#X = np.array([month]).T
Y = np.array(prediction6)

# Splitting training and testing data
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)

# Model Intialization
reg = LinearRegression()

reg.fit(X_train, y_train)
confidence = reg.score(X_test, y_test)

pickle.dump(reg, open('onlineshopping.pkl','wb'))

#model6 = pickle.load( open('onlineshopping.pkl','rb'))
#
#prediction6 = model6.predict([[100]])
#a = str(prediction6[0])
#print(a)

#print("Confidence : ", confidence)  # Confidence is accuracy of the model

#---------------------------------------------------------------------------model 7 ELECTRICITY BILL
electricitybill_data = pd.read_csv('Electricity_bill.csv')
electricitybill = electricitybill_data['Electricity Bill'].values
prediction7 = electricitybill_data['Prediction'].values

X = np.array([electricitybill]).T
#X = np.array([month]).T
Y = np.array(prediction7)

# Splitting training and testing data
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)

# Model Intialization
reg = LinearRegression()

reg.fit(X_train, y_train)
confidence = reg.score(X_test, y_test)

pickle.dump(reg, open('electricity.pkl','wb'))

#model7 = pickle.load( open('electricitybill.pkl','rb'))
#
#prediction7 = model7.predict([[100]])
#a = str(prediction7[0])
#print(a)

#print("Confidence : ", confidence)  # Confidence is accuracy of the model

#---------------------------------------------------------------------------model 8 WATER BILL
waterbill_data = pd.read_csv('Water_bill.csv')
waterbill = waterbill_data['Water Bill'].values
prediction8 = waterbill_data['Prediction'].values

X = np.array([waterbill]).T
#X = np.array([month]).T
Y = np.array(prediction8)

# Splitting training and testing data
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)

# Model Intialization
reg = LinearRegression()

reg.fit(X_train, y_train)
confidence = reg.score(X_test, y_test)

pickle.dump(reg, open('waterbill.pkl','wb'))

#model8 = pickle.load( open('waterbill.pkl','rb'))
#
#prediction8 = model8.predict([[100]])
#a = str(prediction8[0])
#print(a)

#print("Confidence : ", confidence)  # Confidence is accuracy of the model

#---------------------------------------------------------------------------model 9 GAS
gas_data = pd.read_csv('Gas.csv')
gas = gas_data['Gas'].values
prediction9 = gas_data['Prediction'].values

X = np.array([gas]).T
#X = np.array([month]).T
Y = np.array(prediction9)

# Splitting training and testing data
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)

# Model Intialization
reg = LinearRegression()

reg.fit(X_train, y_train)
confidence = reg.score(X_test, y_test)

pickle.dump(reg, open('gas.pkl','wb'))

#model9 = pickle.load( open('gas.pkl','rb'))
#
#prediction9 = model9.predict([[100]])
#a = str(prediction9[0])
#print(a)

#print("Confidence : ", confidence)  # Confidence is accuracy of the model



#---------------------------------------------------------------------------model 10 GROCERIES
groceries_data= pd.read_csv('Groceries.csv')
groceries = groceries_data['Groceries'].values
prediction10 = groceries_data['Prediction'].values

X = np.array([groceries]).T
#X = np.array([month]).T
Y = np.array(prediction10)

# Splitting training and testing data
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)

# Model Intialization
reg = LinearRegression()

reg.fit(X_train, y_train)
confidence = reg.score(X_test, y_test)

pickle.dump(reg, open('groceries.pkl','wb'))

#model10 = pickle.load( open('groceries.pkl','rb'))
#
#prediction10 = model10.predict([[100]])
#a = str(prediction10[0])
#print(a)

#print("Confidence : ", confidence)  # Confidence is accuracy of the model


