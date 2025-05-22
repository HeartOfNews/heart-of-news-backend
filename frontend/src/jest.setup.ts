// Add Jest setup code
import '@testing-library/jest-dom';

// Mock localStorage
const localStorageMock = (function() {
  let store: Record<string, string> = {};
  
  return {
    getItem: function(key: string) {
      return store[key] || null;
    },
    setItem: function(key: string, value: string) {
      store[key] = value.toString();
    },
    removeItem: function(key: string) {
      delete store[key];
    },
    clear: function() {
      store = {};
    }
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // Deprecated
    removeListener: jest.fn(), // Deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock window.location
delete window.location;
window.location = {
  href: '',
  // Add other properties as needed
} as unknown as Location;