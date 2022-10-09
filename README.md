# App-Review-Sentiment-Summarization
(한두줄요약)

## Collaborators
김종민, 김한빈, 송규원, 엄소은, 전재현, 차혜준

## Overview
(발표 pdf 링크)
(뭐를 한건지)

## more logic?
crawling & preprocessing
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


## Reference
