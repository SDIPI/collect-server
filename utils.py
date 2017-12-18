import re
import lxml.html
from lxml.html.clean import Cleaner
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
import string


def clean_punctuation(text: string):
    return text.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))


def clean_html(html_string: string, stopwords, lemmatize: bool):
    # Parse the HTML
    html_content = lxml.html.fromstring(html_string)

    # Remove HTML tags to only keep text
    cleaner = Cleaner()
    cleaner.javascript = True
    cleaner.style = True
    text = cleaner.clean_html(html_content).text_content()

    # Clean lowered text from punctuation and remove stopwords
    no_punc = clean_punctuation(text.lower())
    words = nltk.word_tokenize(no_punc)

    pattern = re.compile(r'[^\W\d_]+', re.U)

    final_words = []
    if lemmatize:
        lemmatiser = WordNetLemmatizer()
        wordnet_tag = {'NN': 'n', 'JJ': 'a', 'VB': 'v', 'RB': 'r'}
        tagged = nltk.pos_tag(words)
        for token in tagged:
            word = token[0]
            if len(word) >= 2 and pattern.match(word) is not None and word not in stopwords:
                try:
                    lemma = lemmatiser.lemmatize(word, wordnet_tag[token[1][:2]])
                except:
                    lemma = lemmatiser.lemmatize(word)
                final_words.append(lemma)

    else:
        for word in words:
            if len(word) >= 2 and pattern.match(word) is not None and word not in stopwords:
                final_words.append(word)

    return ' '.join(final_words)
