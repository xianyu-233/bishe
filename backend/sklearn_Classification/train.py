# -*- coding:utf-8 -*-

import os
import pickle
import random
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

seed = 222
random.seed(seed)
np.random.seed(seed)

def load_data(data_path):
    X,y = [],[]
    with open(data_path,'r',encoding='utf8') as f:
        for line in f.readlines():
            text,label = line.strip().split(',')
            text = ' '.join(list(text.lower()))
            X.append(text)
            y.append(label)

    index = np.arange(len(X))
    np.random.shuffle(index)
    X = [X[i] for i in index]
    y = [y[i] for i in index]
    return X,y

def run(data_path,model_save_path):
    X,y = load_data(data_path)

    # 类型标签
    label_set = sorted(list(set(y)))

    label2id = {label:idx for idx,label in enumerate(label_set)}
    id2label = {idx:label for label,idx in label2id.items()}

    # 把y转化成id值
    y = [label2id[i] for i in y]

    label_names = sorted(label2id.items(), key = lambda kv:kv[1], reverse=False)
    target_names = [i[0] for i in label_names]
    labels = [i[1] for i in label_names]

    # 对训练集进行切割
    train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=0.15, random_state=42)

    print("test:",test_y)

    # 将文本转化为特征矩阵
    vec = TfidfVectorizer(ngram_range=(1,3),min_df=0, max_df=0.9,analyzer='char',use_idf=1,smooth_idf=1, sublinear_tf=1)
    train_X = vec.fit_transform(train_X)
    test_X = vec.transform(test_X)


    # svc_clf = svm.LinearSVC(tol=0.00001, C=6.0, multi_class='ovr',class_weight='balanced',random_state=122, max_iter=1500)
    # -------------LR--------------
    LR = LogisticRegression(C=8, dual=False,n_jobs=4,max_iter=400,multi_class='ovr',random_state=122)
    LR.fit(train_X, train_y)
    pred = LR.predict(test_X)

    # -------------gbdt--------------
    gbdt = GradientBoostingClassifier(n_estimators=450, learning_rate=0.01,max_depth=8, random_state=24)
    gbdt.fit(train_X, train_y)
    pred = gbdt.predict(test_X)

    # -------------融合--------------
    pred_prob1 = LR.predict_proba(test_X)
    pred_prob2 = gbdt.predict_proba(test_X)

    pred = np.argmax((pred_prob1+pred_prob2)/2, axis=1)

    print(classification_report(test_y, pred,target_names=target_names))
    print(confusion_matrix(test_y, pred,labels=labels))

    # pickle.dump(id2label,open(os.path.join(model_save_path,'id2label.pkl'),'wb'))
    # pickle.dump(vec,open(os.path.join(model_save_path,'vec.pkl'),'wb'))
    # pickle.dump(LR,open(os.path.join(model_save_path,'LR.pkl'),'wb'))
    # pickle.dump(gbdt,open(os.path.join(model_save_path,'gbdt.pkl'),'wb'))

if __name__ == '__main__':
    run("./data/intent_recog_data.txt", "./model_file/")