from builtins import eval

import numpy as np
from degree.course_data_helper import get_all
from sklearn.feature_extraction.text import TfidfVectorizer
from degree.course_data_helper import get_course_data
from degree.models import Degree

from sklearn.neural_network import MLPRegressor
from sklearn.externals import joblib

# initial subjects to train into the neural network
SUBJECTS_TO_TRAIN_INIT = []  # ["AACRD"]

tfidf = TfidfVectorizer()
course_vectors = tfidf.fit_transform(list(map(lambda x: x['_source']['description'], get_all())))
course_ids = np.identity(len(get_all())) * 100


def get_course_vector(code):
    if get_course_data([code]) is None:
        return None
    return tfidf.transform([get_course_data([code])['description']]).toarray().tolist()


def create_vector(degree_requirements):
    reqs = list(eval(degree_requirements).items())
    ave_vec = []
    for j in range(len(reqs)):
        k, v = reqs[j]
        for i in range(len(v)):
            d = v[i]
            if "code" in d:
                if d["code"] == "Elective Course":
                    break
                if get_course_vector(d["code"]) is not None:
                    if not ave_vec:
                        ave_vec = np.array(get_course_vector(d["code"])[0])
                    else:
                        ave_vec += np.array(get_course_vector(d["code"])[0])
    return np.array(ave_vec)


def create_training_arrays(degree_requirements):
    global leave_out
    leave_out = 0
    reqs = list(eval(degree_requirements).items())
    if not reqs:
        return np.array([]), np.array([])

    X = []
    Y = []
    left_out = []
    while leave_out < 8 * len(reqs):
        global training_vector
        training_vector = []
        ave_vec = []
        for j in range(len(reqs)):
            k, v = reqs[j]
            for i in range(len(v)):
                d = v[i]
                if "code" in d:
                    if d["code"] == "Elective Course":
                        break
                    if not ave_vec:
                        if leave_out == 4 * j + i + 1:
                            training_vector = d["code"]
                            left_out.append(d["code"])
                            break
                        if get_course_vector(d["code"]) is not None:
                            ave_vec = np.array(get_course_vector(d["code"])[0])
                    else:
                        if leave_out == 4 * j + i + 1:
                            training_vector = d["code"]
                            left_out.append(d["code"])
                            break
                        if get_course_vector(d["code"]) is not None:
                            ave_vec += np.array(get_course_vector(d["code"])[0])
        if not (training_vector == []):
            if get_course_data([training_vector]) is not None:
                X.append(ave_vec)
                Y.append(course_ids[int(get_course_data([training_vector])['id'])])
        leave_out += 1
    return np.array(X), np.array(Y)


def initial_network_training(degrees_to_train):
    degree_list = Degree.objects.all()
    for degree in degree_list:
        if not (degree.code in degrees_to_train):
            continue
        # print(degree.name)
        x_array, y_array = create_training_arrays(degree.requirements)
        if x_array.shape == (0,) or y_array.shape == (0,) or x_array.shape == (1, 0):
            continue
        network = MLPRegressor(hidden_layer_sizes=(1000,), activation='tanh')
        network.fit(x_array, y_array)
        test_data = list(np.argmax(network.predict(x_array), axis=1) == np.argmax(y_array, axis=1))
        # print("Accuracy:", sum(test_data) / len(test_data))
        joblib.dump(network, "network/" + degree.code + ".pkl")





def train_sample(degree):
    try:
        network = joblib.load("network/" + degree.code + ".pkl")
    except:
        # print("no network found")
        network = MLPRegressor(hidden_layer_sizes=(1000,), activation='tanh')
    reqs = dict()
    for semester in eval(str(degree.requirements)):
        for sem in semester.items():
            reqs[sem[0]] = sem[1]

    x_array, y_array = create_training_arrays(str(reqs))
    network.fit(x_array, y_array)
    test_data = list(np.argmax(network.predict(x_array), axis=1) == np.argmax(y_array, axis=1))
    # print("Accuracy:", sum(test_data) / len(test_data))
    joblib.dump(network, "network/" + degree.code + ".pkl")


def get_prediction(degree, number_of_recommendations):
    network = joblib.load("network/" + degree.code + ".pkl")

    # print(type(network_dict[degree]))
    reqs = dict()
    for semester in eval(str(degree.requirements)):
        for sem in semester.items():
            reqs[sem[0]] = sem[1]
    x_array = create_vector(str(reqs))

    ratings = np.sort(network.predict(x_array)[0])[::-1][:number_of_recommendations]
    ids = np.argsort(network.predict(x_array)[0])[::-1][:number_of_recommendations]
    return ids, ratings
