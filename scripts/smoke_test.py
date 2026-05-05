#!/usr/bin/env python
from pupwiki_geo.text import slugify
from pupwiki_geo.categories import match_category

assert slugify('Los Angeles, CA') == 'los-angeles-ca'
cat, conf, meta = match_category({'amenity': 'veterinary', 'name': 'Happy Vet'})
assert cat == 'veterinary-clinics'
print('Smoke test OK')
