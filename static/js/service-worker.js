// Service Worker for Kings Park, Kwamhlanga Community Police Forum
const CACHE_NAME = 'kingspark-cpf-v1';

// Assets to cache on install
const PRECACHE_ASSETS = [
  '/',
  '/static/css/style.css',
  '/static/css/optimize.css',
  '/static/js/main.js',
  '/static/js/performance.js',
  '/static/images/kingsapark_logo_official.png',
  '/static/manifest.json',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js'
];

// On install, cache precache assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(PRECACHE_ASSETS))
      .then(() => self.skipWaiting())
  );
});

// Clean up old caches on activate
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.filter(cacheName => {
          return cacheName.startsWith('kingspark-cpf-') && cacheName !== CACHE_NAME;
        }).map(cacheName => {
          return caches.delete(cacheName);
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Stale-while-revalidate strategy
self.addEventListener('fetch', event => {
  // Skip cross-origin requests
  if (!event.request.url.startsWith(self.location.origin) &&
      !event.request.url.startsWith('https://cdn.jsdelivr.net') &&
      !event.request.url.startsWith('https://cdnjs.cloudflare.com')) {
    return;
  }

  // Skip non-GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  // Skip analytics and API calls
  if (event.request.url.includes('/api/') || 
      event.request.url.includes('analytics') ||
      event.request.url.includes('socket.io')) {
    return;
  }
  
  event.respondWith(
    caches.match(event.request)
      .then(cachedResponse => {
        const fetchPromise = fetch(event.request)
          .then(networkResponse => {
            // Don't cache errors or non-successful responses
            if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
              return networkResponse;
            }

            // Clone the response as it's a stream and can only be consumed once
            const responseToCache = networkResponse.clone();
            
            // Cache the new response
            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });

            return networkResponse;
          })
          .catch(() => {
            // Network failed, try to return a fallback for HTML pages
            if (event.request.headers.get('Accept').includes('text/html')) {
              return caches.match('/offline.html');
            }
            return null;
          });
        
        // Return the cached response immediately if we have it, otherwise wait for the network
        return cachedResponse || fetchPromise;
      })
  );
});

// Background sync for forms
self.addEventListener('sync', event => {
  if (event.tag === 'crime-report-sync') {
    event.waitUntil(syncCrimeReports());
  }
});

// Function to sync crime reports when back online
async function syncCrimeReports() {
  try {
    // Get saved crime reports from IndexedDB
    const db = await openDB();
    const savedReports = await db.getAll('unsyncedReports');
    
    if (!savedReports || savedReports.length === 0) {
      return;
    }
    
    // Try to send each report to the server
    for (const report of savedReports) {
      try {
        const response = await fetch('/api/reports/submit/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': report.csrf_token
          },
          body: JSON.stringify(report.data)
        });
        
        if (response.ok) {
          // If successful, remove from IndexedDB
          await db.delete('unsyncedReports', report.id);
        }
      } catch (err) {
        console.error('Failed to sync report:', err);
      }
    }
  } catch (err) {
    console.error('Error in syncCrimeReports:', err);
  }
}

// Simple IndexedDB wrapper
async function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('KingsParkCPFOfflineDB', 1);
    
    request.onupgradeneeded = event => {
      const db = event.target.result;
      db.createObjectStore('unsyncedReports', { keyPath: 'id', autoIncrement: true });
    };
    
    request.onsuccess = event => resolve(event.target.result);
    request.onerror = event => reject(event.target.error);
  });
}

// Handle push notifications
self.addEventListener('push', event => {
  if (event.data) {
    const data = event.data.json();
    const options = {
      body: data.message || 'New notification from Kings Park CPF',
      icon: '/static/images/icons/icon-192x192.png',
      badge: '/static/images/icons/badge-72x72.png',
      vibrate: [100, 50, 100],
      data: {
        url: data.url || '/'
      }
    };
    
    event.waitUntil(
      self.registration.showNotification(data.title || 'Kings Park CPF Update', options)
    );
  }
});

// Handle notification clicks
self.addEventListener('notificationclick', event => {
  event.notification.close();
  
  event.waitUntil(
    clients.openWindow(event.notification.data.url || '/')
  );
});
