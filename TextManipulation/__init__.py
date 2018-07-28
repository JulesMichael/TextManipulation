#!/usr/bin/env python3
import random
from math import floor
import time
import requests
from re import findall
from threading import Thread
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse

def get_page_text(url):
    try:
        raw_html = requests.get(url).text
        soup = bs(raw_html, 'html.parser')
        return soup.body.get_text() or None
        
    except requests.exceptions.ConnectionError:
        return None
        
    except Exception as e:
        raise e

class LoadTextsFromWeb(object):
    """
        l = LoadTextsFromWeb(startUris = [])
        l.start()
        # Pendant le scrap
        print("Hey")
        l.stop()
        # l.stop arret le scrap
        l.result()
    """

    def __init__(self,startUrls = []):
        self.urls = startUrls
        self.texts = []
        
    @staticmethod
    def get_page_text(url):
        """
        Creer une requette GET
        """
        try:
            raw_html = requests.get(url).text
            soup = bs(raw_html, 'html.parser')
            return soup.body.get_text() or None
            
        except requests.exceptions.ConnectionError:
            return None
        
        except Exception as e:
            raise e

    def run(self,function,*argv,**kwargs):
        """
        Lance une fonction à la fin de l'analyse d'une page web.  
        """
        raise NotImplementedError
    
    def start(self):
        """
        Lance le scrap
        """
        for urls in self.urls:
            pass
        raise NotImplementedError
        
    def stop(self):
        """
        Stop le scrap
        """
        raise NotImplementedError
    
    def __create_threads(self):
        """
        Creer les theads et les lance quand le nb de theads est en dessous de la limite
        """
        raise NotImplementedError
    
    def __process(self,url):
        """
        Traites les données
        """
        pass
    
    def result(self):
        """
        Return the texts
        """
        return self.texts


class InputTypeError(TypeError):
    def __init__(self, value):
        self.value = value

def groupWords(s,depth):
    if type(s) != serializer:
        raise InputTypeError("Input is'n a serializer object")
    else:
        words = s.words
        return [words[word:word+depth] for word in range(len(words)-depth)]

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
        self.depth = depth
        self.input_ = input_
        if type(input_) != serializer:
            raise InputTypeError("Input isn't a serializer object")
        else:
            self.datas = self.analyse()
        
    def analyse(self):
        datas = {}
        for sentence in self.input_.sentences:
            if sentence != "":
                words = ["START"]
                words.extend([word.lower() for word in serializer(sentence,do=["words"]).words])
                words.append("END")
                s = serializer('');s.words = words
                #grams = groupWords(s,self.depth)
                
                
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
        
    def generate(self,length=None,start=None):
        if start:
            text = [start]
        else:
            text = ["START"]

        def append_group():
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
                text.append(itemname)
        if length:
            for _ in range(length):
                append_group()
                if  text[-1] == "END":
                    break
        else:
            while text[-1] != "END":
                append_group()
            
        return (text)

class SortWordsChromosome(object):
    def __init__(self,sentence):
        self.entry = sentence[:]
        self.len = len(sentence)
        self.sentence = sentence
        # random.shuffle(self.sentence)
        i_1 = random.choice(range(self.len))
        i_2 = random.choice(range(self.len))
        self.sentence.insert(i_1, self.sentence.pop(i_2))
        self.fitness = -1
        self.__str__()
    def __str__(self):
        self.string = " ".join(self.sentence).capitalize()
        return self.string

    def __repr__(self):
        return "<Entry {} List: {}, String: \"{}\", Fitness: {}>".format(self.entry,self.sentence,self.__str__(),self.fitness)

class SortWords(object):
    def __init__(self,sentence,markov,population=50,generations=10000,start = False):
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
            chromosome = self.chromosomes[i]
            chromosome.sentence.insert(0,"START")
            chromosome.sentence.append("END")
            for j in range(len(chromosome.sentence)-1):
                mainW = chromosome.sentence[j]
                secW = chromosome.sentence[j+1]
                if self.markov.datas.get(mainW):
                    prob.append(self.markov.datas[mainW].get(secW,0))
                else:
                    prob.append(0)
            chromosome.fitness =  sum(prob) / (len(chromosome.sentence)-1 ) # * 100
            chromosome.sentence.remove("START")
            chromosome.sentence.remove("END")
    
    def makeSelection(self):
        self.chromosomes = sorted(self.chromosomes, key=lambda chromosome: chromosome.fitness, reverse=True)[:floor(len(self.chromosomes)/2)]
        
    def recreate(self):
        for _ in range(self.population - len(self.chromosomes)):
            self.chromosomes.append(SortWordsChromosome(self.sentence))
    
    def result(self):
        return self.chromosomes[0]
    
    def get_prob(self):
        return self.chromosomes[0].fitness
        