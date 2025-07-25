// Service Worker for Smart Inventory PWA
const CACHE_NAME = 'smart-inventory-v1';
const urlsToCache = [
  '/',
  '/static/barcode.js',
  '/static/manifest.json',
  'https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js'
];

// Install event - cache resources
self.addEventListener('install', event => {
  console.log('Service Worker installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Caching app shell');
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        console.log('Service Worker installed successfully');
        return self.skipWaiting();
      })
      .catch(error => {
        console.error('Service Worker install failed:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('Service Worker activating...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('Service Worker activated');
      return self.clients.claim();
    })
  );
});

// Fetch event - serve from cache when possible
self.addEventListener('fetch', event => {
  // Only handle GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  // Skip caching for API calls that need fresh data
  if (event.request.url.includes('/api/') || 
      event.request.url.includes('/submit_stock') ||
      event.request.url.includes('/get_product') ||
      event.request.url.includes('/test_upload')) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Return cached version or fetch from network
        if (response) {
          console.log('Serving from cache:', event.request.url);
          return response;
        }
        
        console.log('Fetching from network:', event.request.url);
        return fetch(event.request).then(response => {
          // Don't cache non-successful responses
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }

          // Clone the response before caching
          const responseToCache = response.clone();
          caches.open(CACHE_NAME)
            .then(cache => {
              cache.put(event.request, responseToCache);
            });

          return response;
        });
      })
      .catch(error => {
        console.error('Fetch failed:', error);
        // You could return a custom offline page here
        return new Response('เกิดข้อผิดพลาด: ไม่สามารถเชื่อมต่อได้', {
          status: 503,
          statusText: 'Service Unavailable',
          headers: new Headers({
            'Content-Type': 'text/plain; charset=UTF-8'
          })
        });
      })
  );
});

// Handle background sync (for offline form submissions)
self.addEventListener('sync', event => {
  if (event.tag === 'stock-sync') {
    console.log('Background sync triggered');
    event.waitUntil(syncStockData());
  }
});

async function syncStockData() {
  // This would handle offline form submissions when connection is restored
  console.log('Syncing offline stock data...');
  // Implementation would go here
}