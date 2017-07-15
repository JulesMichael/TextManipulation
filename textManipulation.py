import json
import random
# import langdetect
# import goslate

# Génération de text


class serializer(object):
    def __init__(self, text):
        self.text = text

    def paragraphes(self):
        if type(self.text) == str:
            t = self.text.split("\n")
        else:
            t = list(map(lambda phrase: phrase.split("\n"), self.text))
        return t

    def phrases(self):
        def process(text):
            for point in ["...", ".", ";", "?", "!"]:
                text = text.replace(point, "[%-%-%]")
            text = text.split("[%-%-%]")
            return(list(map(lambda phrase: phrase.strip(), text)))

        if type(self.text) == str:
            t = process(self.text)
        else:
            print(self.text)
            t = list(map(lambda phrase: process(phrase), self.text))
        return t

    def mots(self, ponctuation=False):
        if ponctuation is False:
            return " ".join(self.phrases()).split(" ")
        else:
            return self.text.split(" ")


class markov(object):
    def __init__(self, text, ponctuation=True):
        string = text
        wordlist = serializer(string).mots(ponctuation=ponctuation)
        self.wordlist = wordlist

    def ocurances(self):
        ocurances = {}
        for word in self.wordlist:
            word = word.lower()
            ocurances[word] = ocurances.get(word, 0) + 1

        return(ocurances)

    def analyse(self):
        proba = {}
        words = self.wordlist
        for word in range(len(words)):
            try:
                wordquisuit = words[word + 1]
            except:
                wordquisuit = '.'
            if not proba.get(words[word]):
                proba[words[word]] = {}
            if proba[words[word]].get(wordquisuit):
                proba[words[word]][wordquisuit] = proba[
                    words[word]][wordquisuit] + 1
            else:
                proba[words[word]][wordquisuit] = 1

        self.proba = proba
        return self.proba

    def generate(self, number, start=None):
        if start:
            text = [start]
        else:
            word = random.choice(self.wordlist)
            text = [word]

        for x in range(number):
            if self.proba.get(text[-1]):
                itemmax = 0
                itemname = []
                for item in self.proba.get(text[-1]):
                    if self.proba.get(text[-1])[item] > itemmax:
                        itemname = item
                    elif self.proba.get(text[-1])[item] == itemmax:
                        itemname.append(item)
                if type(itemname) == list:
                    itemname = random.choice(itemname)
                text.append(itemname)
        return (text)


class jmchain(object):
    def __init__(self, json_f=None, file=None, _Dict=None):

        if json_f:
            self.datas = json.loads(json_f)
        elif file:
            self.phrases = serializer(open(file, "r").read()).phrases()
            self.m = markov(".".join(self.phrases))
            self.words_proba = self.m.analyse()
        elif _Dict:
            self.datas = _Dict

    def order(self, words):
        output = []
        for word in words:
            for wordp in words:
                if word != wordp:
                    if self.datas.get(word):
                        if self.datas[word].get(wordp):
                            if self.datas[word][wordp][1] >= 1:
                                output.append((word, wordp))
                            elif self.datas[word][wordp][1] >= 0:
                                output.append((wordp, word))
        print(output)
        return output

    def analyse(self):
        datas = dict()
        self.phrases = map(lambda l: l.replace("\n", ""), self.phrases)
        for phrase in self.phrases:
            phraseliste = phrase.split(" ")
            while "" in phraseliste:
                phraseliste.remove("")
            for mot in phraseliste:
                for motprim in phraseliste:
                    if motprim != mot:
                        data = [1 if mot in phraseliste[phraseliste.index(motprim):] else 0, 1 if mot in phraseliste[
                            :phraseliste.index(motprim)] else 0, 0, 0]
                        try:
                            if mot == phraseliste[phraseliste.index(motprim) + 1]:
                                data[2] = 1
                            else:
                                data[2] = 0
                        except IndexError:
                            data[2] = 0

                        try:
                            if mot == phraseliste[phraseliste.index(motprim) - 1]:
                                data[3] = 1
                            else:
                                data[3] = 0
                        except IndexError:
                            data[3] = 0

                        if not datas.get(mot):
                            datas[mot] = dict()
                        if not datas[mot].get(motprim):
                            datas[mot][motprim] = data
                        else:
                            if not datas[mot].get(motprim):
                                datas[mot][motprim] = list()
                            for i in range(3):
                                datas[mot][motprim][i] += data[i]

                        data = [1 if mot == phraseliste[0]else 0,
                                1 if mot == phraseliste[-1]else 0]
                        if not datas[mot].get("az"):
                            datas[mot]["az"] = data
                        else:
                            datas[mot]["az"][0] += data[0]
                            datas[mot]["az"][1] += data[1]
                        datas[mot].pop("", None)
        datas.pop('', None)
        self.datas = datas
        return(datas)

    def generate(self, longueure, memoir=3):
        text, motstart = list(), list()
        for mot in self.datas:
            if self.datas[mot]["az"][0] >= 1:
                motstart.append(mot)
        text.append(random.choice(motstart))

        cursor = 0
        while cursor != longueure:
            if self.datas.get(text[-1]):
                if cursor != longueure - 1:
                    def find_word(memoir):
                        new_words = []

                        def with_markov():
                            i = self.m.generate(1, start=text[-1].lower())
                            new_words.append(i[-1])
                        prev_words = text[-1 - memoir:-1]
                        if len(text) == 1:
                            with_markov()
                        else:
                            liste_words = self.datas.keys()
                            for w in liste_words:
                                verif = 0
                                for prev_word in prev_words:
                                    if self.datas[text[-1]].get(w):
                                        if self.datas[text[-1]].get(w)[1] >= 1:
                                            verif += 1
                                if verif == memoir:
                                    new_words.append(w)
                                else:
                                    with_markov()
                        if new_words:
                            return new_words
                        else:
                            return False

                    if memoir >= len(text):
                        new_words = find_word(len(text) - 1)
                    else:
                        new_words = find_word(memoir)
                    if new_words:
                        text.append(random.choice(new_words))
                    else:
                        break
            else:
                break
            cursor += 1
        return text


class groupOfWords():
    def __init__(self, text):
        self.text = text

    def analyse(self, keywords_groups=3):
        groups = []
        words = serializer(self.text).mots()
        words = [word.lower() for word in words]
        for word in words:
            if keywords_groups >= words.index(word):
                groups.append(tuple(words[:words.index(word)]))
            else:
                groups.append(
                    tuple(words[words.index(word) - keywords_groups:words.index(word)]))
        self.groups = groups
        return groups

    def generate(self, keywords):
        output = dict()
        for keyword in keywords:
            for group in self.groups:
                if keyword in group:
                    if output.get(keyword):
                        output[keyword].append(group)
                    else:
                        output[keyword] = [group]

        start = dict()
        for keyword in output:
            for group in output[keyword]:
                if not output[keyword].index(group) % 2:
                    if start.get(keyword):
                        start[keyword].append(group[0])
                    else:
                        start[keyword] = [group[0]]

        print(output)
        print(start)
