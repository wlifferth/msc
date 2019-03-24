import json
import logging
import numpy as np
import os
import pandas as pd
import pickle
import pyrebase
import tensorflow as tf
import warnings

from collections import defaultdict
from flask import Flask, render_template, url_for, request
from tensorflow import keras
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences

from Sample import Sample

app = Flask(__name__)

with open("credentials/pyrebase.json") as pyrebase_config_file:
    pyrebase_config_json = json.load(pyrebase_config_file)
    firebase = pyrebase.initialize_app(pyrebase_config_json)

nlp = None
model = None
tokenizer = None

def load_model(model_file="models/msa_model.json", weights_file="models/msa_weights.hdf"):
    global model
    if model is None:
        # load json and create model
        json_file = open(model_file, 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        model = keras.models.model_from_json(loaded_model_json)
        # load weights into new model
        model.load_weights(weights_file)
    return model

def load_tokenizer(tokenizer_file="models/tokenizer.pickle"):
    global tokenizer
    if tokenizer is None:
        with open(tokenizer_file, "rb") as handle:
            tokenizer = pickle.load(handle)
    return tokenizer

def predict(text):
    maxlen = 64
    model = load_model()
    tokenizer = load_tokenizer()
    text_sequence = tokenizer.texts_to_sequences([text])
    padded_text_sequence = pad_sequences(text_sequence, padding='post', maxlen=maxlen)
    model_output = model.predict(padded_text_sequence)
    return model_output[0][0]

@app.route("/", methods=["GET", "POST"])
def home():
    context = defaultdict(lambda: "")
    if request.method == "POST":
        sample = Sample(request.form["text"])
        sample.prediction_score = predict(sample.text)
        context["sample"] = sample
    return render_template("home.html", context=context)

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    context = dict()
    return render_template("error.html", error=e, css_url=css_url, context=context)

if __name__ == "__main__":
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host="127.0.0.1", port=7070, debug=True)
