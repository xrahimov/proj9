import collections
from itertools import chain
import re

pronunciations = None
lookup = None
rhyme_lookup = None


def consonant_clusters():
    """Return a list of possible English consonant clusters."""
    """
    See the following resources for more information on consonant clusters.
    "consonant cluster: "a group of consonants which have no intervening vowel"
        https://en.wikipedia.org/wiki/Consonant_cluster
    "Two Theories of Onset Clusters", Duanmu
        http://www-personal.umich.edu/~duanmu/CR02.pdf
    "Phoneme distribution and syllable structure of entry words in the CMU
    English Pronouncing Dictionary", Yang
        http://fonetiks.info/bgyang/db/201606cmu.pdf
    "Blends, Digraphs, Trigraphs, and Other Letter Combinations"
        https://www.enchantedlearning.com/consonantblends/
    """
    return [
        "F W",
        "F R",
        "F L",
        "S W",
        "S V",
        "S R",
        "S L",
        "S N",
        "S M",
        "S F",
        "S P",
        "S T",
        "S K",
        "SH W",
        "SH R",
        "SH L",
        "SH N",
        "SH M",
        "TH W",
        "TH R",
        "V W",
        "V R",
        "V L",
        "Z W",
        "Z L",
        "B W",
        "B R",
        "B L",
        "D W",
        "D R",
        "G W",
        "G R",
        "G L",
        "P W",
        "P R",
        "P L",
        "T W",
        "T R",
        "K W",
        "K R",
        "K L",
        "L Y",
        "N Y",
        "M Y",
        "V Y",
        "H Y",
        "F Y",
        "S Y",
        "TH Y",
        "Z Y",
        "B Y",
        "D Y",
        "G Y",
        "P Y",
        "T Y",
        "K Y",
        "S P L",
        "S P R",
        "S T R",
        "S K R",
        "S K W",
    ]


def check_if_stressed_vowel(phone):
    """Returns True if CMUdict phoneme is a stressed vowel."""
    # 1 or 2 indicate vowel is stressed
    return phone[-1] in "12"


def check_if_consonant_cluster(phones):
    """Return True if CMUdict phonemes is a consonant cluster."""
    return phones in consonant_clusters()


def check_if_consonant(phone):
    """Returns True if CMUdict phoneme is a consonant."""
    # consonants do not have any stress number
    return phone[-1] not in "012"


def parse_cmu(cmufh):
    pronunciations = list()
    for line in cmufh:
        line = line.strip()
        if line.startswith(";"):
            continue
        word, phones = line.split(" ", 1)
        pronunciations.append((word.split("(", 1)[0].lower(), phones))
    return pronunciations


def search(pattern):
    """Get words whose pronunciation matches a regular expression.
    This function Searches the CMU dictionary for pronunciations matching a
    given regular expression. (Word boundary anchors are automatically added
    before and after the pattern.)
    .. doctest::
        >>> import pronouncing
        >>> 'interpolate' in pronouncing.search('ER1 P AH0')
        True
    :param pattern: a string containing a regular expression
    :returns: a list of matching words
    """
    init_cmu()
    regexp = re.compile(r"\b" + pattern + r"\b")
    return [word for word, phones in pronunciations if regexp.search(phones)]


def init_cmu(filehandle=None):
    global pronunciations, lookup, rhyme_lookup
    if pronunciations is None:
        pronunciations = parse_cmu(filehandle)
        lookup = collections.defaultdict(list)
        for word, phones in pronunciations:
            lookup[word].append(phones)
        rhyme_lookup = collections.defaultdict(list)
        for word, phones in pronunciations:
            rp = rhyming_part(phones)
            if rp is not None:
                rhyme_lookup[rp].append(word)


def rhyming_part(phones):
    phones_list = phones.split()
    for i in range(len(phones_list) - 1, 0, -1):
        if phones_list[i][-1] in "12":
            return " ".join(phones_list[i:])
    return phones


def phones_for_word(find):
    with open("PronunciationDictionary.txt", "r") as file:
        init_cmu(file.readlines())

    return lookup.get(find.lower(), [])


def rhyme(word):
    phones = phones_for_word(word)
    combined_rhymes = []
    if phones:
        for element in phones:
            combined_rhymes.append(
                [w for w in rhyme_lookup.get(rhyming_part(element), []) if w != word]
            )
        # combined_rhymes = list(chain.from_iterable(combined_rhymes))
        # unique_combined_rhymes = sorted(set(combined_rhymes))
        # return unique_combined_rhymes
        return combined_rhymes
    else:
        return []


def first_phones_for_word(word):
    """Chooses first set of CMUdict phonemes for word

    :param word: a word
    :return: CMUdict phonemes string
    """
    all_phones = phones_for_word(word)
    if not all_phones:
        return ""
    phones = all_phones[0]
    return phones


def perfect_rhyme(word, phones=None):
    """Returns a list of perfect rhymes for a word.

    The conditions for a perfect rhyme between words are:
    (1) last stressed vowel and subsequent phonemes match
    (2) onset of last stressed syllable is different
    If phones argument not given, phones/pronunciation used will default to the
    first in the list of phones returned for word. If no rhyme is found, an
    empty list is returned.


    :param word: a word
    :param phones: specific CMUdict phonemes string for word (default None)
    :return: a list of perfect rhymes for word
    """
    if phones is None:
        phones = first_phones_for_word(word)
        if phones == "":
            return []
    else:
        if phones not in phones_for_word(word):
            raise ValueError(phones + " not phones for +" + word)
    if not phones:
        raise ValueError("phonemes string is empty")
    perf_and_iden_rhymes = rhyme(word, phones)
    identical_rhymes = identical_rhyme(word, phones)
    perfect_rhymes = list(np.setdiff1d(perf_and_iden_rhymes, identical_rhymes))
    if word in perfect_rhymes:
        perfect_rhymes.remove(word)
    return perfect_rhymes


def identical_rhyme(word, phones=None):
    """Returns identical rhymes of word.

    The conditions for an identical rhyme between words are:
    (1) last stressed vowel and subsequent phonemes match
    (2) onset of last stressed syllable is the same
        e.g. 'leave' and 'leave', or 'leave' and 'believe'
    If phones argument not given, phones/pronunciation used will default to the
    first in the list of phones returned for word. If no rhyme is found, an
    empty list is returned.

    The identical part of the word doesn't have to be a 'real' word.
    e.g. The phonemes for 'vection' will be used to find identical rhymes
    of 'convection' (e.g. advection) even though 'vection' is unusual/obscure.


    :param word: a word
    :param phones: specific CMUdict phonemes string for word (default None)
    :return: a list of identical rhymes for word
    """
    if phones is None:
        phones = first_phones_for_word(word)
        if phones == "":
            return []
    else:
        if phones not in phones_for_word(word):
            raise ValueError(phones + " not phones for +" + word)
    if not phones:
        raise ValueError("phonemes string is empty")

    phones_list = phones.split()
    search_list = []
    for i in range(len(phones_list) - 1, -1, -1):
        phone = phones_list[i]
        if check_if_stressed_vowel(phone) is False:
            search_list.append(phone)
        else:
            search_list.append(phone)
            last_stressed_vowel_at_start = i == 0
            if last_stressed_vowel_at_start is True:
                search_list.reverse()
                search = " ".join(search_list)
                rhymes = search(search + "$")
                return rhymes
            else:
                consonant_cnt = 0
                consonants = ""
                search_start = ""
                for j in range(i, 0, -1):
                    next_phone = phones_list[j - 1]
                    if check_if_consonant(next_phone) is True:
                        consonant_cnt += 1
                        if consonant_cnt > 1:
                            consonants = next_phone + " " + consonants
                            if check_if_consonant_cluster(consonants):
                                search_list.append(next_phone)
                            else:
                                break
                        else:
                            consonants = next_phone
                            search_list.append(next_phone)
                    else:
                        if consonant_cnt == 0:  # null onset
                            # Regex: vowel (AA1, EH0, ect.) or start '^'
                            # pretty sure all vowel start two letters...
                            #   (would be "((.{1,2}(0|1|2) )|^)" otherwise)
                            search_start = "((..(0|1|2) )|^)"
                        break
                search_list.reverse()
                search = search_start + " ".join(search_list) + "$"
                rhymes = search(search)
                # for r in rhymes:
                #     print(pronouncing.phones_for_word(r)[0])
                return rhymes


print(rhyme("reader"))
print()
# with open("pronunc_subset6.txt", "r") as file:
#     init_cmu(file.readlines())
