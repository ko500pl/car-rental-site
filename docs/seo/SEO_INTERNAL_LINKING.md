# RentUp.ge — Internal Linking Graph

The central strategy. Every link below is derived from **data that already exists**, so the graph is generated, contextual, and truthful.

```
        PLACE  ────────────  ROUTE  ────────────  ITINERARY
   (attractions/257)      (routes/32)        (itineraries/N-days)
          │  ╲                │  ╲                  │
          │   ╲               │   ╲                 │
          │    ╲              │    ╲                │
          ▼     ▼             ▼     ▼               ▼
       REGION  CAR CATEGORY ◄─────────────────► TRIP PLANNER
                    │                                │
                    ▼                                ▼
                 VEHICLE  ───────────────────►  CAR RENTAL (hub → locations)
```

## Generated edges

| Edge | Source of truth | Rendered as |
|---|---|---|
| attraction → nearby attractions | `attraction.nearby[]` | "Nearby places" cards |
| attraction → routes containing it | reverse index of `route.waypoints[]` | "Part of these road trips" |
| attraction → region | `attraction.region` | breadcrumb + link |
| attraction → car category | `attraction.road` + `attraction.car_category` | "Best car for this drive" → `/car-rental/{category}/` |
| route → attractions | `route.waypoints[]` | stop cards (with photos) |
| route → car category | `route.car_category` | "Recommended vehicle" → `/car-rental/{category}/` |
| route → planner | route slug | "Open in Trip Planner" → `/map/#tour={slug}` |
| route → itinerary band | `route.days` | "Fits a {N}-day Georgia itinerary" |
| itinerary → routes | curated route list | day-by-day links |
| itinerary → car rental | dominant `car_category` of its routes | "Rent a car for this trip" |
| itinerary → planner | composed slugs | "Customize this itinerary" |
| category → vehicles | `car.category` | model cards with real rates |
| category → routes needing it | routes where `route.car_category == category` | "Routes that need this car" |
| location → routes starting nearby | `places.yml` coords vs route first waypoint | "Popular road trips from {place}" |
| location → car rental hub | static | breadcrumb up |
| planner → routes / attractions / car rental | static | crawlable link blocks |

## Reusable UI blocks (implement once, reuse everywhere)

| Block | Appears on | Anchor style |
|---|---|---|
| **Nearby places** | attraction | place name |
| **Part of these road trips** | attraction | route name |
| **Stops on this route** | route, itinerary | place name |
| **Best car for this trip** | route, itinerary, rough-road attraction | "SUV rental in Georgia" / "4×4 rental in Georgia" |
| **Popular road trips from {city}** | location pages | "Tbilisi to Kazbegi road trip" |
| **Open in Trip Planner** | route, itinerary, attraction | descriptive, not "click here" |
| **Continue your road trip** | route | next logical route |
| **Rent a car for this trip** | itinerary, route | category-specific |

## Rules

1. **Contextual, in-content links only.** No sitewide keyword footer blocks.
2. **Descriptive anchors.** Never "click here", "read more", "this page".
3. **Cap per block**: max 6 nearby places, max 4 routes per attraction, max 8 stops preview — avoid link farms on 257 pages.
4. **Bidirectional where truthful**: if a route lists a stop, the stop lists the route.
5. **Language-local links only.** A `/ka/` page links to `/ka/` targets; cross-language linking is handled exclusively by `hreflang`.
6. **No link to a noindex page from indexable content** except intentional product CTAs (`/trip/` after planning, `/account/`).
7. **Rough-road rule**: an attraction with `road: 4x4_only` or `gravel` links to `/car-rental/4x4/`; `paved` links to `/car-rental/economy/`. Never claim a road is passable/impassable beyond what `attraction.road` states.
