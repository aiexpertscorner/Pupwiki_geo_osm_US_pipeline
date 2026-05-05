# OSM Category Reference for PupWiki Dog Services

## Tier A — Core Services

| PupWiki category | OSM tags | Use |
|---|---|---|
| Veterinary clinics | `amenity=veterinary` | Vets, animal hospitals |
| Emergency vets | `amenity=veterinary` + `emergency=yes` | Emergency veterinary services |
| Dog parks | `leisure=dog_park` | Dog parks and off-leash areas |
| Pet stores | `shop=pet` | Pet supply stores |
| Dog grooming | `shop=pet_grooming` | Groomers and pet salons |
| Dog boarding | `amenity=animal_boarding` | Boarding, kennels, pet hotels |
| Animal shelters | `amenity=animal_shelter` | Shelters, rescue and adoption centers |
| Dog training | `amenity=animal_training` + `animal_training=dog` | Trainers, obedience, puppy classes |

## Tier B — Dog-Friendly POIs

| PupWiki category | OSM tags | Use |
|---|---|---|
| Dog-friendly parks | `leisure=park` + `dog=yes/leashed/designated` | Parks where dogs are allowed |
| Dog-friendly beaches | `natural=beach` + `dog=yes/leashed/designated` | Dog-friendly beaches |
| Pet-friendly hotels | `tourism=hotel/motel/guest_house` + `dog=yes` or `pets=yes` | Dog-friendly lodging |
| Dog-friendly restaurants | `amenity=restaurant/cafe/bar/pub` + `dog=yes/outside/leashed` | Dog-friendly patios/cafes/restaurants |

## Tier C — Micro Amenities

| PupWiki category | OSM tags | Use |
|---|---|---|
| Dog toilets | `amenity=dog_toilet` | Dog relief areas |
| Dog washing | `dog_washing=yes` | Self-service dog washing |
| Dog water points | `amenity=drinking_water` + `dog=yes/designated` | Water points useful for dogs |

## Important data-quality notes

Dog-friendly POIs are less reliable than hard service POIs.

Use display labels such as:

- "reported dog-friendly"
- "dog access may vary"
- "verify before visiting"

Avoid:

- "verified"
- "official"
- "guaranteed dog-friendly"
