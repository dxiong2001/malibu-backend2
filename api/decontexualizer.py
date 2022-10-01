def decontexualizer1(sentence):
    conjunctive_adverbs = ["accordingly", "also", "anyway", "besides", "certainly", "consequently", "finally", "furthermore", "hence", "however", "in addition", "in fact", "incidentally", "indeed", "instead", "lately", "likewise", "meanwhile", "moreover", "nevertheless", "next", "nonetheless", "now", "otherwise", "rather", "similarly", "since", "still", "subsequently", "then", "thereby", "therefore", "thus", "ultimately", "but ultimately"]
    conj_with_comma = conjunctive_adverbs
    conj2 = ["and", "but"]
    sentence = sentence.strip()
    for c in range(len(conj_with_comma)):
        conj_with_comma[c] = conj_with_comma[c]+","
    conj_processed = conj_with_comma
    # print(conj_with_comma)

    begin_conj_adverb = sentence.lower().startswith(tuple(conj_processed))
    begin_conj2 = sentence.lower().startswith(tuple(conj2))
    # print(begin_conj_adverb)


    parts = sentence

    if(begin_conj_adverb):
        parts = ",".join(sentence.split(',')[1:]).strip()
        parts = parts[0].upper()+parts[1:]
      # print(parts)
    if(begin_conj2):
        parts = " ".join(sentence.split(" ")[1:]).strip()
        parts = parts[0].upper()+parts[1:]
    return parts