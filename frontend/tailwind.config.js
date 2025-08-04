/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        secondary: {
          50: '#fdf4ff',
          100: '#fae8ff',
          200: '#f5d0fe',
          300: '#f0abfc',
          400: '#e879f9',
          500: '#d946ef',
          600: '#c026d3',
          700: '#a21caf',
          800: '#86198f',
          900: '#701a75',
        },
        success: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        },
        warning: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
        },
        error: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1' }],
        '6xl': ['3.75rem', { lineHeight: '1' }],
      },
      fontWeight: {
        thin: '100',
        extralight: '200',
        light: '300',
        normal: '400',
        medium: '500',
        semibold: '600',
        bold: '700',
        extrabold: '800',
        black: '900',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      borderRadius: {
        '4xl': '2rem',
        '5xl': '2.5rem',
      },
      boxShadow: {
        'soft': '0 2px 15px -3px rgba(0, 0, 0, 0.07), 0 10px 20px -2px rgba(0, 0, 0, 0.04)',
        'medium': '0 4px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        'large': '0 10px 40px -10px rgba(0, 0, 0, 0.15), 0 2px 10px -2px rgba(0, 0, 0, 0.05)',
        'glow': '0 0 20px rgba(59, 130, 246, 0.5)',
        'glow-purple': '0 0 20px rgba(147, 51, 234, 0.5)',
        'glow-pink': '0 0 20px rgba(236, 72, 153, 0.5)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
        'float': 'float 6s ease-in-out infinite',
        'spin-slow': 'spin 3s linear infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
        'wiggle': 'wiggle 1s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'gradient': 'gradient 3s ease infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.9)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        wiggle: {
          '0%, 100%': { transform: 'rotate(-3deg)' },
          '50%': { transform: 'rotate(3deg)' },
        },
        shimmer: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
        gradient: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
      zIndex: {
        '60': '60',
        '70': '70',
        '80': '80',
        '90': '90',
        '100': '100',
      },
    },
  },
  plugins: [
    // Custom component styles
    function({ addComponents, theme }) {
      addComponents({
        // Glass morphism effect
        '.glass': {
          backgroundColor: 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
        },
        
        // Button styles
        '.btn': {
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '0.5rem 1rem',
          borderRadius: '0.5rem',
          fontWeight: '500',
          transition: 'all 0.2s ease-in-out',
          cursor: 'pointer',
          border: 'none',
          outline: 'none',
          textDecoration: 'none',
          '&:focus': {
            outline: '2px solid transparent',
            outlineOffset: '2px',
          },
        },
        '.btn-sm': {
          padding: '0.375rem 0.75rem',
          fontSize: '0.875rem',
        },
        '.btn-lg': {
          padding: '0.75rem 1.5rem',
          fontSize: '1.125rem',
        },
        '.btn-primary': {
          backgroundColor: theme('colors.primary.600'),
          color: 'white',
          '&:hover': {
            backgroundColor: theme('colors.primary.700'),
            transform: 'translateY(-1px)',
            boxShadow: theme('boxShadow.large'),
          },
        },
        '.btn-secondary': {
          backgroundColor: 'rgba(255, 255, 255, 0.1)',
          color: 'white',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          '&:hover': {
            backgroundColor: 'rgba(255, 255, 255, 0.2)',
            transform: 'translateY(-1px)',
          },
        },
        
        // Card styles
        '.card': {
          backgroundColor: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: '1rem',
          padding: '1.5rem',
          boxShadow: theme('boxShadow.soft'),
          transition: 'all 0.3s ease-in-out',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: theme('boxShadow.large'),
          },
        },
        
        // Form styles
        '.form-group': {
          marginBottom: '1rem',
        },
        '.form-label': {
          display: 'block',
          marginBottom: '0.5rem',
          fontWeight: '500',
          fontSize: '0.875rem',
        },
        '.form-input': {
          width: '100%',
          padding: '0.75rem 1rem',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          borderRadius: '0.5rem',
          backgroundColor: 'rgba(255, 255, 255, 0.05)',
          color: 'white',
          transition: 'all 0.2s ease-in-out',
          '&:focus': {
            outline: 'none',
            borderColor: theme('colors.primary.400'),
            boxShadow: `0 0 0 3px ${theme('colors.primary.400')}20`,
          },
          '&::placeholder': {
            color: 'rgba(255, 255, 255, 0.5)',
          },
        },
        
        // Navigation styles
        '.nav-link': {
          display: 'flex',
          alignItems: 'center',
          padding: '0.5rem 1rem',
          color: 'rgba(255, 255, 255, 0.8)',
          textDecoration: 'none',
          borderRadius: '0.5rem',
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            color: 'white',
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            transform: 'translateY(-1px)',
          },
        },
        
        // Mobile navigation
        '.mobile-nav-link': {
          display: 'flex',
          alignItems: 'center',
          padding: '0.75rem 1rem',
          color: 'rgba(255, 255, 255, 0.8)',
          textDecoration: 'none',
          borderRadius: '0.5rem',
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            color: 'white',
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
          },
          '& svg': {
            marginRight: '0.75rem',
          },
        },
        
        // Dropdown styles
        '.dropdown-item': {
          display: 'flex',
          alignItems: 'center',
          padding: '0.5rem 1rem',
          color: 'rgba(255, 255, 255, 0.8)',
          textDecoration: 'none',
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            color: 'white',
          },
          '& svg': {
            marginRight: '0.75rem',
          },
        },
        
        // Stat card styles
        '.stat-card': {
          backgroundColor: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: '1rem',
          padding: '1.5rem',
          transition: 'all 0.3s ease-in-out',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: theme('boxShadow.large'),
          },
        },
        '.stat-icon': {
          width: '3rem',
          height: '3rem',
          borderRadius: '0.75rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '1rem',
          color: 'white',
        },
        '.stat-content': {
          flex: '1',
        },
        '.stat-title': {
          fontSize: '0.875rem',
          color: 'rgba(255, 255, 255, 0.7)',
          marginBottom: '0.5rem',
        },
        '.stat-value': {
          fontSize: '2rem',
          fontWeight: '700',
          color: 'white',
          marginBottom: '0.25rem',
        },
        '.stat-change': {
          fontSize: '0.75rem',
          fontWeight: '500',
        },
        
        // Quick action styles
        '.quick-action-card': {
          backgroundColor: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: '1rem',
          padding: '1.5rem',
          transition: 'all 0.3s ease-in-out',
          textDecoration: 'none',
          position: 'relative',
          overflow: 'hidden',
          '&:hover': {
            transform: 'translateY(-4px) scale(1.02)',
            boxShadow: theme('boxShadow.large'),
          },
        },
        '.quick-action-icon': {
          width: '3rem',
          height: '3rem',
          borderRadius: '0.75rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '1rem',
          color: 'white',
          fontSize: '1.5rem',
        },
        '.quick-action-content': {
          flex: '1',
        },
        '.quick-action-title': {
          fontSize: '1.125rem',
          fontWeight: '600',
          color: 'white',
          marginBottom: '0.5rem',
        },
        '.quick-action-description': {
          fontSize: '0.875rem',
          color: 'rgba(255, 255, 255, 0.7)',
          marginBottom: '1rem',
        },
        '.quick-action-arrow': {
          color: 'rgba(255, 255, 255, 0.5)',
          transition: 'all 0.2s ease-in-out',
        },
        '.quick-action-card:hover .quick-action-arrow': {
          color: 'white',
          transform: 'translateX(4px)',
        },
        
        // Activity styles
        '.activity-item': {
          display: 'flex',
          alignItems: 'center',
          padding: '1rem',
          borderRadius: '0.75rem',
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
          },
        },
        '.activity-icon': {
          width: '2.5rem',
          height: '2.5rem',
          borderRadius: '0.5rem',
          backgroundColor: 'rgba(59, 130, 246, 0.2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginRight: '1rem',
          color: 'rgb(59, 130, 246)',
        },
        '.activity-content': {
          flex: '1',
        },
        '.activity-title': {
          fontSize: '0.875rem',
          fontWeight: '500',
          color: 'white',
          marginBottom: '0.25rem',
        },
        '.activity-score': {
          fontSize: '0.75rem',
          color: 'rgba(255, 255, 255, 0.6)',
        },
        '.activity-time': {
          fontSize: '0.75rem',
          color: 'rgba(255, 255, 255, 0.5)',
        },
        
        // Progress styles
        '.progress-card': {
          backgroundColor: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: '1rem',
          padding: '1.5rem',
        },
        '.progress-title': {
          fontSize: '1.125rem',
          fontWeight: '600',
          color: 'white',
          marginBottom: '1rem',
        },
        '.progress-bar-container': {
          width: '100%',
          height: '0.5rem',
          backgroundColor: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '0.25rem',
          overflow: 'hidden',
          marginBottom: '0.75rem',
        },
        '.progress-bar': {
          height: '100%',
          backgroundColor: 'linear-gradient(90deg, #3b82f6, #8b5cf6)',
          borderRadius: '0.25rem',
          transition: 'width 1s ease-in-out',
        },
        '.progress-text': {
          fontSize: '0.875rem',
          color: 'rgba(255, 255, 255, 0.7)',
        },
        '.streak-display': {
          textAlign: 'center',
          marginBottom: '0.75rem',
        },
        '.streak-number': {
          fontSize: '3rem',
          fontWeight: '700',
          color: 'white',
          lineHeight: '1',
        },
        '.streak-label': {
          fontSize: '1rem',
          color: 'rgba(255, 255, 255, 0.7)',
          marginTop: '0.25rem',
        },
        
        // Skeleton loading
        '.skeleton': {
          backgroundColor: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '0.25rem',
          animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        },
        '.skeleton-text': {
          height: '1rem',
          marginBottom: '0.5rem',
        },
        
        // Spinner
        '.spinner': {
          border: '2px solid rgba(255, 255, 255, 0.1)',
          borderTop: '2px solid white',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
        },
      });
    },
  ],
} 