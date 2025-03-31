# 🧠 収集したデータを使ってCNNモデルを学習させるスクリプトです。
# 学習後のモデルは自動運転時に使用されます。

from tensorflow.keras.preprocessing import image as keras_image
import os
import numpy as np
from tqdm import tqdm
from PIL import ImageFile
import pandas as pd

dirname = "data.1648194303.940672/"

def image_to_tensor(img_path):
	img = keras_image.load_img(
		os.path.join(dirname, img_path),
		target_size=(120,160))
	x = keras_image.img_to_array(img)
	return np.expand_dims(x, axis=0)

def data_to_tensor(img_paths):
	list_of_tensors = [
		image_to_tensor(img_path) for img_path in tqdm(img_paths)]
	return np.vstack(list_of_tensors)

ImageFile.LOAD_TRUNCATED_IMAGES = True
# Load the data
data = pd.read_csv(os.path.join(dirname, "0_road_labels.csv"))

files = data['file']
targets = data['label'].values

tensors = data_to_tensor(files)

print(data.tail())
print(tensors.shape)
print(targets.shape)

###

import cv2
import matplotlib.pyplot as plt

# Name list
names = ['_0_forward', '_1_right', '_2_left', '_3_stop']

def display_images(img_path, ax):
	img = cv2.imread(os.path.join(dirname, img_path))
	ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

fig = plt.figure(figsize=(10, 3))
for i in range(4):
	ax = fig.add_subplot(1, 4, i + 1, xticks=[], yticks=[])
	ax.set_title(names[targets[i+4]], color='blue')
	display_images(files[i+4], ax)
plt.show()

###

from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split

tensors = tensors.reshape(-1,120,160,3)
print(tensors.shape)

tensors = tensors.astype('float32')/255
targets = to_categorical(targets, 4)

x_train, x_test, y_train, y_test = train_test_split(
		tensors,
		targets,
		test_size = 0.2,
		random_state = 1)

n = int(len(x_test)/2)
x_valid, y_valid = x_test[:n], y_test[:n]
x_test, y_test = x_test[n:], y_test[n:]

print(x_train.shape, y_train.shape)
print(x_test.shape, y_test.shape)
print(x_valid.shape, y_valid.shape)

###

import tensorflow as tf

model = tf.keras.Sequential([ #donkey car CNN
	tf.keras.layers.Conv2D(24, (5, 5), strides=(2, 2), padding="same",
		activation='relu', input_shape=x_train.shape[1:]),
	tf.keras.layers.Dropout(0.2),
	tf.keras.layers.Conv2D(32, (5, 5), strides=(2, 2), padding="same",
		activation='relu'),
	tf.keras.layers.Dropout(0.2),
	tf.keras.layers.Conv2D(64, (5, 5), strides=(2, 2), padding="same",
		activation='relu'),
	tf.keras.layers.Dropout(0.2),
	tf.keras.layers.Conv2D(64, (3, 3), padding="same", activation='relu'),
	tf.keras.layers.Dropout(0.2),
	tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
	tf.keras.layers.Dropout(0.2),
	tf.keras.layers.Flatten(),
	tf.keras.layers.Dense(100,activation='relu'),
	tf.keras.layers.Dropout(0.2),
	tf.keras.layers.Dense(50,activation='relu'),
	tf.keras.layers.Dropout(0.2),
	tf.keras.layers.Dense(4,activation='softmax')
])

model.compile(loss='categorical_crossentropy',
		optimizer='adam', metrics=['accuracy'])

history = model.fit(x_train, y_train, epochs=40,
		validation_data=(x_valid, y_valid))

loss = history.history['loss']

epochs = range(1, len(loss) + 1)

plt.plot(epochs, loss, 'g', label='Training loss')
plt.title('Training loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()

model.save("model.h5")

###

from tensorflow.keras.models import load_model

model1 = load_model('model.h5')

# Model predictions for the testing dataset
y_test_predict = model1.predict(x_test)
print(y_test_predict.shape, y_test_predict[0])
y_test_predict = np.argmax(y_test_predict,axis=1)
print(y_test_predict.shape, y_test_predict[0])

# Display true labels and predictions
fig = plt.figure(figsize=(18, 18))
for i, idx in enumerate(np.random.choice(x_test.shape[0], size=16,
						replace=False)):
	ax = fig.add_subplot(4, 4, i + 1, xticks=[], yticks=[])
	ax.imshow(np.squeeze(x_test[idx]))
	pred_idx = y_test_predict[idx]
	true_idx = np.argmax(y_test[idx])
	ax.set_title("{} ({})".format(names[pred_idx], names[true_idx]),
		color=("#4876ff" if pred_idx == true_idx else "darkred"))
plt.show()