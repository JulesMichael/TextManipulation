import random
from math import floor

class InputTypeError(TypeError):
    def __init__(self, value):
        self.value = value

class serializer(object):
    def __init__(self,input_,punctuation=False,do=["subsections","sentences","words"]):
        self.input_ = input_
        self.punctuation = punctuation
        if type(input_) != str:
            raise InputTypeError("Input is'n a str object")
        else:
            if "subsections" in do:
                self.subsections = self.get_subsections()
            if "sentences" in do:
                self.sentences = self.get_sentences()
            if "words" in do:
                self.words = self.get_words()
            
    def get_subsections(self):
        return self.input_.split("\n")

    def get_sentences(self):
        def process(text):
            for point in ["...", ".", ";", "?", "!"]:
                text = text.replace(point, "[%-%-%]")
            text = text.split("[%-%-%]")
            return(list(map(lambda phrase: phrase.strip(), text)))

        return process(self.input_)
    
    def get_words(self):
        if self.punctuation is False:
            return " ".join(self.get_sentences()).split(" ")
        else:
            return self.input_.split(" ")
    
            
class markov(object):
    def __init__(self,input_,depth=2):
        self.input_ = input_
        if type(input_) != serializer:
            raise InputTypeError("Input is'n a serializer object")
        else:
            self.datas = self.analyse()
        
    def analyse(self):
        datas = {}
        for sentence in self.input_.sentences:
            if sentence != "":
                words = ["START"]
                words = [word.lower() for word in serializer(sentence,do=["words"]).words]
                words.append("END")
                for wId in range(len(words)-1):
                    if not datas.get(words[wId]):
                        datas[words[wId]] = {}
                    if datas[words[wId]].get(wId + 1):
                        datas[words[wId]][wId + 1] = datas[words[wId]][words[wId + 1]] + 1
                    else:
                        datas[words[wId]][words[wId + 1]] = 1
                    
        for mainW in datas:
            for secW in datas[mainW]:
                datas[mainW][secW] = datas[mainW][secW]/len(datas[mainW])
        return datas
        
    def generate(self,length,start=None):
        if start:
            text = [start]
        else:
            text = ["START"]

        for _ in range(length):
            if self.datas.get(text[-1]):
                itemmax = 0
                itemname = []
                for item in self.datas.get(text[-1]):
                    if self.datas.get(text[-1])[item] > itemmax:
                        itemname = item
                    elif self.datas.get(text[-1])[item] == itemmax:
                        itemname.append(item)
                if type(itemname) == list:
                    itemname = random.choice(itemname)
                #text.append(" ".join(itemname))
                text.append(itemname)
        return (text)

class SortWordsChromosome(object):
    def __init__(self,sentence):
        self.entry = sentence[:]
        self.sentence = sentence
        random.shuffle(self.sentence)
        self.fitness = -1
        self.__str__()
    def __str__(self):
        self.string = " ".join(self.sentence).capitalize()
        return self.string

    def __repr__(self):
        return "<Entry {} List: {}, String: \"{}\", Fitness: {}>".format(self.entry,self.sentence,self.__str__(),self.fitness)
        
class SortWords():
    def __init__(self,sentence,markov,population=50,generations=10000):
        self.sentence = sentence
        self.sentenceLen = len(self.sentence)
        self.markov = markov
        self.population = population
        self.generations = generations
        self.chromosomes = [SortWordsChromosome(sentence[:]) for _ in range(self.population)]

        for _ in range(generations):
            self.recreate()
            self.computeFitness()
            self.makeSelection()

            
    def computeFitness(self):
        for i in range(len(self.chromosomes)):
            prob = []
            for j in range(len(self.chromosomes[i].sentence)-1):
                mainW = self.chromosomes[i].sentence[j]
                secW = self.chromosomes[i].sentence[j+1]
                if self.markov.datas.get(mainW):
                    prob.append(self.markov.datas[mainW].get(secW,0))
                else:
                    prob.append(0)
            self.chromosomes[i].fitness =  sum(prob) / (len(self.chromosomes[i].sentence)-1 ) * 100
    
    def makeSelection(self):
        self.chromosomes = sorted(self.chromosomes, key=lambda chromosome: chromosome.fitness, reverse=True)[:floor(len(self.chromosomes)/2)]
        
    def recreate(self):
        for _ in range(self.population - len(self.chromosomes)):
            self.chromosomes.append(SortWordsChromosome(self.sentence))
    
    def result(self):
        return self.chromosomes[0]