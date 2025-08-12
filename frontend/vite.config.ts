import path from 'path';
import { defineConfig } from 'vite';

export default defineConfig(() => {
    return {
      resolve: {
        alias: {
          '@': path.resolve(__dirname, '.'),
        }
      },
      server: {
        host: true,
      },
      test: {
        globals: true,
        environment: 'jsdom',
        setupFiles: ['./vitest.setup.ts']
      }
    };
});
