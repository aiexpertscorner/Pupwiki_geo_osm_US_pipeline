PY ?= python
PBF ?= data-raw/osm/google-drive/us-latest.osm.pbf
VERSION ?= v1
BUILD ?= data-build/places/$(VERSION)

.PHONY: init download-p1 drive-osm extract build qa compress clean

init:
	$(PY) -m pupwiki_geo.cli init

download-p1:
	$(PY) -m pupwiki_geo.cli download --priority P1 --verify-remote

drive-osm:
	$(PY) -m pupwiki_geo.cli drive-osm --file-id 1z3fynwYHrnx-9HzvsXrS1izorU8dD5AY --out $(PBF)

extract:
	$(PY) -m pupwiki_geo.cli extract-osm --pbf $(PBF) --out data-work/osm/us-dog-pois.ndjson

build:
	$(PY) -m pupwiki_geo.cli build --input data-work/osm/us-dog-pois.ndjson --states data-work/boundaries/us-states.geojson --places data-work/boundaries/us-places.geojson --counties data-work/boundaries/us-counties.geojson --out $(BUILD)

qa:
	$(PY) -m pupwiki_geo.cli qa --build $(BUILD)

compress:
	$(PY) -m pupwiki_geo.cli compress --build $(BUILD)

clean:
	rm -rf data-work data-build tmp logs
