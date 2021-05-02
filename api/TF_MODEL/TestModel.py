import cv2
import tensorflow_hub as hub
import tensorflow as tf
import numpy as np
from django.core.files.uploadedfile import InMemoryUploadedFile
from tensorflow.keras.models import load_model
import os


def tf_test_model(path_to_file):
	# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

	print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
	current_dir = os.path.dirname(__file__)

	model = load_model(f'{current_dir}\saved_model.h5', custom_objects={'KerasLayer': hub.KerasLayer})
	# filepath = "test_data/NormalG0 (2).png"

	CATEGORIES = ['Normal', 'Doubtful', 'Mild', 'Moderate', 'Severe']

	print(f"Predicting file {path_to_file}")
	IMG_SIZE = 224
	arr = cv2.imread(path_to_file, cv2.IMREAD_COLOR)
	new_arr = cv2.resize(arr, (IMG_SIZE, IMG_SIZE))
	image = new_arr.reshape(-1, IMG_SIZE, IMG_SIZE, 3)
	image = image / 255
	prediction = model.predict(image)
	print(f"Prediction: {CATEGORIES[prediction.argmax()]}\t\tConfidence: {int(prediction[0][prediction.argmax()] * 100)}")
	return {"prediction": CATEGORIES[prediction.argmax()], "confidence": int(prediction[0][prediction.argmax()] * 100), "index": int(prediction.argmax())}
