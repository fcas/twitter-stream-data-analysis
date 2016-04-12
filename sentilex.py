from pyspark import SparkContext


def line_to_tuple(x):
    adjective = x[0]
    sentiment = x[1].split(";")[3].split("=")[1]
    return adjective, int(sentiment)


sentiLexFile = "sentilex.txt"
sparkContext = SparkContext("local", "SentiLex to mongodb")
sentiLexRdd = sparkContext.textFile(sentiLexFile)
# Pair RDD containing adjectives and the sentiment related with
sentiLexPairRdd = sentiLexRdd.map(lambda line: line_to_tuple(line.split(",")))
