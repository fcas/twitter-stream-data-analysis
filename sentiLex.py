from pyspark import SparkContext

sentiLexFile = "sentiLexFlex.txt"
sparkContext = SparkContext("local", "SentiLex to mongodb")
sentiLexRdd = sparkContext.textFile(sentiLexFile).cache()

# sentilex_json_rdd = sentiLexRdd.map(lambda line: processing(line.split(",")[0]))
# save(sentilex_json_rdd.collect())

pairs = sentiLexRdd.map(lambda line: (line.split(",")[0], line.split(";")[3].split("=")[1]))