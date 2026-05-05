# Google Drive OSM source

Configured file:

```txt
https://drive.google.com/file/d/1z3fynwYHrnx-9HzvsXrS1izorU8dD5AY/view?usp=drivesdk
```

File ID:

```txt
1z3fynwYHrnx-9HzvsXrS1izorU8dD5AY
```

Target path:

```txt
data-raw/osm/google-drive/us-latest.osm.pbf
```

## Recommended ways to get the 12GB file locally

### Option A — Google Drive Desktop

Sync/download the file and copy it to the target path.

### Option B — gdown

```bash
pip install gdown
python -m pupwiki_geo.cli drive-osm --file-id 1z3fynwYHrnx-9HzvsXrS1izorU8dD5AY
```

### Option C — rclone

Best for private/large Drive files:

```bash
rclone copy "gdrive:path/to/us-latest.osm.pbf" data-raw/osm/google-drive/ --progress
```

If Drive rate-limits or warns about virus scan size, manual Drive Desktop or rclone is usually more reliable than plain HTTP.
