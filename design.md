# FINOVO — Ultra-Premium Glassmorphism Design Philosophy

A state-of-the-art, ultra-attractive fintech design system pushing the boundaries of web aesthetics. Combining dynamic ambient lighting, true glassmorphic surfaces, tactile noise textures, and hyper-refined typography for an unparalleled luxury experience.

---

## 1. Typography System

Three distinct font families, each assigned a strict, non-substitutable role:

- **Fraunces** *(serif, weight 400–600, italic for emphasis)* — Reserved exclusively for main hero titles, section headlines (`h1`, `h2`), and modal titles.
  - *Styling Rule*: Text can be styled with an animated gradient clip for maximum visual impact, especially on key feature titles.
- **Inter** *(sans-serif, weight 400–700)* — All primary UI copy, body text, form labels, navigation links, and standard buttons.
- **IBM Plex Mono** *(monospace, weight 400–600)* — Every numeric figure, currency value, percentage, ROI rate, transaction hash, ticker symbol, timestamp, badge kicker, and table header.
  - *Rule*: Must be rendered in `IBM Plex Mono` with `font-variant-numeric: tabular-nums`.

---

## 2. Palette & Ambient Atmosphere

### Palette Tokens
```css
:root {
  /* Atmosphere & Base Surfaces */
  --bg:         #030507; /* Deep Void base */
  --glass-bg:   rgba(14, 19, 25, 0.45); /* Translucent glass */
  --glass-bg-2: rgba(21, 28, 37, 0.55); /* Elevated translucent glass */
  --field:      rgba(10, 14, 19, 0.6); /* Form input background */
  --line:       rgba(255, 255, 255, 0.08); /* Hairline border stroke */
  --line-light: rgba(255, 255, 255, 0.15); /* Highlight edge */

  /* Text Hierarchy */
  --text:       #F1F3F7; /* High-contrast body text */
  --mute:       #8A94A4; /* Muted secondary copy */

  /* Primary Accent: Deep Emerald (Primary Action & Financial Growth) */
  --emerald:      #10B981;
  --emerald-soft: #34D399;
  --emerald-deep: #059669;

  /* Secondary Accent: Warm Gold (Premium Tier, Highlights & Signals) */
  --gold:      #F59E0B;
  --gold-soft: #FBBF24;
}
```

### The "Living Canvas" Atmosphere
1. **Animated Ambient Orbs**: The background is not a static color, but a deep void (`#030507`) containing slowly drifting, large, blurred geometric orbs (Emerald and Gold). This creates a dynamic, moving light source behind all components.
2. **Noise Texture**: A subtle SVG film-grain/noise texture is overlaid on the background or cards to provide a tactile, premium matte finish.

---

## 3. Surface Architecture: True Glassmorphism

1. **Translucent Panels**: All cards, sidebars, and modals use a highly translucent background (`rgba(14, 19, 25, 0.45)`) paired with a strong `backdrop-filter: blur(24px)`.
2. **Edge Lighting**: To define the glass edges, surfaces must have a 1px semi-transparent white border (`border: 1px solid rgba(255,255,255,0.08)`), combined with an inner top-edge glow (`box-shadow: inset 0 1px 0 rgba(255,255,255,0.15)`).
3. **Floating Shadows**: Deep, soft drop shadows (`box-shadow: 0 15px 35px rgba(0,0,0,0.5)`) lift the glass off the background canvas.

---

## 4. Component Design System

### Primary Buttons
- **Gradient Fill**: `linear-gradient(135deg, var(--emerald) 0%, var(--emerald-deep) 100%)`.
- **Interactions**: Shimmer sweeps on hover, accompanied by a pulsing emerald outer glow.

### Cards & Panels
- **Hover Physics**: Smooth elevation `translateY(-5px)` and an increase in backdrop-filter blur and shadow spread.
- **Featured / Highlight Card**: Elevated with a glowing gold translucent border, ambient gold inner shadow, and top-right gold gradient pill badge.

### Styled Empty States
Empty data lists use a structured component:
- Centered circular icon badge with a glowing ring.
- Muted secondary explanation copy.
- Primary CTA action button.

---

## 5. Motion & Accessibility

- **Ambient Drift**: Background orbs drift slowly (20-30s animation cycles) using CSS keyframes.
- **Micro-interactions**: Hover states are smooth (`300ms cubic-bezier`).
- **Accessibility**: Respect `prefers-reduced-motion: reduce` by stopping background orb animations and disabling hover lifts.