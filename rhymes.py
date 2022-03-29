import collections
import re

pronunciations = None
lookup = None
rhyme_lookup = None


def search(pattern):
    regexp = re.compile(r"\b" + pattern + r"\b")
    return [word for word, phones in pronunciations if regexp.search(phones)]


def consonant_clusters():
    """Return a list of possible English consonant clusters."""
    """
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
    # 1 or 2 indicate vowel is stressed
    return phone[-1] in "12"


def check_if_consonant_cluster(phones):
    return phones in consonant_clusters()


def check_if_consonant(phone):
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


def init_cmu(f_name):
    global pronunciations, lookup, rhyme_lookup
    with open(f_name, "r") as file:
        filehandle = file.readlines()
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
    return lookup.get(find.lower(), [])


def chain(*iterables):
    for it in iterables:
        for each in it:
            yield each


def rhyme(word):
    phones = phones_for_word(word)
    combined_rhymes = []
    if phones:
        for element in phones:
            combined_rhymes.append(
                [w for w in rhyme_lookup.get(rhyming_part(element), []) if w != word]
            )

        rhymes = list(set([item for sublist in combined_rhymes for item in sublist]))
        return rhymes
    else:
        return []


def first_phones_for_word(word):
    all_phones = phones_for_word(word)
    if not all_phones:
        return ""
    phones = all_phones[0]
    return phones


def perfect_rhyme(word, phones=None):
    if phones is None:
        phones = first_phones_for_word(word)
        if phones == "":
            return []
    else:
        if phones not in phones_for_word(word):
            raise ValueError(phones + " not phones for +" + word)
    if not phones:
        raise ValueError("phonemes string is empty")
    rhymes = rhyme(word)
    identical_rhymes = identical_rhyme(word, phones)
    perfect_rhymes = list(set(rhymes).difference(set(identical_rhymes)))
    if word in perfect_rhymes:
        perfect_rhymes.remove(word)
    return sorted(perfect_rhymes)


def identical_rhyme(word, phones=None):
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
                searchs = " ".join(search_list)
                rhymes = search(searchs + "$")
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
                        if consonant_cnt == 0:
                            search_start = "((..(0|1|2) )|^)"
                        break
                search_list.reverse()
                searchs = search_start + " ".join(search_list) + "$"
                rhymes = search(searchs)

                return rhymes


def main():
    filename = input("Enter file name:\n")
    init_cmu(filename)
    word = ""
    while word != "#quit":
        word = input('\nEnter word to rhyme, or enter "#quit":\n').strip()
        if word == "#quit":
            break
        elif word == "":
            print("No word given.\n")
        elif len(word.split()) > 1:
            print("Multiple words entered, please enter only one word at a time.")
        else:
            print("Rhymes for: ", word.upper())
            rhyming_words = perfect_rhyme(word)
            if len(rhyming_words) == 0:
                print("  -- none found --")
            else:
                for el in rhyming_words:
                    print("  " + el.upper())


main()
