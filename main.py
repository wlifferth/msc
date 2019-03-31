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
from flask import Flask, render_template, url_for, request, jsonify
from tensorflow import keras
from keras import backend as K
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences

from Sample import Sample
from recall_metric import recall_metric

app = Flask(__name__)

with open("credentials/pyrebase.json") as pyrebase_config_file:
    pyrebase_config_json = json.load(pyrebase_config_file)
    firebase = pyrebase.initialize_app(pyrebase_config_json)
    db = firebase.database()

nlp = None
model = None
tokenizer = None
graph = None

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
        global graph
        graph = tf.get_default_graph()
    return model

def load_tokenizer(tokenizer_file="models/tokenizer.pickle"):
    global tokenizer
    if tokenizer is None:
        with open(tokenizer_file, "rb") as handle:
            tokenizer = pickle.load(handle)
    return tokenizer

def predict(text):
    global graph
    model = load_model()
    with graph.as_default():
        maxlen = 64
        tokenizer = load_tokenizer()
        text_sequence = tokenizer.texts_to_sequences([text])
        padded_text_sequence = pad_sequences(text_sequence, padding='post', maxlen=maxlen)
        model_output = model.predict(padded_text_sequence)
        return float(model_output[0][0])

def train_single(text, label):
    global graph
    model = load_model()
    with graph.as_default():
        maxlen = 64
        model.compile(optimizer='adam', loss='binary_crossentropy')
        tokenizer = load_tokenizer()
        text_sequence = tokenizer.texts_to_sequences([text])
        padded_text_sequence = pad_sequences(text_sequence, padding='post', maxlen=maxlen)
        model_label = np.array([[float(label)]])
        model.fit(padded_text_sequence, model_label,
                        epochs=1,
                        verbose=0,
                        batch_size=1,
                        class_weight={1: 10, 0: 1})

def push_sample_to_firebase(sample):
    result = db.child("samples").push(sample.get_firebase_dict())
    return result["name"]

def update_sample_in_firebase(sample_id, sample):
    result = db.child("samples").child(sample_id).update(sample.get_firebase_dict())
    print("update result: ", result)

def get_sample_from_firebase(sample_id):
    sample_firebase_record = db.child("samples").child(sample_id).get().val()
    return Sample.build_from_firebase_record(sample_firebase_record)

@app.route("/", methods=["GET", "POST"])
def home():
    context = defaultdict(lambda: "")
    if request.method == "POST":
        sample = Sample(request.form["text"], prediction_score=predict(request.form["text"]))
        sample.id = push_sample_to_firebase(sample)
        context["sample"] = sample
    return render_template("home.html", context=context)

@app.route("/_prediction_feedback")
def register_prediction_feedback():
    sample_id = request.args.get("sample_id", None, type=str)
    correct = request.args.get("correct", None, type=bool)
    if sample_id is None or correct is None:
        return jsonify(success=False)
    else:
        sample = get_sample_from_firebase(sample_id)
        if correct:
            if sample.prediction_score > 0.5:
                sample.label = 1
            else:
                sample.label = 0
        else:
            if sample.prediction_score > 0.5:
                sample.label = 0
            else:
                sample.label = 1
        sample.labeled = True
        update_sample_in_firebase(sample_id, sample)
        train_single(sample.text, sample.label)
        return jsonify(success=True)


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    context = dict()
    return render_template("error.html", error=e, css_url=css_url, context=context)

if __name__ == "__main__":
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host="127.0.0.1", port=7070, debug=True)
