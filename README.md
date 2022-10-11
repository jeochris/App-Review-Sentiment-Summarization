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
- Motivation : 
- ㄹㄹㄹ

**2. 리뷰 데이터 확보**
- 플레이스토어 '수면' 키워드를 가진 앱을 기준으로 리뷰 데이터 확보
- 총 20개 어플에서 19,833개의 리뷰 수집
- 각 리뷰별로 user id, rating, date, review 데이터 확보
- 자세한 코드는 data/crawling 폴더 확인
- inference 상황에서도 동일한 crawling을 진행 - crawler.py 확인

![image](https://user-images.githubusercontent.com/72757567/195042487-894372aa-2b7a-4ca8-912a-c9253a123999.png)

**3. 데이터 전처리**
- 추후 감정 분류 모델에서 발생 가능한 데이터 불균형을 해소하고자 리뷰 데이터 분포 조절
- 리뷰 데이터 특성 상, 한 리뷰 내에 긍/부정 감정이 함께 들어있음을 확인 -> 리뷰를 문장 단위로 분리
- 품사 수가 부족한 문장을 제거하도록 하여 의미가 크지 않은 문장을 제외
- 자세한 코드는 data/preprocess 폴더 확인
- inference 상황에서도 동일한 preprocess를 진행 - preprocess.py

![image](https://user-images.githubusercontent.com/72757567/195042673-305c25c4-2fdb-42d5-85a8-445025e8dc60.png)

**4. 감정 분류**
- 전처리된 리뷰 문장을 4가지 감정 클래스로 라벨링 - 부정, 긍정, 개선, 일반
  - 개선 : 긍정에도 부정에도 속하지 않는 개선 내용을 담는 문장에 대한 클래스
  - 일반 : 개인적인 이야기, 의미없는 이야기 등 기타 문장에 대한 클래스
  - [라벨링 결과](https://github.com/jeochris/App-Review-Sentiment-Summarization/blob/main/data/labeling_total.xlsx)
- pre-trained KoBERT를 활용하여 4가지 클래스로 분류하는 classification fine-tuning 진행

![image](https://user-images.githubusercontent.com/72757567/195069618-c1c59a66-a3f5-4314-a777-6fbf40abb72b.png)

- 모델 성능 향상 과정
  - 부정, 개선 클래스 분류 기준 모호 -> 부정, 개선 클래스 합쳐 3가지 클래스로 분류하도록
  - 외부 데이터 함께 활용 : 비슷한 특성의 데이터셋인 [Naver 영화 리뷰 데이터셋](https://github.com/e9t/nsmc/)
  - 일반 클래스 데이터 부족하여 데이터 증강 (5에서 이어짐)
  
![image](https://user-images.githubusercontent.com/72757567/195069483-0927c691-d126-468f-8483-edd8452c5a8f.png)


## more logic?
kobert accuracy result
등등

## Dependencies

* Python 3.9
* PyTorch 1.12.1
* dependencies in requirements.txt

## How to run
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
* app_name
  * App you want to find out
* rating
  * If you want to find out reviews only with certain rating, add this option.
  * Can be omitted.
* sentiment
  * Sentiment you want to find out.
  * Three options {negative, positive, personal}
  
## Result
(excel)

## File Description
### main
- main.py : 
- crawler.py
- preprocess.py
- kobert_classifier.py
- topic_summary.py
### model
- kobert_finetune
  - Train_Test_Accruacy : {우리 데이터}로 KoBERT를 fine tuning 진행 및 train test accuracy 계산
  - Augemantation_Train_Test : 일반 클래스를 증강하여 다시 fine tuning 진행 및 train test accuracy 계산
-
### data
- crawling
- preprocess

## Reference
- KoBERT
  - https://github.com/SKTBrain/KoBERT
  - https://velog.io/@seolini43/KOBERT%EB%A1%9C-%EB%8B%A4%EC%A4%91-%EB%B6%84%EB%A5%98-%EB%AA%A8%EB%8D%B8-%EB%A7%8C%EB%93%A4%EA%B8%B0-%ED%8C%8C%EC%9D%B4%EC%8D%ACColab
  - https://yeong-jin-data-blog.tistory.com/entry/BERT%EB%A1%9C-%ED%95%9C%EA%B8%80-%EC%98%81%ED%99%94-%EB%A6%AC%EB%B7%B0-%EA%B0%90%EC%84%B1%EB%B6%84%EC%84%9D-%ED%95%98%EA%B8%B0
  - https://inistory.tistory.com/20
- BERTopic
  - https://arxiv.org/abs/2203.05794
  - https://maartengr.github.io/BERTopic/index.html
- KoBART-summarization
  - https://github.com/seujung/KoBART-summarization
  - https://huggingface.co/gogamza/kobart-summarization
