# 01 — Repo Audit + Integration Plan

Audit the PupWiki repository for the Dog Services Map feature.

Tasks:
1. Identify the app framework and routing model:
   - Astro pages?
   - React SPA?
   - Vite?
   - Existing App.tsx navigation?
   - Existing layout/header/footer components?

2. Search for existing datasets:
   - /data
   - /src/data
   - /public/data
   - /src/content
   - any .json, .geojson, .ts data files
   - US states, cities, locations, geo boundaries, breed/location datasets, service datasets

3. Search for design system files:
   - tokens CSS
   - Tailwind config
   - shared UI components
   - Card/Button/Badge components
   - layout components

4. Search package.json for:
   - map libraries
   - React
   - Astro
   - TypeScript
   - scripts for build/typecheck/lint

5. Produce an implementation plan with:
   - exact files to add
   - exact files to modify
   - safest route integration approach
   - dataset sources discovered
   - risk list
   - build command to run

Do not implement yet except if you need to inspect files. End with a concise plan.
