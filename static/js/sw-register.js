// Service worker registration for offline support and faster loading
if ('serviceWorker' in navigator) {
  // Use window load event to reduce impact on page performance
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/js/service-worker.js')
      .then(registration => {
        console.log('Service worker registered successfully:', registration.scope);
      })
      .catch(error => {
        console.error('Service worker registration failed:', error);
      });
  });

  // Handle updates
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    if (refreshing) return;
    window.location.reload();
    refreshing = true;
  });
  
  // Set up background sync if available
  if ('SyncManager' in window) {
    // This will be used when users submit forms while offline
    document.addEventListener('DOMContentLoaded', () => {
      setupOfflineFormSubmission();
    });
  }
}

// Save form data when offline and sync later
function setupOfflineFormSubmission() {
  // Find forms that should work offline
  const offlineForms = document.querySelectorAll('form[data-offline="true"]');
  
  offlineForms.forEach(form => {
    form.addEventListener('submit', async event => {
      // Only intercept if we're offline
      if (!navigator.onLine) {
        event.preventDefault();
        
        try {
          // Get form data
          const formData = new FormData(form);
          const data = {};
          formData.forEach((value, key) => {
            data[key] = value;
          });
          
          // Get CSRF token
          const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
          
          // Save to IndexedDB for later sync
          const db = await openDB();
          await db.add('unsyncedReports', {
            data: data,
            csrf_token: csrfToken,
            timestamp: new Date().toISOString()
          });
          
          // Register for background sync
          const registration = await navigator.serviceWorker.ready;
          await registration.sync.register('crime-report-sync');
          
          // Show success message to user
          alert('You are currently offline. Your report has been saved and will be submitted automatically when you are back online.');
          
          // Redirect as if successful
          window.location.href = form.getAttribute('data-success-url') || '/';
          
        } catch (err) {
          console.error('Error saving form data for offline use:', err);
          // Let the form submit normally as fallback
          form.submit();
        }
      }
    });
  });
}

// Simple IndexedDB wrapper
async function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('KingsParkCPFOfflineDB', 1);
    
    request.onupgradeneeded = event => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains('unsyncedReports')) {
        db.createObjectStore('unsyncedReports', { keyPath: 'id', autoIncrement: true });
      }
    };
    
    request.onsuccess = event => {
      const db = event.target.result;
      resolve({
        add: (store, item) => {
          return new Promise((resolve, reject) => {
            const transaction = db.transaction(store, 'readwrite');
            const objectStore = transaction.objectStore(store);
            const request = objectStore.add(item);
            
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
          });
        },
        getAll: (store) => {
          return new Promise((resolve, reject) => {
            const transaction = db.transaction(store, 'readonly');
            const objectStore = transaction.objectStore(store);
            const request = objectStore.getAll();
            
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
          });
        },
        delete: (store, id) => {
          return new Promise((resolve, reject) => {
            const transaction = db.transaction(store, 'readwrite');
            const objectStore = transaction.objectStore(store);
            const request = objectStore.delete(id);
            
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
          });
        }
      });
    };
    
    request.onerror = event => reject(event.target.error);
  });
}
