import collections
from itertools import chain

pronunciations = None
lookup = None
rhyme_lookup = None


def parse_cmu(cmufh):
    pronunciations = list()
    for line in cmufh:
        line = line.strip()
        if line.startswith(";"):
            continue
        word, phones = line.split(" ", 1)
        pronunciations.append((word.split("(", 1)[0].lower(), phones))
    return pronunciations


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
    with open("pronunc_subset7.txt", "r") as file:
        init_cmu(file.readlines())

    return lookup.get(find.lower(), [])


def rhymes(word):
    phones = phones_for_word(word)
    combined_rhymes = []
    if phones:
        for element in phones:
            combined_rhymes.append(
                [w for w in rhyme_lookup.get(rhyming_part(element), []) if w != word]
            )
        combined_rhymes = list(chain.from_iterable(combined_rhymes))
        unique_combined_rhymes = sorted(set(combined_rhymes))
        return unique_combined_rhymes
    else:
        return []


print(rhymes("survivor"))
# with open("pronunc_subset6.txt", "r") as file:
#     init_cmu(file.readlines())
