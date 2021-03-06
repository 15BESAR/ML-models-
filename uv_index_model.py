# -*- coding: utf-8 -*-
"""UvIndex.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19rgrqfvhfcknbCc7Divf1bs4cPIFJkzs
"""

import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
import math 
from tensorflow import keras

"""### Data Cleaning"""

dfuv = pd.read_csv("EcoTrans-AQIFinalDataset - Uv Index.csv")

frames = list(range(7,len(dfuv)+7))
dfuv["list"] = frames
dfuv["Hour"] = dfuv["list"]%24

dfuv.head()

dfuv.groupby("Hour")["uvIndex"].mean()

dfuv = dfuv[dfuv["uvIndex"]>=1 ]
dfuv

dfuv.groupby("Hour")["uvIndex"].mean()

dfuv=dfuv["uvIndex"]

plt.figure(figsize = (25,7))
plt.plot(range(len(dfuv)), dfuv)

def split_counter(df,split_size):
  training = math.floor(len(df)*split_size)
  testing = math.floor(len(df) - training)

  training_set = df[:training]
  testing_set = df[training:]
  print("We have  {} for training and we have {} for testing".format(training,testing))


  return  training_set,testing_set

training_set, testing_set = split_counter(dfuv,0.9)

a = np.array(training_set)

shuffle_buffer_size = 1000
def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
    series = tf.expand_dims(series, axis=-1)
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size + 1, shift=1, drop_remainder=True)
    ds = ds.flat_map(lambda w: w.batch(window_size + 1))
    ds = ds.shuffle(shuffle_buffer)
    ds = ds.map(lambda w: (w[:-1], w[1:]))
    return ds.batch(batch_size).prefetch(1)


def model_forecast(model, series, window_size):
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size, shift=1, drop_remainder=True)
    ds = ds.flat_map(lambda w: w.batch(window_size))
    ds = ds.batch(32).prefetch(1)
    forecast = model.predict(ds)
    return forecast

tf.keras.backend.clear_session()
tf.random.set_seed(51)
np.random.seed(51)
window_size = 72
batch_size = 128
train_set = windowed_dataset(a, window_size, batch_size, shuffle_buffer_size)
print(train_set)
print(a.shape)

model = tf.keras.models.Sequential([
  tf.keras.layers.Conv1D(filters=32, kernel_size=5,
                      strides=1, padding="causal",
                      activation="relu",
                      input_shape=[None, 1]),
  tf.keras.layers.LSTM(64, return_sequences=True),
  tf.keras.layers.LSTM(64, return_sequences=True),
  tf.keras.layers.Dense(30, activation="relu"),
  tf.keras.layers.Dense(10, activation="relu"),
  tf.keras.layers.Dense(1),
  tf.keras.layers.Lambda(lambda x: x * 10)
])

lr_schedule = tf.keras.callbacks.LearningRateScheduler(
    lambda epoch: 1e-8 * 10**(epoch / 20))
optimizer = tf.keras.optimizers.SGD(learning_rate=1e-8, momentum=0.9)
model.compile(loss=tf.keras.losses.Huber(),
              optimizer=optimizer,
              metrics=["mae"])
history = model.fit(train_set, epochs=150, callbacks=[lr_schedule])

plt.semilogx(history.history["lr"], history.history["loss"])
plt.axis([1e-8, 1e-1, 0, 10])

tf.keras.backend.clear_session()
tf.random.set_seed(51)
np.random.seed(51)
train_set = windowed_dataset(a, window_size=72, batch_size=100, shuffle_buffer=shuffle_buffer_size)
model = tf.keras.models.Sequential([
  tf.keras.layers.Conv1D(filters=60, kernel_size=5,
                      strides=1, padding="causal",
                      activation="relu",
                      input_shape=[None, 1]),
  tf.keras.layers.LSTM(64, return_sequences=True),
  tf.keras.layers.LSTM(128, return_sequences=True),
  tf.keras.layers.Dense(60, activation="relu"),
  tf.keras.layers.Dropout(0.1),
  tf.keras.layers.Dense(10, activation="relu"),
  tf.keras.layers.Dense(1),
  tf.keras.layers.Lambda(lambda x: x * 10)
])


optimizer = tf.keras.optimizers.SGD(learning_rate=5e-3, momentum=0.9)
model.compile(loss=tf.keras.losses.Huber(),
              optimizer=optimizer,
              metrics=["mae"])
history = model.fit(train_set,epochs=200)

datas= np.array(dfuv)
datas

def model_forecast(model, series, window_size):
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size, shift=1, drop_remainder=True)
    ds = ds.flat_map(lambda w: w.batch(window_size))
    ds = ds.batch(32).prefetch(1)
    forecast = model.predict(ds)
    return forecast

rnn_forecast = model_forecast(model, datas[..., np.newaxis], window_size)
rnn_forecast = rnn_forecast[(len(training_set) - window_size):-1, -1, 0]

rnn_forecast

def plot_series(time, series, format="-", start=0, end=None):
    plt.plot(time[start:end], series[start:end], format)
    plt.xlabel("Time")
    plt.ylabel("Value")
    plt.grid(True)

plt.figure(figsize=(10, 6))
plot_series(range(len(testing_set)), testing_set)
plot_series(range(len(testing_set)), rnn_forecast)

tf.keras.metrics.mean_absolute_error(testing_set, rnn_forecast).numpy()

#Making dataframe
frames = {"Uv":testing_set, "Uv-Forcast": rnn_forecast}
dfforecast = pd.DataFrame(frames)
dfforecast



from google.colab import drive
drive.mount('/gdrive')

!mkdir -p saved_model

model.save('saved_model/UvIndex2')

UvModel = tf.keras.models.load_model('/gdrive/MyDrive/saved_model/UvIndex2')
# Check its architecture
UvModel.summary()

def model_forecast(model, series, window_size):
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size, shift=1, drop_remainder=True)
    ds = ds.flat_map(lambda w: w.batch(window_size))
    ds = ds.batch(32).prefetch(1)
    forecast = model.predict(ds)
    return forecast

rnn_forecast = model_forecast(model, datas[..., np.newaxis], window_size)
rnn_forecast = rnn_forecast[(len(training_set) - window_size):-1, -1, 0]

rnn_forecast

