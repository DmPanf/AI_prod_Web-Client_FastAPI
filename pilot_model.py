#@title [pilot_model(image_path)]
from tensorflow.keras.models import load_model
from tensorflow.keras import backend as K
import numpy as np

model_path = '/app/data/model.h5'
label_path = '/app/data/class_list.npy'

def dice_coef(y_true, y_pred, smooth=1):
    intersection = K.sum(y_true * y_pred, axis=[1,2,3])
    union = K.sum(y_true, axis=[1,2,3]) + K.sum(y_pred, axis=[1,2,3])
    dice = K.mean((2. * intersection + smooth)/(union + smooth), axis=0)
    return dice

def load_and_preprocess_image(image):
    #img = Image.open(image)
    #return np.array(img).reshape(-1,224,224,3)
    return np.array(image).reshape(-1,224,224,3)

def get_model_prediction(model, x_train):
    return model.predict(x_train).reshape(224,224,-1)

def postprocess_prediction(prediction, class_labels):
    prediction = np.argmax(prediction, axis=-1)
    return np.take(class_labels, prediction, axis=0)

def pilot_model(image):
    custom_objects = {'dice_coef': dice_coef}
    model = load_model(model_path, custom_objects=custom_objects)
    CLASS_LABELS = np.load(label_path)
    x_train = load_and_preprocess_image(image) # Проверить, что функция получает!
    prediction = get_model_prediction(model, x_train)
    # print(prediction.shape)
    processed_image = postprocess_prediction(prediction, CLASS_LABELS)
    return processed_image
