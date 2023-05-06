from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Flatten
from keras.layers.convolutional import Conv2D, MaxPooling2D


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#data = pd.read_excel("/home/a/Desktop/People_type.xlsx")
#data.to_csv("/home/a/Desktop/People_type.csv")
data = pd.read_csv("/home/a/Desktop/권장섭취량분류모델/train.csv")

#test = pd.read_excel("/home/a/Desktop/People_type_test.xlsx")
#test.to_csv("/home/a/Desktop/People_type_test.csv")
test = pd.read_csv("/home/a/Desktop/권장섭취량분류모델/test.csv")

x=np.array(data[['age','sex']])
y=np.array(data['class'])

xt=np.array(test[['age','sex']])
yt=np.array(test['class'])

from sklearn.model_selection import train_test_split

#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, shuffle=True)

y_train = pd.get_dummies(y)
y_test = pd.get_dummies(yt)

from tensorflow import keras
model = keras.models.load_model("/home/a/Desktop/권장섭취량분류모델/model_load.h5")

#model = Sequential()
#model.add(Dense(128, input_dim=2, activation='ELU'))
#model.add(Dense(64, activation='ELU'))
#model.add(Dense(64, activation='ELU'))
#model.add(Dense(21, activation='softmax'))

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

history = model.fit(x, y_train, epochs=10000, batch_size=20)
model.save("/home/a/Desktop/권장섭취량분류모델/model_load.h5")

age = float(input('나이 : '))
sex = float(input('성별 : '))
xt = np.array([[age,sex]])

output = model.predict(xt)

for i in range(len(output[0])):
	if(np.max(output)==output[0][i]).all():
		print("class : ", i)
