---
name: Solaris Tech Education
colors:
  surface: '#fefce8'
  surface-dim: '#fef9c3'
  surface-bright: '#fffdf2'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#fefce8'
  surface-container: '#fef9c3'
  surface-container-high: '#fef08a'
  surface-container-highest: '#fde047'
  on-surface: '#1c1917'
  on-surface-variant: '#44403c'
  inverse-surface: '#313124'
  inverse-on-surface: '#f3f2de'
  outline: '#a8a29e'
  outline-variant: '#d6d3d1'
  surface-tint: '#785a00'
  primary: '#eab308'
  on-primary: '#422006'
  primary-container: '#fef08a'
  on-primary-container: '#713f12'
  inverse-primary: '#f7be1d'
  secondary: '#885123'
  on-secondary: '#ffffff'
  secondary-container: '#ffb780'
  on-secondary-container: '#794619'
  tertiary: '#00658e'
  on-tertiary: '#ffffff'
  tertiary-container: '#60c5ff'
  on-tertiary-container: '#005072'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdf9a'
  primary-fixed-dim: '#f7be1d'
  on-primary-fixed: '#251a00'
  on-primary-fixed-variant: '#5a4300'
  secondary-fixed: '#ffdcc4'
  secondary-fixed-dim: '#ffb780'
  on-secondary-fixed: '#2f1400'
  on-secondary-fixed-variant: '#6b3a0d'
  tertiary-fixed: '#c7e7ff'
  tertiary-fixed-dim: '#83cfff'
  on-tertiary-fixed: '#001e2e'
  on-tertiary-fixed-variant: '#004c6c'
  background: '#fcfae6'
  on-background: '#1c1c10'
  surface-variant: '#e5e3d0'
typography:
  display-lg:
    fontFamily: geist
    fontSize: 64px
    fontWeight: '800'
    lineHeight: '1.1'
    letterSpacing: -0.04em
  headline-lg:
    fontFamily: geist
    fontSize: 40px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: geist
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
  headline-md:
    fontFamily: geist
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.4'
  body-lg:
    fontFamily: inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  body-sm:
    fontFamily: inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
  code-md:
    fontFamily: jetbrainsMono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1.5'
  label-caps:
    fontFamily: inter
    fontSize: 12px
    fontWeight: '700'
    lineHeight: '1.0'
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  container-max: 1200px
  gutter: 24px
  margin-mobile: 16px
  stack-xs: 8px
  stack-md: 24px
  stack-lg: 48px
  section-gap: 96px
---

## Brand & Style

The design system has evolved from a dark, technical aesthetic into a **warm, high-clarity, and accessible** learning environment. The brand personality remains **authoritative and structured**, but it now evokes an emotional response of **optimism, energy, and mental clarity**. It is designed to reduce the "visual heaviness" often associated with deep technical study, replacing it with a bright, sun-drenched workspace that stimulates focus.

The style is a blend of **Minimalism** and **Modern Corporate**, utilizing a sophisticated palette of creams and yellows to create a "paper-like" reading experience. 

- **Optimistic Precision:** The use of vibrant sunflower accents against soft cream backgrounds suggests a premium, modern educational tool.
- **High Legibility:** By moving to a light theme, the system prioritizes long-form reading and documentation clarity.
- **Structured Warmth:** While the colors are soft, the strict adherence to the Geist typeface and geometric layouts ensures the "technical" soul of the product remains intact.

## Colors

The palette is centered around a **Sun-Bleached Paper** strategy, optimized for daytime productivity and reducing eye strain compared to pure white.

- **Surface Logic:** The primary canvas uses `#fefce8` (Soft Cream). Containers use subtle shifts into `#fef9c3` to create a tiered hierarchy of information without relying on harsh lines.
- **Accent Logic:** 
    - **Primary (Sunflower):** A vibrant `#eab308` is used for calls to action, active progress states, and brand-critical elements.
    - **High-Contrast Text:** All typography is set in deep charcoals and rich browns (`#1c1917`) to ensure AAA accessibility against the yellow-tinted surfaces.
- **Interactive States:** Hover states on light surfaces should use a 5% black overlay. Borders use a soft stone-colored outline (`#d6d3d1`) to maintain structure.

## Typography

Typography remains the backbone of the technical identity. 

- **Geist** provides the structural, "engineered" look for titles and headers, now rendered in deep dark-brown tones for maximum impact.
- **Inter** handles the heavy lifting of instructional text. In this light theme, the 1.6 line height is critical for maintaining readability across wide content containers.
- **JetBrains Mono** is used for code and technical metadata. Use a slightly darker weight than the body text to ensure these monospace elements don't get lost against the light cream backgrounds.

## Layout & Spacing

The layout philosophy follows a **Fixed Grid** approach for desktop to preserve the readability of technical documentation.

- **12-Column Grid:** Desktop content is centered within a 1200px max-width container. 
- **The 4px Rhythm:** Every margin, padding, and gap must be a multiple of 4px to maintain the "mathematical" precision of the brand.
- **Fluid Adaptation:** On mobile, the grid collapses to a single column with 16px side margins. Complex horizontal elements like roadmaps must transition to a vertical "stepper" flow to remain functional on narrow screens.

## Elevation & Depth

In this light yellow theme, depth is achieved through **Tonal Layering** and **Soft Shadows**.

- **Surface Tiers:** Use the `surface-container` tokens to create depth. A `surface-container-low` card sitting on a `surface` background provides enough contrast without needing heavy borders.
- **Soft Ambient Shadows:** For high-priority elements like dropdowns or floating modals, use highly diffused, low-opacity shadows with a slight warm tint (e.g., `rgba(66, 32, 6, 0.08)`) to maintain the sunny, light feel.
- **Interactive Depth:** Buttons should feel tactile. On hover, a subtle "lift" effect using a small shadow is preferred over a color change alone.

## Shapes

The design system uses a **Rounded** shape language to soften the technical nature of the content.

- **Standard Elements:** Buttons, cards, and input fields use a `0.5rem` (8px) radius.
- **Icon Nodes:** For educational roadmaps, use circular shapes for nodes to differentiate them from UI components.
- **Status Chips:** Use full-pill rounding for difficulty and category labels to provide a distinct visual "tag" style.

## Components

### Buttons
- **Primary:** Solid Sunflower Yellow (`#eab308`) with Deep Brown text (`#422006`).
- **Secondary:** Outline variant using the `on-surface-variant` color for the stroke.
- **Ghost:** Transparent background with `#713f12` text, increasing in prominence on hover.

### Input Fields
- Background: `surface-bright` (`#fffdf2`).
- Border: 1px solid `outline-variant`.
- Active: Border transitions to Primary Sunflower with a 2px soft outer glow.

### Progress & Roadmaps
- **Nodes:** Large circular containers in `primary-container` with deep brown icons.
- **Connectors:** 2px solid lines using `outline-variant`. Completed paths should turn Sunflower Yellow.

### Cards & Containers
- Standard cards use `surface-container-low` with no border, or `surface` with a 1px `outline-variant` border for a more "document" feel.
- Lists should utilize alternating row colors (`surface` and `surface-container`) to help track information across wide screens.