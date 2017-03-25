from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense
from keras import backend as K
import numpy as np
from PIL import Image
import os
import csv

# dimensions of our images.
img_width, img_height = 150, 150
batch_size = 1

test_data_dir = './data/test'
results_name = 'submission_1.csv'
input_shape = (img_width, img_height, 3)

model = Sequential()
model.add(Conv2D(32, (3, 3), input_shape=input_shape))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(32, (3, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(64, (3, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Flatten())
model.add(Dense(64))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(1))
model.add(Activation('sigmoid'))

model.load_weights("./models/first_try.h5")

def preprocess_input(x):
    from keras.applications.vgg16 import preprocess_input
    X = np.expand_dims(x, axis=0)
    X = preprocess_input(X)
    return X[0]

test_datagen = ImageDataGenerator(rescale=1. / 255)
# test_datagen.mean = np.array([103.939, 116.779, 123.68], dtype=np.float32)
test_generator = test_datagen.flow_from_directory(test_data_dir,
                                                  target_size=(img_width, img_height),
                                                  batch_size=batch_size,
                                                  shuffle=False)

# Calculate class posteriors probabilities
y_probabilities = model.predict_generator(test_generator,
                                          steps=12500)
y_probabilities = [p[0] for p in y_probabilities]
# Calculate class labels

filenames = [filename.split('/')[1] for filename in test_generator.filenames]
ids = [int(filename.split('.')[0]) for filename in filenames]

submission = list(zip(ids, y_probabilities))
submission.sort(key=lambda t: t[0])

# save results as a csv file in the specified results directory
with open(results_name, 'w') as file:
    writer = csv.writer(file)
    writer.writerow(('id', 'label'))
    writer.writerows(submission)
