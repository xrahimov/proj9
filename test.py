from collections import defaultdict

pronunciations = None
lookup = None
rhyme_lookup = None
pronunciations_dict = defaultdict()

with open("PronunciationDictionary.txt", "r") as file:
    lines = file.readlines()
    for line in lines:
        syllabelles = line.split()
        pronunciations_dict[syllabelles[0]] = syllabelles[1:]


def rhymes(word):
    word_phonemas = pronunciations_dict[word.upper()]
    w_phonemas = []
    rhyming = []
    for phonema in word_phonemas:
        if '1' in phonema:
            w_phonemas.append(phonema)
        elif '0' in phonema:
            w_phonemas.append(phonema)
        elif '2' in phonema:
            w_phonemas.append(phonema)




    for key in pronunciations_dict:
        c_phonemes = pronunciations_dict[key]
        for phonema in c_phonemes:
            if phonema in w_phonemas:
                if word_phonemas[word_phonemas.index(phonema)-1] != c_phonemes[c_phonemes.index(phonema)-1]:
                    for i in w_phonemas:
                        boolean_case = False
                        if '1' in i:
                            boolean_case = True
                            if not (boolean_case != True or '1' in word_phonemas[0]):
                                rhyming.append(key)

    print(rhyming)


rhymes('yeah')
'''
    "SKYLIGHT":  [['S', 'K', 'AY1', 'L', 'AY2', 'T'], ['HH', 'AY1', 'L', 'AY2', 'T']]
}

'''
# SKYLIGHT  S K AY1 L AY2 T
# HIGHLIGHT  HH AY1 L AY2 T