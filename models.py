# Model Planning
import numpy as np
from numpy.random import choice

from read import read_data, read_metadata, validation
from osufileparse.osuparse import HitObject
from osufileparse.osuparse import parse_beatmap

ncentroids = 16

# Snap Clustering & Classification (For snap approximation and reduce the variant of the snap data)
# KMeans 1D
def kMeans1D(X, n_centroids=8):
    # X must be 1D array
    data = np.array(X)
    centroids = choice(X, n_centroids)
    @np.vectorize
    def get_group(x):
        dist = np.abs(centroids - x)
        return np.argmin(dist)

    def get_new_centroids(d, group):
        new_centroids = []
        for i in range(n_centroids):
            new_centroid = np.mean(d[group == i])
            new_centroids.append(new_centroid)
        return np.array(new_centroids)
        
    recents = []
    while True:
        results = get_group(data)
        if results.tolist() in recents:
            break
        new_centroids = get_new_centroids(data, results)
        centroids = new_centroids.copy()
        recents.append(results.tolist())
    return centroids

def get_class_from_centroids(x, centroids):
    return np.argmin(np.abs(centroids - x))

not_tech, tech = read_data()

def get_delta(hitobjects):
    current = -1
    delta = []
    for hitobject in hitobjects:
        if current == -1:
            delta.append(0)
            current = hitobject.offset
            continue
        delta.append(hitobject.offset - current)
        current = hitobject.offset
    return delta

nt = [get_delta(n) for n in not_tech]
t = [get_delta(n) for n in tech]
data_for_clustering = []
for i in nt+t:
    data_for_clustering += i
data_for_clustering = list(set(data_for_clustering))
centroids = kMeans1D(data_for_clustering, ncentroids)
centroids = np.sort(centroids)

# osuFile with Classified Snaps -> Text
def translate_hitobjects(hitobjects):
    LANES = [chr(i) for i in range(ord("A"), ord("A") + 16)]
    delta = get_delta(hitobjects)
    translated_text = ""
    first = True
    bit = 0
    for hit, d in zip(hitobjects, delta):
        lane = hit.lane // 128
        if d == 0 and not first:
            bit += 2 ** lane
            continue
        group = get_class_from_centroids(d, centroids)
        translated_text += str(group) + LANES[bit] + " "
        first = False
        bit = 2 ** lane
    return translated_text[:-1]

nt = [translate_hitobjects(n) for n in not_tech]
t = [translate_hitobjects(n) for n in tech]
Xtrain = nt + t
Ytrain = ["Not Tech"] * len(nt) + ["Tech"] * len(t)

# TFIDF and LogReg
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(Xtrain)
Logistic_Regressor = LogisticRegression(solver='lbfgs', max_iter=100)
Logistic_Regressor.fit(X, Ytrain)

results = Logistic_Regressor.predict(X)
not_tech_meta, tech_meta = read_metadata()
meta = not_tech_meta + tech_meta
with open('results_on_train.txt', 'w+') as results_log:
    for res, y, m in zip(results, Ytrain, meta):
        results_log.write("Beatmap : {}\n".format(m))
        results_log.write("AI Prediction : {} || Actual Results : {}\n".format(res, y))

    results_log.write("Accuracy = {}%".format(np.sum(results == np.array(Ytrain)) / len(Ytrain) * 100))

ISTECH = ["Not Tech", "Tech"]
def predict(file_direction):
    file_ = parse_beatmap(file_direction)
    hit_objects = file_.HitObjects
    txt = translate_hitobjects(hit_objects)
    txt = vectorizer.transform([txt])
    results = Logistic_Regressor.predict(txt)
    correct = ISTECH[file_.metadata['IsTech']]
    return results, correct

initial_validation = "./validation/{}"
validation_metadata = read_metadata(val=True)
with open('results_on_validation.txt', 'w+') as results_log:
    correct_predict = 0
    all_data = 0
    for files, metadata in zip(validation, validation_metadata):
        result, correct = predict(initial_validation.format(files))
        result = result[0]
        results_log.write("Beatmap : {}\n".format(metadata))
        results_log.write("AI Prediction : {} || Actual Results : {}\n".format(result, correct))
        all_data += 1
        if result == correct:
            correct_predict += 1
    results_log.write("Accuracy = {}%".format(correct_predict / all_data * 100))
    print("Test Accuracy = {}%".format(correct_predict / all_data * 100))
