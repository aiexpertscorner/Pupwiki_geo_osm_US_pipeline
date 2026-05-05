# Overpass Query Templates

Use these manually or in controlled scripts. Do not run them from the browser.

## BBox combined dog-service query

Replace `{{bbox}}` with:

```txt
south,west,north,east
```

Example:

```txt
34.00,-118.55,34.35,-118.15
```

```overpass
[out:json][timeout:120];
(
  node["amenity"="veterinary"]({{bbox}});
  way["amenity"="veterinary"]({{bbox}});
  relation["amenity"="veterinary"]({{bbox}});

  node["leisure"="dog_park"]({{bbox}});
  way["leisure"="dog_park"]({{bbox}});
  relation["leisure"="dog_park"]({{bbox}});

  node["shop"="pet"]({{bbox}});
  way["shop"="pet"]({{bbox}});
  relation["shop"="pet"]({{bbox}});

  node["shop"="pet_grooming"]({{bbox}});
  way["shop"="pet_grooming"]({{bbox}});
  relation["shop"="pet_grooming"]({{bbox}});

  node["amenity"="animal_boarding"]({{bbox}});
  way["amenity"="animal_boarding"]({{bbox}});
  relation["amenity"="animal_boarding"]({{bbox}});

  node["amenity"="animal_shelter"]({{bbox}});
  way["amenity"="animal_shelter"]({{bbox}});
  relation["amenity"="animal_shelter"]({{bbox}});

  node["amenity"="animal_training"]({{bbox}});
  way["amenity"="animal_training"]({{bbox}});
  relation["amenity"="animal_training"]({{bbox}});

  node["amenity"="dog_toilet"]({{bbox}});
  way["amenity"="dog_toilet"]({{bbox}});
  relation["amenity"="dog_toilet"]({{bbox}});
);
out center tags;
```

## Dog-friendly restaurants/cafes

```overpass
[out:json][timeout:120];
(
  node["amenity"~"^(restaurant|cafe|bar|pub)$"]["dog"~"^(yes|outside|leashed)$"]({{bbox}});
  way["amenity"~"^(restaurant|cafe|bar|pub)$"]["dog"~"^(yes|outside|leashed)$"]({{bbox}});
  relation["amenity"~"^(restaurant|cafe|bar|pub)$"]["dog"~"^(yes|outside|leashed)$"]({{bbox}});
);
out center tags;
```
