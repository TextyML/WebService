from nltk.tokenize import sent_tokenize, word_tokenize

class Preprocessor():
    
    def __init__(self, stemmer=None, lemmatizer=None, stopwords=None):
        self.stemmer = stemmer
        self.lemmatizer = lemmatizer
        self.stopwords = stopwords
    
    def _tokenize(self, string):
        return word_tokenize(string)
    
    def _filter_for_words(self, tokens):
        return [w for w in tokens if w.isalpha()]
    
    def _lowercase_words(self, tokens):
        return [w.lower() for w in tokens]
    
    def _remove_stopwords(self, tokens):
        return [w for w in tokens if w not in self.stopwords]
    
    def _stem(self, tokens):
        return [self.stemmer.stem(t) for t in tokens]

    def _lemmatize(self, tokens):
        return [self.lemmatizer.lemmatize(t) for t in tokens]
    
    def _process(self, string):
        tokens = self._tokenize(string)
        tokens = self._filter_for_words(tokens)
        tokens = self._lowercase_words(tokens)
        if self.stopwords is not None:
            tokens = self._remove_stopwords(tokens)
        if self.stemmer is not None:
            tokens = self._stem(tokens)
        elif self.lemmatizer is not None:
            tokens = self._lemmatize(tokens)
        return tokens
    
    def get_preprocessed_text(self, string):
        return ' '.join(self._process(string))
    
    def get_preprocessed_tokens(self, string):
        return self._process(string)