import argparse

from crawler import Crawler
from preprocess import Preprocess
from kobert_classifier import FineTuned_KoBERT, BERTClassifier

def main():
    parser = argparse.ArgumentParser(description='Baseline')
    parser.add_argument('--app_name', type=str, metavar='app_name', help='App Name')
    args = parser.parse_args()

    # crawl reviews
    crawler = Crawler(args.app_name)
    crawler.crawl()

    # preprocess
    preprocess = Preprocess(crawler.review_dict_total)
    preprocess.preprocess()

    classifier = FineTuned_KoBERT(preprocess.result_sentences_df)
    classifier.inference()

if __name__ == '__main__':
	main()