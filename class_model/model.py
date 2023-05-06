from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Flatten
from keras.layers.convolutional import Conv2D, MaxPooling2D
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tensorflow import keras

model = keras.models.load_model("model_load.h5")

age = float(input('나이 : '))
sex = float(input('성별 : '))
xt = np.array([[age,sex]])

output = model.predict(xt)

for i in range(len(output[0])):
	if(np.max(output)==output[0][i]).all():
		print("class : ", i)
