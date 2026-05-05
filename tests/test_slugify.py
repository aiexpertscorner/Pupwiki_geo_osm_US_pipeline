from pupwiki_geo.text import slugify


def test_slugify():
    assert slugify("Los Angeles, CA") == "los-angeles-ca"
    assert slugify("PupWiki & Dogs") == "pupwiki-and-dogs"
