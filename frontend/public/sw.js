const CACHE_NAME = "disaster-cache-v2";
const STATIC_ASSETS = [
  "/",
  "/index.html",
  "/manifest.json",
  "/favicon.svg",
  "/icons.svg",
  "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",
  "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png"
];

// Fallback emergency datasets when completely offline with empty cache
const EMERGENCY_FALLBACK_DATA = {
  shelters: [
    {
      id: "sh-101",
      name: "St. Joseph Higher Secondary School Shelter (Offline Cache)",
      address: "Meppadi Town, Wayanad, Kerala - 673577",
      capacity: 650,
      current_occupancy: 120,
      status: "active",
      contact_number: "+91-9447100101",
      accessibility_rating: 0.9,
      structural_safety_rating: 0.95,
      latitude: 11.5450,
      longitude: 76.1210
    },
    {
      id: "sh-102",
      name: "Meppadi Community Hall & Relief Camp (Offline Cache)",
      address: "Near Main Bus Stand, Meppadi, Wayanad, Kerala - 673577",
      capacity: 500,
      current_occupancy: 85,
      status: "active",
      contact_number: "+91-9447100102",
      accessibility_rating: 0.85,
      structural_safety_rating: 0.88,
      latitude: 11.5482,
      longitude: 76.1245
    },
    {
      id: "sh-103",
      name: "Government Primary Health Center Meppadi",
      address: "Hospital Road, Meppadi, Wayanad, Kerala - 673577",
      capacity: 250,
      current_occupancy: 40,
      status: "active",
      contact_number: "+91-9447100103",
      accessibility_rating: 0.95,
      structural_safety_rating: 0.92,
      latitude: 11.5510,
      longitude: 76.1260
    }
  ],
  hazardZones: [
    {
      id: "hz-101",
      name: "Chooralmala Red Zone Alpha",
      hazard_type: "landslide",
      risk_level: "CRITICAL",
      risk_score: 0.92,
      latitude: 11.5300,
      longitude: 76.1300
    },
    {
      id: "hz-102",
      name: "Mundakkai High Risk Slope",
      hazard_type: "landslide",
      risk_level: "HIGH",
      risk_score: 0.78,
      latitude: 11.5350,
      longitude: 76.1350
    }
  ],
  alerts: [
    {
      id: "al-101",
      title: "OFFLINE CRITICAL RED ALERT — Wayanad Sector 1",
      message: "Extreme landslide and mudflow risk. Relocate immediately to St. Joseph Shelter.",
      severity: "CRITICAL",
      affected_area: "Chooralmala & Mundakkai",
      status: "ACTIVE",
      recommended_action: "Follow designated offline evacuation routes."
    }
  ]
};

// Install Event: Cache Static Assets
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log("[PWA Service Worker] Pre-caching emergency static assets & map dependencies");
      return cache.addAll(STATIC_ASSETS).catch((err) => {
        console.warn("[PWA Service Worker] Pre-cache non-fatal item error:", err);
      });
    })
  );
  self.skipWaiting();
});

// Activate Event: Clean up old caches
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            console.log("[PWA Service Worker] Removing outdated cache:", key);
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch Event: Cache First for assets, Network First with Cache/Fallback for API
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);

  // Bypass dev server modules, hot-reloading and node_modules
  if (
    url.pathname.includes("@vite") ||
    url.pathname.includes("@react-refresh") ||
    url.pathname.includes("/src/") ||
    url.pathname.includes("node_modules") ||
    url.search.includes("t=")
  ) {
    return;
  }

  // Handle SPA navigation requests
  if (event.request.mode === "navigate") {
    event.respondWith(
      fetch(event.request).catch(async () => {
        const cachedIndex = await caches.match("/index.html");
        return cachedIndex || caches.match("/");
      })
    );
    return;
  }

  // API Requests: Network First, Fallback to Cache or Pre-Seeded Offline JSON
  if (url.pathname.startsWith("/api/v1/")) {
    event.respondWith(
      fetch(event.request)
        .then((networkResponse) => {
          if (networkResponse.ok) {
            const clonedResponse = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, clonedResponse);
            });
          }
          return networkResponse;
        })
        .catch(async () => {
          console.warn("[PWA Service Worker] Offline fallback for API endpoint:", url.pathname);
          const cachedResponse = await caches.match(event.request);
          if (cachedResponse) {
            return cachedResponse;
          }

          // Fallbacks for standard emergency queries
          let payload = null;
          if (url.pathname.includes("/shelters")) {
            payload = EMERGENCY_FALLBACK_DATA.shelters;
          } else if (url.pathname.includes("/hazard-zones")) {
            payload = EMERGENCY_FALLBACK_DATA.hazardZones;
          } else if (url.pathname.includes("/alerts")) {
            payload = EMERGENCY_FALLBACK_DATA.alerts;
          } else {
            payload = {
              detail: "Offline mode active. Emergency local data served.",
              offline: true,
              stale: true,
            };
          }

          return new Response(JSON.stringify(payload), {
            status: 200,
            headers: {
              "Content-Type": "application/json",
              "X-Offline-Cached": "true",
            },
          });
        })
    );
    return;
  }

  // Static Assets, CDN scripts & Map Tiles: Cache First with Network Fallback
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }
      return fetch(event.request)
        .then((networkResponse) => {
          if (
            networkResponse.ok &&
            (event.request.url.includes("cartocdn") ||
              event.request.url.includes("openstreetmap") ||
              event.request.url.includes("leaflet") ||
              event.request.url.includes("/assets/"))
          ) {
            const responseToCache = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseToCache);
            });
          }
          return networkResponse;
        })
        .catch(() => {
          // Provide placeholder for images if offline
          if (event.request.destination === "image") {
            return caches.match("https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png");
          }
          return new Response("Offline Resource Unavailable", { status: 503 });
        });
    })
  );
});

