# 05 — Route/Page Integration

Integrate the Dog Services Map into PupWiki routing/navigation.

## Tasks

1. Detect routing model:
   - Astro file routing
   - React SPA App.tsx routing
   - hybrid

2. Add main route:

```txt
/dog-services/
```

Astro preferred:

- `src/pages/dog-services/index.astro`
- import layout/header/footer conventions from existing site
- render DogServicesPage as client component if needed

React SPA fallback:

- Add a route/state/view for dog-services
- Ensure header/nav can link to it
- Preserve existing homepage/breed pages

3. Navigation:

Add link in a sensible place:

- primary nav if not too crowded, or
- resources/tools section, or
- footer

Label:

```txt
Dog Services Map
```

or shorter:

```txt
Dog Services
```

4. SEO metadata:

Title:

```txt
Dog Services Map | Find Vets, Dog Parks, Groomers & Pet Stores | PupWiki
```

Description:

```txt
Explore dog-related services including veterinary clinics, emergency vets, dog parks, groomers, pet stores, boarding, shelters and dog-friendly places. Data is based on generated location datasets and OpenStreetMap inputs.
```

5. Content blocks:

Add intro section:

- H1
- short explanation
- trust/disclaimer box
- category overview cards
- map section
- service list section
- methodology/attribution section

6. Do not create thin SEO pages yet unless routing is already ready.
7. Ensure no broken links.
8. Run build/typecheck.
