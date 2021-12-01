
def get_clean_deckstring(deckstring: str) -> str:
    """ Выделяет код колоды из формата, в котором колода копируется из Hearthstone """

    deckstring = deckstring.strip()

    if not deckstring.startswith('###'):
        return deckstring

    return deckstring.split('#')[-3].strip()

