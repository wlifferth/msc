from tensorflow import keras
from keras import backend as K

def recall_metric(y_true, y_pred):	
    """Recall metric.	
     Only computes a batch-wise average of recall.	
     Computes the recall, a metric for multi-label classification of	
    how many relevant items are selected.	
    """	
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))	
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))	
    recall = true_positives / (possible_positives + K.epsilon())	
    return recall
