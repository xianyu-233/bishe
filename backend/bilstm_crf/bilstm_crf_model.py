# coding=utf-8
import keras

from crf_layer import CRF

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
        