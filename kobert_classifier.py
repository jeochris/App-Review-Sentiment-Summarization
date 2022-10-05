import pandas as pd
import numpy as np

import torch
from torch import nn
from torch.utils.data import Dataset

import gluonnlp as nlp
from tqdm import tqdm

#kobert
from kobert.utils import get_tokenizer
from kobert.pytorch_kobert import get_pytorch_kobert_model

class BERTDataset(Dataset):
    def __init__(self, dataset, sent_idx, label_idx, bert_tokenizer, max_len,
                 pad, pair):
        transform = nlp.data.BERTSentenceTransform(
            bert_tokenizer, max_seq_length=max_len, pad=pad, pair=pair)

        self.sentences = [transform([i[sent_idx]]) for i in dataset]
        self.labels = [np.int32(i[label_idx]) for i in dataset]

    def __getitem__(self, i):
        return (self.sentences[i] + (self.labels[i], ))

    def __len__(self):
        return (len(self.labels))

class BERTClassifier(nn.Module):
    def __init__(self,
                 bert,
                 hidden_size = 768,
                 num_classes=3,   ##클래스 수 조정##
                 dr_rate=None,
                 params=None):
        super(BERTClassifier, self).__init__()
        self.bert = bert
        self.dr_rate = dr_rate
                 
        self.classifier = nn.Linear(hidden_size , num_classes)
        if dr_rate:
            self.dropout = nn.Dropout(p=dr_rate)
    
    def gen_attention_mask(self, token_ids, valid_length):
        attention_mask = torch.zeros_like(token_ids)
        for i, v in enumerate(valid_length):
            attention_mask[i][:v] = 1
        return attention_mask.float()

    def forward(self, token_ids, valid_length, segment_ids):
        attention_mask = self.gen_attention_mask(token_ids, valid_length)
        
        _, pooler = self.bert(input_ids = token_ids, token_type_ids = segment_ids.long(), attention_mask = attention_mask.float().to(token_ids.device))
        if self.dr_rate:
            out = self.dropout(pooler)
        return self.classifier(out)

class FineTuned_KoBERT(object):
    def __init__(self, sentence_df, app_name):
        self.sentence_df = sentence_df
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.predicts = []
        self.result = None
        self.app_name = app_name

    ## Label 예측에 사용될 함수 정의
    def calc_pre(self, X, Y):
        max_vals, max_indices = torch.max(X, 1)
        for i in max_indices:
            self.predicts.append(i)
        pre1 = (max_indices == Y).sum().data.cpu().numpy()/max_indices.size()[0]
        return pre1
        
    def predict(self, data, model, vocab): #최종 예측 결과 엑셀로 저장하려면 path 지정

        # Setting parameters
        max_len = 64
        batch_size = 64
        warmup_ratio = 0.1
        num_epochs = 10
        max_grad_norm = 1
        log_interval = 200
        learning_rate =  5e-5

        ### Data Model에 넣을 수 있도록 transform 하는 과정
        d1 = pd.DataFrame({'Review': data.iloc[:,0],'Label':0})
        dataset_ = []
        for q, label in zip(d1['Review'], d1['Label'])  :
            data_2 = []
            data_2.append(q)
            data_2.append(str(label))
            dataset_.append(data_2)
        
        tokenizer = get_tokenizer()
        tok = nlp.data.BERTSPTokenizer(tokenizer, vocab, lower=False)

        data_ = BERTDataset(dataset_, 0, 1, tok, max_len, True, False)
        dataloader = torch.utils.data.DataLoader(data_, batch_size=batch_size, num_workers=1)

        model.eval()
        pre=0

        ### Label 예측해서 저장하는 과정
        for batch_id, (token_ids, valid_length, segment_ids, label) in enumerate(tqdm(dataloader)):
            token_ids = token_ids.long().to(self.device)
            segment_ids = segment_ids.long().to(self.device)
            valid_length= valid_length
            label = label.long().to(self.device)
        
            out = model(token_ids, valid_length, segment_ids)
            pre += self.calc_pre(out, label)

        ### 예측한 Label과 원래 데이터 합쳐서 데이터 프레임으로 최종 변환 및 저장
        predict_labels=[]
        for i in range(len(self.predicts)):
            if self.predicts[i] == 0:
                predict_labels.append(0)
            elif self.predicts[i] == 1:
                predict_labels.append(1)
            else:
                predict_labels.append(2)

        final = pd.DataFrame({'Review' : data.iloc[:,0],
                'Label': predict_labels})
        
        final.to_excel(f'./result/sentiment/predicted_reviews_{self.app_name}.xlsx')

        return(final)
    
    def inference(self):

        #BERT 모델, Vocabulary 불러오기
        bertmodel, vocab = get_pytorch_kobert_model(cachedir=".cache")

        model = BERTClassifier(bertmodel, dr_rate=0.5).to(self.device)
        model.load_state_dict(torch.load('./finetuned_bertmodel.pt', map_location=self.device))

        self.result = self.predict(self.sentence_df, model, vocab)

        print('predicted label for first sentence :', self.result.iloc[0]['Label'])
