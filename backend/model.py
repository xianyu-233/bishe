from bert4keras.tokenizers import Tokenizer
from bert_intent_recognition.bert_model import build_bert_model
import os
import pickle
import numpy as np
from bilstm_crf.crf_layer import CRF
from keras.preprocessing.sequence import pad_sequences
import keras

# 建立意图识别模型
class BertIntentModel(object):
    def __init__(self):
        super(BertIntentModel, self).__init__()
        self.dict_path = 'bert_intent_recognition/config/vocab.txt'
        self.config_path= 'bert_intent_recognition/config/bert_config.json'
        self.checkpoint_path='./bert_intent_recognition/config/bert_model.ckpt'

        self.label_list = [line.strip() for line in open('bert_intent_recognition/data/label', 'r', encoding='utf8')]
        self.id2label = {idx:label for idx,label in enumerate(self.label_list)}

        self.tokenizer = Tokenizer(self.dict_path)
        self.model = build_bert_model(self.config_path,self.checkpoint_path,13)
        self.model.load_weights('./bert_intent_recognition/checkpoint/best_model.weights')

    def predict(self,text):
        token_ids, segment_ids = self.tokenizer.encode(text, maxlen=60)
        proba = self.model.predict([[token_ids], [segment_ids]])
        rst = {l:p for l,p in zip(self.label_list,proba[0])}
        rst = sorted(rst.items(), key = lambda kv:kv[1],reverse=True)
        name,confidence = rst[0]
        return {"name":name,"confidence":float(confidence)}

# 聊天类型分类器
class CLFModel(object):
    def __init__(self):
        super(CLFModel, self).__init__()
        self.model_save_path = './sklearn_Classification/model_file'
        self.id2label = pickle.load(open(os.path.join(self.model_save_path, 'id2label.pkl'), 'rb'))
        self.vec = pickle.load(open(os.path.join(self.model_save_path, 'vec.pkl'), 'rb'))
        self.LR_clf = pickle.load(open(os.path.join(self.model_save_path, 'LR.pkl'), 'rb'))
        self.gbdt_clf = pickle.load(open(os.path.join(self.model_save_path, 'gbdt.pkl'), 'rb'))

    def predict(self, text):
        text = ' '.join(list(text.lower()))
        text = self.vec.transform([text])
        proba1 = self.LR_clf.predict_proba(text)
        proba2 = self.gbdt_clf.predict_proba(text)
        label = np.argmax((proba1+proba2)/2, axis=1)
        return self.id2label.get(label[0])

# 实体识别
# BILSTM-CRF模型的构造
class BiLstmCrfModel(object):
    def __init__(
            self,
            # 句子的最大长度
            max_len,
            # 词向量字典大小
            vocab_size,
            # 词向量的维度
            embedding_dim,
            # 隐层单元数量
            lstm_units,
            # 标签数量
            class_nums,
            # 词向量矩阵
            embedding_matrix=None
        ):
        super(BiLstmCrfModel, self).__init__()
        self.max_len = max_len
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.lstm_units = lstm_units
        self.class_nums = class_nums
        self.embedding_matrix = embedding_matrix
        if self.embedding_matrix is not None:
            self.vocab_size,self.embedding_dim = self.embedding_matrix.shape

    # 建立模型
    def build(self):
        # 句子输入层（输入字的特征向量）
        inputs = keras.layers.Input(
                shape=(self.max_len,),
                dtype='int32'
            )
        # 对句子的向量进行预处理
        x = keras.layers.Masking(
                mask_value=0
            )(inputs)

        # 构造嵌入层
        x = keras.layers.Embedding(
                input_dim=self.vocab_size,
                output_dim=self.embedding_dim,
                trainable=False,
                weights=self.embedding_matrix,
                mask_zero=True
            )(x)

        # 将双向LSTM的每个字的结果输出
        x = keras.layers.Bidirectional(
                keras.layers.LSTM(
                    self.lstm_units,
                    return_sequences=True
                )
            )(x)

        x = keras.layers.TimeDistributed(
                # 防止过拟合
                keras.layers.Dropout(
                    0.2
                )
            )(x)

        # CRF层
        crf = CRF(self.class_nums)
        outputs = crf(x)
        model = keras.Model(inputs=inputs, outputs=outputs)
        model.compile(
            optimizer='adam',
            loss=crf.loss_function,
            metrics=[crf.accuracy]
            )

        return model
# 构造实体识别模型
class MedicalNerModel(object):
    # 基于bilstm-crf的命名实体识别模型
    def __init__(self):
        super(MedicalNerModel, self).__init__()
        self.word2id,_,self.id2tag = pickle.load(
                open("bilstm_crf/checkpoint/word_tag_id.pkl", "rb")
            )
        self.model = BiLstmCrfModel(80,2410,200,128,24).build()
        self.model.load_weights('./bilstm_crf/checkpoint/best_bilstm_crf_model.h5')

    def tag_parser(self,string,tags):
        item = {"string": string, "entities": [],"recog_label":"model"}
        entity_name = ""
        flag=[]
        visit=False
        for char, tag in zip(string, tags):
            if tag[0] == "B":
                if entity_name!="":
                    x=dict((a,flag.count(a)) for a in flag)
                    y=[k for k,v in x.items() if max(x.values())==v]
                    item["entities"].append({"word": entity_name,"type": y[0]})
                    flag.clear()
                    entity_name=""
                entity_name += char
                flag.append(tag[2:])
            elif tag[0]=="I":
                entity_name += char
                flag.append(tag[2:])
            else:
                if entity_name!="":
                    x=dict((a,flag.count(a)) for a in flag)
                    y=[k for k,v in x.items() if max(x.values())==v]
                    item["entities"].append({"word": entity_name,"type": y[0]})
                    flag.clear()
                flag.clear()
                entity_name=""

        if entity_name!="":
            x=dict((a,flag.count(a)) for a in flag)
            y=[k for k,v in x.items() if max(x.values())==v]
            item["entities"].append({"word": entity_name,"type": y[0]})

        return item

    def predict(self,texts):
        # texts 为一维列表，元素为字符串
        X = [[self.word2id.get(word,1) for word in list(x)] for x in texts ]
        X = pad_sequences(X,maxlen=80,value=0)
        pred_id = self.model.predict(X)
        res = []
        for text,pred in zip(texts,pred_id):
            tags = np.argmax(pred,axis=1)
            tags = [self.id2tag[i] for i in tags if i!=0]
            ents = self.tag_parser(text,tags)
            if ents["entities"]:
                res.append(ents)

        return res
