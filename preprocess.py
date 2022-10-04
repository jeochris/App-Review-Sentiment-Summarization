from konlpy.tag import Kkma, Okt
import pandas as pd

class Preprocess(object):
    def __init__(self, review_dict_total):

        self.okt = Okt()
        self.kkma = Kkma()

        self.review_dict_total = review_dict_total
        self.result_sentences = []
        self.result_sentences_df = None

    def CustomTokenizer(self, corpus, stop = ['Josa','Suffix','Punctuation', 'Foreign', 'Number']):
        tokenized = []
        for i, j in self.okt.pos(corpus, stem = True, norm = True):
            if j in stop:
                continue
            tokenized.append(i)
        return tokenized

    #text를 입력받아 Kkma.sentences()를 이용해 문장단위로 나눈 뒤 sentences로 리턴
    def text2sentences(self, text):
        sentences = self.kkma.sentences(text)  #text일 때 문장별로 리스트 만듦
        for idx in range(1, len(sentences)):  #길이에 따라 문장 합침(위와 동일)
            
            # 문장의 품사가 5개 미만이면 생략
            if len(self.CustomTokenizer(sentences[idx])) <= 10:
                if sentences[idx-1] == '':
                    if sentences[idx-2] == '':
                        sentences[idx-3] += (''+sentences[idx])
                        sentences[idx] = ''
                sentences[idx-2] += ('' + sentences[idx])
            sentences[idx] = ''
            sentences[idx-1] += ('' + sentences[idx])
            sentences[idx] = ''
    
        for idx in range(0, len(sentences)):
        
            word_list = []

            # ['Punctuation', 'Foreign'] 제거
            for word, pos in self.okt.pos(sentences[idx], norm = True):
                stop = ['Punctuation', 'Foreign']
                if pos in stop:
                    word = ""
                # 문장을 예쁘게 하기 위해 임시로 ';' 붙여두기
                elif pos == 'Suffix' or pos == 'Josa':
                    word = word + ';'
                word_list.append(word)

            # 문장 클리닝 
            sentence = ''
            for word in word_list:
                if word == '':
                    continue
                elif ';' in word:
                    sentence += word[:-1]
                else: 
                    sentence += " " + word 

            sentences[idx] = sentence

        # 공란 문장 제거
        sentences__ = []
        for sentence in sentences:
            if sentence == '':
                pass
            else:
                sentences__.append(sentence)

        return sentences__

    def preprocess(self):

        tot_raw_reivew = []
        for item in self.review_dict_total.values():
            tot_raw_reivew.append(item['review'])

        for i in range(len(tot_raw_reivew)):
            changed_sentences = self.text2sentences(tot_raw_reivew[i])

            for sentence in changed_sentences:
                if len(sentence) <= 15:
                    continue
                else: 
                    self.result_sentences.append(sentence)

        print('preprocessed sentences :', len(self.result_sentences))
        print('first sentence :', self.result_sentences[0])

        self.result_sentences_df = pd.DataFrame(self.result_sentences)
        self.result_sentences_df.columns = ['Review']