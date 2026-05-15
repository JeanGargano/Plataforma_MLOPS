/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{ts,tsx}',   // escanea todos los archivos TypeScript/TSX
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Paleta personalizada del proyecto
        navy: {
          900: '#080c14',
          800: '#0d1525',
          700: '#111c30',
          600: '#1a2d4a',
          500: '#1f3660',
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Courier New', 'monospace'],
      }
    }
  },
  plugins: [],
}
