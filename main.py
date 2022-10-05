import argparse

from crawler import Crawler
from preprocess import Preprocess
from kobert_classifier import FineTuned_KoBERT
from topic_summary import Topic_Modeling

def main():
    parser = argparse.ArgumentParser(description='Baseline')
    parser.add_argument('--app_name', type=str, metavar='app_name', help='App Name')
    parser.add_argument('--rating', type=str, metavar='rating', help='Target Rating')
    parser.add_argument('--sentiment', type=str, metavar='sentiment', help='Target Sentiment')
    args = parser.parse_args()

    # print(args.sentiment) # positive, negative, personal

    # crawl reviews
    crawler = Crawler(args.app_name, args.rating)
    crawler.crawl()

    # preprocess
    preprocess = Preprocess(crawler.review_dict_total)
    preprocess.preprocess()

    classifier = FineTuned_KoBERT(preprocess.result_sentences_df, args.app_name)
    classifier.inference()

    topic_modeling = Topic_Modeling(classifier.result, args.sentiment, args.app_name, args.rating)
    topic_modeling.retrive_topic()
    topic_modeling.summary()

if __name__ == '__main__':
	main()