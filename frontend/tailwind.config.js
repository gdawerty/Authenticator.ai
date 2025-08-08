/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        charcoal: {
          50: '#f8f8f8',
          100: '#e8e8e8',
          200: '#d1d1d1',
          300: '#b4b4b4',
          400: '#888888',
          500: '#6d6d6d',
          600: '#5d5d5d',
          700: '#4f4f4f',
          800: '#454545',
          900: '#3d3d3d',
          950: '#111111',
        },
        // Gradient colors for orbs
        orb: {
          blue: 'rgba(59, 130, 246, 0.15)',
          purple: 'rgba(147, 51, 234, 0.1)',
          emerald: 'rgba(16, 185, 129, 0.15)'
        }
      },
      animation: {
        // Dot animations
        'float-dot-1': 'floatDot1 12s ease-in-out infinite',
        'float-dot-2': 'floatDot2 15s ease-in-out infinite',
        'float-dot-3': 'floatDot3 18s ease-in-out infinite',
        // Shape animations
        'float-circle-1': 'floatCircle1 8s ease-in-out infinite',
        'float-square-1': 'floatSquare1 5s ease-in-out infinite',
        'float-circle-2': 'floatCircle2 4s ease-in-out infinite',
        'float-square-2': 'floatSquare2 6s ease-in-out infinite',
        // Orb animations
        'pulse-orb': 'pulseOrb 4s ease-in-out infinite'
      },
      keyframes: {
        // Floating Dots
        floatDot1: {
          '0%, 100%': { transform: 'translate(0px, 0px) scale(1)', opacity: '0.8' },
          '25%': { transform: 'translate(30px, -40px) scale(1.2)', opacity: '1' },
          '50%': { transform: 'translate(-20px, -80px) scale(0.8)', opacity: '0.6' },
          '75%': { transform: 'translate(50px, -30px) scale(1.1)', opacity: '0.9' }
        },
        floatDot2: {
          '0%, 100%': { transform: 'translate(0px, 0px) rotate(0deg)', opacity: '0.7' },
          '20%': { transform: 'translate(-40px, 30px) rotate(72deg)', opacity: '1' },
          '40%': { transform: 'translate(20px, -50px) rotate(144deg)', opacity: '0.5' },
          '60%': { transform: 'translate(-30px, -20px) rotate(216deg)', opacity: '0.8' },
          '80%': { transform: 'translate(40px, 40px) rotate(288deg)', opacity: '0.9' }
        },
        floatDot3: {
          '0%, 100%': { transform: 'translate(0px, 0px)', opacity: '0.6' },
          '33%': { transform: 'translate(60px, -30px)', opacity: '1' },
          '66%': { transform: 'translate(-40px, -60px)', opacity: '0.4' }
        },
        // Geometric Shapes
        floatCircle1: {
          '0%, 100%': { transform: 'translate(0px, 0px) scale(1)', opacity: '0.6' },
          '25%': { transform: 'translate(40px, -30px) scale(1.1)', opacity: '0.8' },
          '50%': { transform: 'translate(-20px, -60px) scale(0.9)', opacity: '0.4' },
          '75%': { transform: 'translate(30px, -40px) scale(1.2)', opacity: '0.7' }
        },
        floatSquare1: {
          '0%, 100%': { transform: 'rotate(45deg) translate(0px, 0px) scale(1)', opacity: '0.5' },
          '33%': { transform: 'rotate(135deg) translate(35px, -25px) scale(1.3)', opacity: '0.8' },
          '66%': { transform: 'rotate(225deg) translate(-30px, -50px) scale(0.8)', opacity: '0.3' }
        },
        floatCircle2: {
          '0%, 100%': { transform: 'translate(0px, 0px) rotate(0deg)', opacity: '0.7' },
          '50%': { transform: 'translate(-45px, 35px) rotate(180deg)', opacity: '0.9' }
        },
        floatSquare2: {
          '0%, 100%': { transform: 'rotate(45deg) translate(0px, 0px) scale(1)', opacity: '0.4' },
          '25%': { transform: 'rotate(135deg) translate(-40px, 30px) scale(1.4)', opacity: '0.7' },
          '50%': { transform: 'rotate(225deg) translate(20px, -45px) scale(0.7)', opacity: '0.9' },
          '75%': { transform: 'rotate(315deg) translate(50px, -20px) scale(1.1)', opacity: '0.5' }
        },
        // Gradient Orbs
        pulseOrb: {
          '0%, 100%': { opacity: '0.3', transform: 'scale(1)' },
          '50%': { opacity: '0.6', transform: 'scale(1.05)' }
        }
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'minimal-gradient': 'linear-gradient(180deg, #111111 0%, #1a1a1a 100%)'
      },
      backdropBlur: {
        xs: '2px',
        sm: '4px',
        md: '8px',
        lg: '12px',
        xl: '20px'
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('tailwindcss-animate')
  ],
}