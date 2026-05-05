# 04 — MapLibre GL JS Components

Build the MapLibre GL JS UI for PupWiki Dog Services.

Goal:
Create a responsive, mobile-first interactive map page that uses generated GeoJSON datasets.

Install dependency if missing:

```bash
npm install maplibre-gl
```

Use client-only loading:

- In Astro, use a React island/client directive or compatible approach.
- In React SPA, lazy-load MapLibre component where possible.
- Do not execute maplibregl on the server.

Preferred structure:

```txt
src/features/dog-services/components/
  DogServicesMap.tsx
  DogServicesPage.tsx
  DogServiceFiltersPanel.tsx
  DogServiceList.tsx
  DogServiceCard.tsx
  DogServiceLegend.tsx
  DogServiceAttribution.tsx
  DogServiceEmptyState.tsx

src/features/dog-services/hooks/
  useDogServiceData.ts
  useDogServiceFilters.ts

src/features/dog-services/lib/
  mapLibreConfig.ts
  dogServiceMapLayers.ts
```

## Requirements

### 1. Data loading

Load:

```txt
/data/dog-services/us/all.geojson
```

Fallback:

```txt
/data/dog-services/us/sample.geojson
```

### 2. MapLibre

Create a MapLibre map with:

- GeoJSON source
- clustering enabled for points
- category-based styling
- unclustered point layer
- cluster layer
- cluster count layer
- popup or side panel on marker click
- fit bounds to loaded data
- graceful empty state

### 3. Filters

Support:

- category filter
- tier filter
- search query
- city/state text filter if available
- high confidence only
- has website
- emergency only

### 4. UI

- Mobile-first
- Map at top on mobile
- List below map on mobile
- Split map/list layout on desktop
- Use existing PupWiki design tokens/components
- Do not create a generic-looking map page
- Match PupWiki editorial/authoritative style

### 5. Accessibility

- Buttons have accessible labels
- Filter controls use labels
- Cards are keyboard-friendly
- Map has descriptive aria-label
- Popup content readable

### 6. Attribution

Add visible attribution:

```txt
© OpenStreetMap contributors. Data available under ODbL.
```

Also include a small notice:

```txt
Listings may be incomplete. Verify hours, services and dog access rules before visiting.
```

### 7. Performance

- Avoid rendering thousands of DOM markers.
- Use MapLibre layers instead of individual HTML markers for the main point layer.
- Use memoization for filtered features.
- Keep list capped or paginated if many records.

### 8. Styling

Use existing CSS variables/tokens. If needed, add scoped CSS module or feature CSS:

- dog-service-map
- dog-service-panel
- dog-service-card
- dog-service-filter-chip

Run build/typecheck.
Fix only scoped issues.
