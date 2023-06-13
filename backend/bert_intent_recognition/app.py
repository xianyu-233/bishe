# -*- coding:utf-8 -*-
# import flask
# from gevent import pywsgi
import tensorflow as tf
# from keras.backend.tensorflow_backend import set_session
from bert4keras.tokenizers import Tokenizer

from bert_model import build_bert_model

# global graph,model,sess
#
#
# config = tf.compat.v1.ConfigProto()
# config.gpu_options.allow_growth=True
# sess = tf.compat.v1.Session(config=config)
# graph = tf.compat.v1.get_default_graph()
# tf.compat.v1.keras.backend.set_session(sess)

class BertIntentModel(object):
    def __init__(self):
        super(BertIntentModel, self).__init__()
        self.dict_path = 'config/vocab.txt'
        self.config_path= 'config/bert_config.json'
        self.checkpoint_path='./config/bert_model.ckpt'

        self.label_list = [line.strip() for line in open('data/label', 'r', encoding='utf8')]
        self.id2label = {idx:label for idx,label in enumerate(self.label_list)}

        self.tokenizer = Tokenizer(self.dict_path)
        self.model = build_bert_model(self.config_path,self.checkpoint_path,13)
        self.model.load_weights('./checkpoint/best_model.weights')

    def predict(self,text):
        token_ids, segment_ids = self.tokenizer.encode(text, maxlen=60)
        proba = self.model.predict([[token_ids], [segment_ids]])
        rst = {l:p for l,p in zip(self.label_list,proba[0])}
        rst = sorted(rst.items(), key = lambda kv:kv[1],reverse=True)
        name,confidence = rst[0]
        return {"name":name,"confidence":float(confidence)}


BIM = BertIntentModel()


if __name__ == '__main__':

    r = BIM.predict("请问，淋球菌性尿道炎可以怎么治疗")
    print(r)
    r = BIM.predict("你好，请问什么是淋球菌性尿道炎")
    print(r)