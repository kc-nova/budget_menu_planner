# kc-nova Brand Guidelines

> **Version 1.0** · October 2026 · Maintained by kc-nova

---

## 1. Brand Identity

**kc-nova** is an independent open-source software brand focused on smart home automation, budget-conscious living, and accessible productivity tools. The brand communicates clarity, precision, and warmth.

---

## 2. Logo Usage

| Asset | File | Usage |
|---|---|---|
| Primary SVG | `kc-nova_logo.svg` | All digital surfaces, README headers, docs |
| Raster PNG | `kc-nova_logo.png` | Email, platforms without SVG support |
| Favicon | `favicon.ico` | Browser tabs, PWA icons |

### Clear Space
Always maintain a minimum clear space equal to the height of the "k" letterform on all sides of the logo.

### Do NOT
- Stretch or distort the logo
- Change logo colors outside approved palette
- Apply drop shadows or filters
- Place on low-contrast backgrounds without the white shield variant

---

## 3. Color Palette

All tokens are defined in [`brand_theme.json`](./brand_theme.json).

### Primary — kc-nova Blue
| Token | Hex | Usage |
|---|---|---|
| `colors.primary.default` | `#1B4F8A` | CTAs, headers, links, icon fills |
| `colors.primary.light` | `#2E6DB4` | Hover states |
| `colors.primary.dark` | `#0D2E52` | Active states, dark mode text |

### Accent — Nova Gold
| Token | Hex | Usage |
|---|---|---|
| `colors.accent.default` | `#F5A623` | Highlights, badges, "nova" wordmark |
| `colors.accent.light` | `#F7BB54` | Soft emphasis |
| `colors.accent.dark` | `#C47D08` | Active/pressed accent |

### Secondary — Foliage Green
| Token | Hex | Usage |
|---|---|---|
| `colors.secondary.default` | `#2C7A5E` | Success states, eco/health indicators |

### Dark Mode Background
| Token | Hex |
|---|---|
| `colors.dark_mode.background` | `#0D1B2A` |
| `colors.dark_mode.surface` | `#1A2D3D` |
| `colors.dark_mode.text_primary` | `#F1F5F9` |

---

## 4. Typography

### Font Stack
```
Primary (UI): 'Inter', 'Segoe UI', system-ui, sans-serif
Monospace:    'JetBrains Mono', 'Fira Code', monospace
```

### Hierarchy
| Level | Size | Weight | Use |
|---|---|---|---|
| Display | 2.25rem (36px) | 800 | Hero headings |
| H1 | 1.875rem (30px) | 700 | Page titles |
| H2 | 1.5rem (24px) | 700 | Section headers |
| H3 | 1.25rem (20px) | 600 | Subsections |
| Body | 1rem (16px) | 400 | Paragraph text |
| Small | 0.875rem (14px) | 400 | Captions, metadata |
| Mono | 0.875rem (14px) | 400 | Code, data |

---

## 5. Component Defaults

### Buttons
- Height: 40px
- Padding: 0 16px
- Border radius: 8px
- Font weight: 600

### Input fields
- Height: 40px
- Border radius: 8px
- Border: 1px solid `colors.neutral.200` (light) / `colors.dark_mode.border` (dark)

### Cards
- Padding: 20px
- Border radius: 12px
- Elevation: `elevation.md` = `0 4px 12px rgba(0,0,0,0.12)`

---

## 6. Iconography

Use [Material Design Icons (MDI)](https://materialdesignicons.com/) throughout kc-nova applications to ensure consistency with the Home Assistant ecosystem.

Preferred icon size: **24px** at 1× scale.

---

## 7. Voice & Tone

| Attribute | Description |
|---|---|
| **Clear** | Avoid jargon. Explain features in plain language. |
| **Helpful** | Every piece of UI copy should guide the user forward. |
| **Warm** | Friendly, not corporate. Use "you" and "your". |
| **Concise** | Respect the user's time. Be brief. |

---

## 8. Application of Brand in Open-Source Projects

All open-source repositories under `kc-nova` MUST:

1. Include this `assets/` directory or link to it.
2. Reference `brand_theme.json` tokens in any custom UI.
3. Apply the kc-nova logo and color scheme to Swagger/OpenAPI documentation.
4. Use the MIT license.
5. Include `kc-nova` in the `codeowners` field of HA integrations.

---

*Questions? Open an issue at [github.com/kc-nova](https://github.com/kc-nova).*
