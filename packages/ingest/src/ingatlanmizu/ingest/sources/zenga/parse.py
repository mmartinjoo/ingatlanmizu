from bs4 import BeautifulSoup
from ingatlanmizu.ingest.sources.base import SourceSpecificListingDict, ListingContent

def parse(listing_content: ListingContent) -> SourceSpecificListingDict:
    """
    zenga.hu hirdetés HTML-ből dict-et készít.
    """
    soup = BeautifulSoup(listing_content.html, "lxml")

    data = {
        "megnevezes": _text(_by_cy(soup, "advert-details-title")),
        "ar": _text(_by_cy(soup, "advert-details-price")),
        "negyzetmeter_ar": _text(_by_cy(soup, "advert-details-price-per-square-meter")),
        "cim": _text(_by_cy(soup, "advert-details-map-btn")),
        "alapterulet": None,
        "telek": None,
        "emelet": None,
        "szobak_szama": None,
        "leiras": _text(_by_cy(soup, "advert-details-description")),
        "hirdeteskod": _after_label(
            _by_cy(soup, "advert-details-advert-code"), "Hirdetéskód"
        ),
        "referenciaszam": _after_label(
            _by_cy(soup, "advert-details-office-code"), "Referenciaszám"
        ),
        "frissitve": _text(_by_cy(soup, "advert-details-last-updated")),
        "allapot": None,
        "futes": None,
        "epites_eve": None,
        "terasz": None,
        "energetikai_besorolas": None,
        "hirdeto_neve": _text(_by_cy(soup, "advertiser-contact-name")),
        "ingatlan_iroda_neve": _text(_by_cy(soup, "advertiser-contact-agency")),
        "tipus": None,
        "szintek_szama": None,
    }

    data.update(_highlight_params(soup))

    params = _property_params(soup)
    for label, key in PARAM_LABELS.items():
        if label in params:
            data[key] = params[label]

    return data

PARAM_LABELS = {
    "Állapot": "allapot",
    "Fűtés": "futes",
    "Építés éve": "epites_eve",
    "Terasz": "terasz",
    "Energetikai besorolás": "energetikai_besorolas",
    "Típus": "tipus",
    "Szintek száma": "szintek_szama",
}

HIGHLIGHT_LABELS = {
    "Alapterület": "alapterulet",
    "Telek": "telek",
    "Emelet": "emelet",
    "Szobák száma": "szobak_szama",
}

def _text(node):
    """Csomópont szövege, csak a széli whitespace levágva. None, ha nincs csomópont."""
    if node is None:
        return None
    return node.get_text().strip() or None


def _by_cy(soup, value):
    """Első elem a megadott data-cy attribútummal."""
    return soup.find(attrs={"data-cy": value})


def _after_label(node, label):
    """
    'Hirdetéskód: 8689235' típusú blokkból a címke utáni rész.
    A címkét és a kettőspontot vágja le, mást nem.
    """
    text = _text(node)
    if text is None:
        return None
    if text.startswith(label):
        text = text[len(label):]
    return text.lstrip(": ").strip() or None


def _highlight_params(soup):
    """
    A galéria alatti három kiemelt paraméter (alapterület / telek vagy emelet /
    szobák száma). A pozíció ingatlantípusonként változik, ezért a címke
    alapján párosítunk, nem sorrend szerint.
    """
    found = {}
    for slot in ("first", "second", "third"):
        value = _text(_by_cy(soup, f"advert-details-{slot}-param"))
        label = _text(_by_cy(soup, f"advert-details-{slot}-param-title"))
        if label is None:
            continue
        key = HIGHLIGHT_LABELS.get(label)
        if key is not None and key not in found:
            found[key] = value
    return found


def _property_params(soup):
    """
    A "Tulajdonságok" doboz címke -> érték párjai.
    Ahol nincs valódi érték (pl. energetikai besorolásnál egy
    "Megkérdezem" gomb áll), ott None kerül vissza.
    """
    params = {}
    for row in soup.find_all(attrs={"data-cy": "advert-details-param-list-item"}):
        cells = row.find_all("div", recursive=False)
        if len(cells) < 2:
            continue
        label = _text(cells[0])
        if label is None:
            continue
        label = label.rstrip(":").strip()
        if cells[1].find("button") is not None:
            params[label] = None
        else:
            params[label] = _text(cells[1])
    return params
