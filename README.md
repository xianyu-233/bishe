# bishe
一个毕设
**后端主要使用的包**：

tqdm

bert4keras

Keras                            2.3.1

tensorflow                       2.0.0

pandas

py2neo

scikit-learn

fastpai

uvicorn



**使用的数据库**：neo4j-community-3.5.35

data文件夹是neo4j数据库

直接覆盖即可



**项目结构：**

--bert_intent_recognition：意图识别模块，使用的是bert+textcnn为模型

--bilstm_crf：命名实体识别，使用的是BILSTM+CRF为模型

--history：记录聊天过程中上一个实体的信息

--sklearn_Classification：聊天类型分类，使用梯度提升决策树+逻辑回归作为分类器

-App.py：项目的入口文件

-config.py：回复模板文件

-json_utils.py：操作history的文件，可以对其进行增，删，改

model.py：建立意图识别模型、实体识别模型、聊天类型分类模型

modules.py：使用模型进行模板槽位的填充，以及对话的返回等



**项目流程：**

* 判断聊天类型

  --如果判断为普通闲聊如：greet、isrobot、goodbye等，直接返回模板语句

  --如果判断为诊断：diagnosis，则进行下一步

* 查找语句中的实体，如果没找到，则读取历史记录中的实体进行查询

* 在查找语句实体过程中，同时进行语句意图判断，判断语句的意图是什么，例如判断为查询疾病定义，则使用查询疾病定义的数据库语句模板

* 如果查询数据库没有找到相应数据，那么就返回查找失败的回复模板

