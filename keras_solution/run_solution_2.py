import numpy as np
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dropout, Flatten, Dense
from keras import applications
import os

# dimensions of our images.
img_width, img_height = 150, 150

top_model_weights_path = './models/bottleneck_fc_model.h5'
train_data_dir = 'data/train'
validation_data_dir = 'data/validation'
nb_train_samples = 20000
nb_validation_samples = 5000
epochs = 50
batch_size = 16




def save_bottlebeck_features():
    datagen = ImageDataGenerator()
    # datagen.mean = np.array([103.939, 116.779, 123.68], dtype=np.float32)

    # build the VGG16 network
    model = applications.VGG16(include_top=False, weights='imagenet')

    generator = datagen.flow_from_directory(
        train_data_dir,
        target_size=(img_width, img_height),
        batch_size=batch_size,
        class_mode=None,
        shuffle=False)

    bottleneck_features_train = model.predict_generator(
        generator, nb_train_samples // batch_size)
    np.save('./models/bottleneck_features_train.npy', bottleneck_features_train)

    generator = datagen.flow_from_directory(
        validation_data_dir,
        target_size=(img_width, img_height),
        batch_size=batch_size,
        class_mode=None,
        shuffle=False)
    bottleneck_features_validation = model.predict_generator(
        generator, nb_validation_samples // batch_size)
    np.save('./models/bottleneck_features_validation.npy', bottleneck_features_validation)


def train_top_model():
    train_data = np.load('./models/bottleneck_features_train.npy')
    dirs = os.listdir(train_data_dir)
    paths = []
    for dir in dirs:
        if os.path.isdir(os.path.join(train_data_dir, dir)) and not dir.startswith("."):
            paths.extend(os.listdir(os.path.join(train_data_dir, dir)))
    paths = sorted(paths)
    paths = paths[:(nb_train_samples // batch_size) * batch_size]
    train_labels = [0 if "cat" in p else 1 for p in paths]

    validation_data = np.load('./models/bottleneck_features_validation.npy')
    dirs = os.listdir(validation_data_dir)
    paths = []
    for dir in dirs:
        if os.path.isdir(os.path.join(validation_data_dir, dir)) and not dir.startswith("."):
            paths.extend(os.listdir(os.path.join(validation_data_dir, dir)))
    paths = sorted(paths)
    paths = paths[:(nb_validation_samples // batch_size) * batch_size]
    validation_labels = [0 if "cat" in p else 1 for p in paths]

    model = Sequential()
    model.add(Flatten(input_shape=train_data.shape[1:]))
    model.add(Dense(256, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(1, activation='sigmoid'))

    model.compile(optimizer='rmsprop',
                  loss='binary_crossentropy', metrics=['accuracy'])

    model.fit(train_data, train_labels,
              epochs=epochs,
              batch_size=batch_size,
              validation_data=(validation_data, validation_labels))
    model.save_weights(top_model_weights_path)


# save_bottlebeck_features()
train_top_model()