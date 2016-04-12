import os
import re
import sys
import json
import nltk.test
import abbreviations
import portuguese_tagger_processor
from sentilex import sentiLexPairRdd
from nltk.corpus.reader import WordListCorpusReader

__output_path = "result.json"

stopwords = nltk.corpus.stopwords.words('portuguese')
reader = WordListCorpusReader('.', ['symbols.txt'])
symbols = reader.words()
reader = WordListCorpusReader('.', ['positive_emoticons.txt'])
positive_emoticons = reader.words()
reader = WordListCorpusReader('.', ['negative_emoticons.txt'])
negative_emoticons = reader.words()

tweet_tokenizer = portuguese_tagger_processor.get_tweet_tokenizer()
tagger = portuguese_tagger_processor.get_tagger()
json_result = []
tweet_dict = {}


def count_positive_emoticons(tokens):
    counter = 0
    for emoticon in positive_emoticons:
        if emoticon in tokens:
            counter += 1
    return counter


def count_negative_emoticons(tokens):
    counter = 0
    for emoticon in negative_emoticons:
        if emoticon in tokens:
            counter += 1
    return counter


def replace_symbols(text):
    for symbol in symbols:
        text = text.replace(symbol, "")
    return text


def replace_urls(text):
    return re.sub(r"http\S+", "", text)


def replace_abbreviations(tokens):
    for abbreviation in abbreviations.words.keys():
        if abbreviation in tokens:
            i = tokens.index(abbreviation)
            tokens[i] = abbreviations.words[abbreviation]
    return tokens


def remove_stopwords(tokens):
    for stopword in stopwords:
        if stopword in tokens:
            tokens.remove(stopword)
    return tokens


def remove_symbols(tokens):
    for symbol in symbols:
        if symbol in tokens:
            if symbol is "...":
                tokens[symbol] = " "
            else:
                tokens.remove(symbol)
    return tokens


def replace_user_mentions(text, user_mentions):
    if len(user_mentions) > 0:
        for user_mention in user_mentions:
            screen_name = user_mention['screen_name']
            text = text.replace("@" + screen_name, "")
    return text


def text_processor(tweet):
    text = tweet['text'].lower()
    text = replace_user_mentions(text, tweet['entities']['user_mentions'])
    text = replace_urls(text)

    if "rt" in text:
        try:
            text = replace_symbols(text.split(":")[1])
        except IndexError:
            pass
    else:
        text = replace_symbols(text)

    return text.strip()


def tokens_processor(tokens):
    tokens = remove_stopwords(tokens)
    tokens = remove_symbols(tokens)
    tokens = replace_abbreviations(tokens)
    return tokens


def sentiments_processor(text, tokens, tags):
    adjectives = []
    adverbs = []
    for tagged_word in tags:
        word = tagged_word[0]
        tag = tagged_word[1]
        if tag == "ADJ":
            adjectives.append(word)
        if tag == "ADV" or tag == "ADVL+adv":
            adverbs.append(word)

    if len(adjectives) > 0:
        positive = 0
        negative = 0
        for adjective in adjectives:
            sentiments = sentiLexPairRdd.lookup(adjective)
            has_negative_adverbs = "não" in adverbs
            if len(sentiments) > 0:
                sentiment = sentiments[0]
                if has_negative_adverbs:
                    if sentiment == 1:
                        negative += 1
                    elif sentiment == -1:
                        positive += negative
                else:
                    if sentiment == 1:
                        positive += 1
                    elif sentiment == -1:
                        negative += negative

        positive = positive + count_positive_emoticons(tokens)
        negative = negative + count_negative_emoticons(tokens)

        score = 0
        sum = positive + negative
        dif = positive - negative
        if sum > 0:
            score = dif / sum

        if score > 0.5:
            tweet_dict[text] = 'positive'
        elif score < 0.5:
            tweet_dict[text] = 'negative'
        else:
            tweet_dict[text] = 'neutral'


def tweet_processor(tweet):
    text = text_processor(tweet)
    tokens = tweet_tokenizer.tokenize(text)
    tokens = tokens_processor(tokens)
    tags = tagger.tag(tokens)
    sentiments_processor(text, tokens, tags)


def save():
    if os.path.isfile(__output_path) is False:
        for key in tweet_dict.keys():
            json_result.append({"text": key, "label": tweet_dict[key]})
        json_file = open(__output_path, 'w')
        json.dump(json_result, json_file, indent=4)
        json_file.close()
    else:
        json_file = open(__output_path, "r")
        model = json.load(json_file)
        model = list(model)
        json_file.close()
        for key in tweet_dict.keys():
            json_object = {"text": key, "label": tweet_dict[key]}
            if json_object not in model:
                model.append(json_object)
        json_file = open(__output_path, "w+")
        json_file.write(json.dumps(model, indent=4))
        json_file.close()
    sys.exit(0)
