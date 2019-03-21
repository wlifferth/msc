import logging
import numpy as np
import os
import pickle
import pandas as pd
import tensorflow as tf
import warnings

from collections import defaultdict
from flask import Flask, render_template, url_for, request
from tensorflow import keras
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences


app = Flask(__name__)
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

def get_human_readable_label(score):
    if score > 0.9:
        return "Morally Salient (High Confidence)"
    elif score > 0.6:
        return "Morally Salient (Medium Confidence)"
    elif score > 0.5:
        return "Morally Salient (Low Confidence)"
    elif score > 0.4:
        return "Not Morally Salient (Low Confidence)"
    elif score > 0.1:
        return "Not Morally Salient (Medium Confidence)"
    else:
        return "Not Morally Salient (Low Confidence)"

@app.route("/", methods=["GET", "POST"])
def hello():
    """Return a friendly HTTP greeting."""
    css_url = url_for("static", filename="style.css")
    context = defaultdict(lambda: "")
    if request.method == "POST":
        score = predict(request.form["text"])
        label = get_human_readable_label(score)
        context["label"] = label
        context["text"] = request.form["text"]
        context["score"] = score
    return render_template("home.html", css_url=css_url, context=context)

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    context = dict()
    return render_template("error.html", error=e, css_url=css_url, context=context)

if __name__ == "__main__":
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host="127.0.0.1", port=7070, debug=True)
