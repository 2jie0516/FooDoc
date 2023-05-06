from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Flatten
from keras.layers.convolutional import Conv2D, MaxPooling2D


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#data = pd.read_excel("/home/a/Desktop/People_type.xlsx")
#data.to_csv("/home/a/Desktop/People_type.csv")
data = pd.read_csv("/home/a/Desktop/유튜브 클래스 모델.csv")

#test = pd.read_excel("/home/a/Desktop/People_type_test.xlsx")
#test.to_csv("/home/a/Desktop/People_type_test.csv")
test = pd.read_csv("/home/a/Desktop/유튜브 클래스 모델.csv")

x=np.array(data[['임산부','당뇨','고혈압','피부미용','웨이트']])
y=np.array(data['클래스'])

xt=np.array(test[['임산부','당뇨','고혈압','피부미용','웨이트']])
yt=np.array(test['클래스'])



#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, shuffle=True)

y_train = pd.get_dummies(y)
y_test = pd.get_dummies(yt)

from tensorflow import keras
#model = keras.models.load_model("/home/a/Desktop/권장섭취량분류모델/model_load.h5")

model = Sequential()
model.add(Dense(128, input_dim=5, activation='ELU'))
model.add(Dense(64, activation='ELU'))
model.add(Dense(64, activation='ELU'))
model.add(Dense(31, activation='softmax'))

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

history = model.fit(x, y_train, epochs=10000, batch_size=20)
model.save("/home/a/Desktop/model_load.h5")

a = int(input('임산부 : '))
b = int(input('당뇨 : '))
c = int(input('고혈압 : '))
d = int(input('피부미용 : '))
e = int(input('웨이트 : '))
abcde = np.array([[a,b,c,d,e]])

output = model.predict(abcde)

for i in range(len(output[0])):
	if(np.max(output)==output[0][i]).all():
		print("클래스 : ", i)
