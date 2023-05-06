from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Flatten
from keras.layers.convolutional import Conv2D, MaxPooling2D
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tensorflow import keras

model = keras.models.load_model("/home/a/Desktop/model_load.h5")

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
