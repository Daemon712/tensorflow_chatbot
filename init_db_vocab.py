import re

import data_utils
from app import db
from app.models import VocabularyWord
from tensorflow.python.platform import gfile


def init_database_vocabulary():
    max_vocabulary_size = 60000
    data_path = 'data/data.a'
    vocab = {}
    words = 0
    with gfile.GFile(data_path, mode="rb") as f:
        counter = 0
        for line in f:
            counter += 1
            if counter % 100000 == 0:
                print("  processing line %d" % counter)
            tokens = data_utils.basic_tokenizer(line)
            for w in tokens:
                word = re.sub(data_utils._DIGIT_RE, b"0", w)
                words += 1
                if word in vocab:
                    vocab[word] += 1
                else:
                    vocab[word] = 1
        vocab_list = sorted(vocab, key=vocab.get, reverse=True)
        print('>> Full Vocabulary Size :', len(vocab_list))
        if len(vocab_list) > max_vocabulary_size:
            vocab_list = vocab_list[:max_vocabulary_size]

        db.session.add_all(VocabularyWord(word=w, frequency=1_000_000 * vocab[w] / words) for w in vocab_list)
        db.session.commit()