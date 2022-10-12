# App-Review-Sentiment-Summarization
플레이스토어 Review 데이터의 리뷰 감정에 따른 토픽별 요약 모델

## DSL 22-2 Modeling Project F조
**팀명** : 연어들<br>
**팀원** : 김종민, 김한빈, 송규원, 엄소은, 전재현, 차혜준

## Overview
[Presentation PDF](https://github.com/jeochris/App-Review-Sentiment-Summarization/blob/main/F%EC%A1%B0_%EC%97%B0%EC%96%B4%EB%93%A4_%EB%B0%9C%ED%91%9C%EC%9E%90%EB%A3%8C.pdf)
<br>
[Presentation Youtube](https://youtu.be/QVdFWApKydw?t=108)

![image](https://user-images.githubusercontent.com/72757567/194735017-3a5f7793-e91d-494c-89c2-1e7fdab443ab.png)

**1. 개요**
- Background: 
  - 로드맵 설정은 PM의 큰 고민
  - 리뷰를 통해 인사이트를 얻을 수 있으나 그 수가 너무 많음
- 기획 의도
  - 리뷰를 감정별-토픽별로 계층화하여 분리
  - 이후 각 토픽별로 요약하여 인사이트를 한줄로 표현함 
- 해결 방법 
  - Playstore Review Data를 확보 
  - KoBERT를 활용하여 감정 분류 
  - BERTopic을 활용하여 토픽 분류 
  - KoBART를 활용하여 리뷰 요약 
  - 평점별로 최종 분류

**2. 리뷰 데이터 확보**
- 플레이스토어 '수면' 키워드를 가진 앱을 기준으로 리뷰 데이터 확보
- 총 20개 어플에서 19,833개의 리뷰 수집
- 각 리뷰별로 user id, rating, date, review 데이터 확보
- 자세한 코드는 `data/crawling` 폴더 확인
- inference 상황에서도 동일한 crawling을 진행 - `crawler.py` 확인

![image](https://user-images.githubusercontent.com/72757567/195042487-894372aa-2b7a-4ca8-912a-c9253a123999.png)

**3. 데이터 전처리**
- 추후 감정 분류 모델에서 발생 가능한 데이터 불균형을 해소하고자 리뷰 데이터 분포 조절
- 리뷰 데이터 특성 상, 한 리뷰 내에 긍/부정 감정이 함께 들어있음을 확인 -> 리뷰를 문장 단위로 분리
- 품사 수가 부족한 문장을 제거하도록 하여 의미가 크지 않은 문장을 제외
- 자세한 코드는 `data/preprocess` 폴더 확인
- inference 상황에서도 동일한 preprocess를 진행 - `preprocess.py`

![image](https://user-images.githubusercontent.com/72757567/195042673-305c25c4-2fdb-42d5-85a8-445025e8dc60.png)

**4. 감정 분류**
- 전처리된 리뷰 문장을 4가지 감정 클래스로 라벨링 - 부정, 긍정, 개선, 일반
  - 개선 : 긍정에도 부정에도 속하지 않는 개선 내용을 담는 문장에 대한 클래스
  - 일반 : 개인적인 이야기, 의미없는 이야기 등 기타 문장에 대한 클래스
  - 라벨링 결과 : `data/labeling_total.xlsx`
  
![image](https://user-images.githubusercontent.com/72757567/195073668-abfdb84b-9b1e-48aa-8b8d-604c610864f1.png)

- pre-trained KoBERT를 활용하여 4가지 클래스로 분류하는 classification fine-tuning 진행
- 자세한 코드는 `model/kobert_finetune/Train_Test_Accuracy.ipynb` 파일 확인
- inference 상황에서 학습된 모델 활용 - `kobert_classifier.py`

![image](https://user-images.githubusercontent.com/72757567/195069618-c1c59a66-a3f5-4314-a777-6fbf40abb72b.png)

- 모델 성능 향상 과정 (10 epoch 기준)
  - 기존 : test 기준 73%
  - 부정, 개선 클래스 분류 기준 모호 -> 부정, 개선 클래스 합쳐 3가지 클래스로 분류하도록 : test 기준 85%
  - 외부 데이터 함께 활용 : 비슷한 특성의 데이터셋인 [Naver 영화 리뷰 데이터셋](https://github.com/e9t/nsmc/) : test 기준 87%
  - 일반 클래스 데이터 부족하여 데이터 증강 (5에서 이어짐)
  
![image](https://user-images.githubusercontent.com/72757567/195069483-0927c691-d126-468f-8483-edd8452c5a8f.png)

**5. 리뷰 데이터 증강**
- 일반 클래스 리뷰 데이터가 부족하여 이에 대해 데이터 증강 -> 1201개의 일반 문장 확보
- Easy Data Augmentation (EDA) 방식을 활용
  - SR, RI, RD, RS를 stochastic하게 적용
  - `` 파일 확인
- 모델 성능은 오히려 감소
  - 증강 전 데이터 자체가 부족, 일반 문장 간의 공통점이 적기 때문인 것으로 판단
  - `model/kobert_finetune/Augemantation_Train_Test.ipynb` 파일 확인

**6. 토픽 모델링**
- BERTopic 활용 : 토픽 모델링 기법으로서, BERT 기반의 embedding + class-based TF-IDF 활용
- 각 감정 클래스 내에서 BERTopic 수행
  - 보다 좋은 토픽 추출을 위해 각 문장에서 명사만 남기고 BERTopic 수행

![image](https://user-images.githubusercontent.com/72757567/195073961-a128c968-4747-43b6-a2db-dbe0dabaf915.png)

**7. 리뷰 요약**
- pre-trained KoBART를 summarization task에 fine-tuning한 [KoBART-summarization](https://github.com/seujung/KoBART-summarization)을 활용
  - BART : Transformer의 Bidirectional Encoder, Auto-Regressive Decoder를 합쳐서 pre-train한 모델 (denoising autoencoder) 
- 같은 토픽으로 분류된 문장끼리 모아 한 문단으로 묶은 후 KoBART-summarization 수행
- 자세한 코드는 `model/topic_summary/review_topic_summarization.ipynb` 파일 확인
- inference 상황에서도 동일한 topic modeling & summarization 진행 - `topic_summary.py`

![image](https://user-images.githubusercontent.com/72757567/195087801-41dc584d-16f6-4187-b20d-349c8c86bdaf.png)

## End-to-End Inference
위 Overview에서 설명한 전체 과정을 한꺼번에 inference할 수 있는 end-to-end pipeline code를 구성

### Dependencies

* Python 3.9
* PyTorch 1.12.1
* dependencies in requirements.txt

### How to run
1. Clone this repository.
```
git clone https://github.com/jeochris/App-Review-Sentiment-Summarization.git
cd App-Review-Sentiment-Summarization
```

2. Install pytorch and other dependencies.
```
pip install -r requirements.txt
```

3. Download our fine-tuned KoBERT model.
```
https://drive.google.com/file/d/10N0RprpvGZwnpguET_KL35Db11owD10O/view?usp=sharing
```

4. Run code with your option. - For example,
```
python main.py --app_name=미라클나잇 --rating=5 --sentiment=negative
```
`app_name`
- App you want to find out

`rating`
- If you want to find out reviews only with certain rating, add this option.
- Can be omitted.

`sentiment`
- Sentiment you want to find out.
- Three options {negative, positive, personal}
  
## Result
'Sleep Cycle' 앱의 부정 리뷰 기준으로 결과 확인 - `python main.py --app_name=슬립사이클 --sentiment=negative`

**1. Crawling, Preprocess, Sentiment Analysis**

- Result : result/sentiment/predicted_reviews_슬립사이클.xlsx

**2. Topic Modeling**

- Result : result/topic/review_nouns_topic_슬립사이클_None_negative.xlsx

**3. Summary**

- Result : result/summary/topic_and_summary_슬립사이클_None_negative.xlsx

## Result Anaylsis
'Sleep Cycle' 앱의 1점, 5점 리뷰 내 부정 리뷰 문장 기준으로 결과 확인 및 분석 - `--rating` 옵션 추가<br>
(1점 리뷰 : 이탈 예정 유저, 5점 리뷰 : 충성 유저로 간주)

![image](https://user-images.githubusercontent.com/72757567/195092233-7e05867b-dca4-4de3-85b2-4ce668f84c42.png)
![image](https://user-images.githubusercontent.com/72757567/195092307-4548089c-ef8b-4e09-8aba-78bcbe16762a.png)

## File Description
### main
- main.py : 
- crawler.py : 
- preprocess.py : 
- kobert_classifier.py :
- topic_summary.py :

### data
- crawling
  - f
- preprocess
  - f
- labeling_total.xlsx : 

### model
- kobert_finetune
  - Train_Test_Accruacy.ipynb : 라벨링 데이터로 KoBERT를 fine tuning 진행 및 train test accuracy 계산.
  - Augemantation_Train_Test.ipynb : 일반 클래스를 증강하여 다시 fine tuning 진행 및 train test accuracy 계산.
- topic_summary
  - review_topic_summarization.ipynb : 감성이 label 된 문장들을 단어 단위로 쪼갠 후, 명사들만 사용하여 토픽 모델링(BERTopic)을 수행. 나누어진 토픽들을 한 문단으로 합친 후 요약모델(kobart summarization)을 사용하여 한 문장으로 요약.

### result
- sentiment : 텍스트 전처리 후 각 문장별 감정 분류 수행 결과
- topic : 각 문장과 그에 따른 토픽 결과
- summary : 각 토픽별 요약 문장 결과

## Reference
- KoBERT
  - https://github.com/SKTBrain/KoBERT
  - https://velog.io/@seolini43/KOBERT%EB%A1%9C-%EB%8B%A4%EC%A4%91-%EB%B6%84%EB%A5%98-%EB%AA%A8%EB%8D%B8-%EB%A7%8C%EB%93%A4%EA%B8%B0-%ED%8C%8C%EC%9D%B4%EC%8D%ACColab
  - https://yeong-jin-data-blog.tistory.com/entry/BERT%EB%A1%9C-%ED%95%9C%EA%B8%80-%EC%98%81%ED%99%94-%EB%A6%AC%EB%B7%B0-%EA%B0%90%EC%84%B1%EB%B6%84%EC%84%9D-%ED%95%98%EA%B8%B0
  - https://inistory.tistory.com/20
- BERTopic
  - https://arxiv.org/abs/2203.05794
  - https://maartengr.github.io/BERTopic/index.html
  - https://dacon.io/en/competitions/official/235914/codeshare/5728
- KoBART-summarization
  - https://github.com/seujung/KoBART-summarization
  - https://huggingface.co/gogamza/kobart-summarization
