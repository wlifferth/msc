import logging
import numpy as np
import os
import pickle
import pandas as pd
import tensorflow as tf
import warnings

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
    tokeniizer = load_tokenizer()
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
    context = {}
    if request.method == "POST":
        print("POST!")
        output = predict(request.form["text"])
        label = get_human_readable_label(output)
        context["label"] = label
        print(output)
    return render_template("home.html", css_url=css_url, context=context)

@app.route('/api/classify', methods=["GET"])
def get_obscenity():
    # initialize the data dictionary that will be returned from the
    # view
    data = {"success": False}

    # ensure an image was properly uploaded to our endpoint
    if flask.request.method == "POST":
        if not flask.request.json or not "text" in flask.request.json:
            text = flask.request.json["text"]
            model_output = predict
            data["troll_score"] = [text]

            # loop over the results and add them to the list of
            # returned predictions
            for (imagenetID, label, prob) in results[0]:
                r = {"label": label, "probability": float(prob)}
                data["predictions"].append(r)

            # indicate that the request was a success
            data["success"] = True

    # return the data dictionary as a JSON response
    return flask.jsonify(data)

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == "__main__":
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host="127.0.0.1", port=7070, debug=True)
