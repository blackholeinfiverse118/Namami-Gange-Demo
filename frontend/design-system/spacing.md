# BHIV Design System — Spacing and Grid Density

To facilitate immediate, sound-free operational awareness, the Namami Gange Platform enforces a **high-density grid discipline**. This removes superfluous whitespace and budgets layout regions so operators can scan 100+ variables without scrolling.

## 1. 8px Base Spacing Scale

All layout components align to a modular 8px scale:

| Token Name | Rem Value | Pixel Value | Typical Application |
| :--- | :--- | :--- | :--- |
| `space-xxs` | `0.25rem` | `4px` | Tiny inline spacing, confidence indicator heights, status dot offsets. |
| `space-xs` | `0.5rem` | `8px` | Small list items, badge paddings, telemetry details spacing. |
| `space-sm` | `0.75rem` | `12px` | Intermediate details, standard grid margins, inner card spacing. |
| `space-md` | `1rem` | `16px` | Standard page grid gap, primary card internal paddings. |
| `space-lg` | `1.5rem` | `24px` | Major pane boundaries, macro component gaps. |

## 2. Fit-to-Viewport Discipline

Sovereign command dashboards must **never require scrolling** for core operations. We budget our height and layout space systematically:

```
┌────────────────────────────────────────────────────────┐
│ TOP BAR: Uptime & Critical Tickers          [64px Max] │
├────────────────────────────────────────────────────────┤
│                                                        │
│ MAIN THREE-COLUMN VIEWPORT:                            │
│ - Col 1: Topology & Health matrix                      │
│ - Col 2: Waterway Corridor & Location detail           │
│ - Col 3: Replay logs & validation contract             │
│                                            [820px Max] │
│                                                        │
├────────────────────────────────────────────────────────┤
│ BOTTOM PANEL: Audit Ledgers & Recovery      [160px Max] │
└────────────────────────────────────────────────────────┘
Total Height = ~1044px (Optimized for standard 1080p command screens)
```

## 3. Density Best Practices

- **Minimal Padding**: Limit primary card padding to `12px` - `16px` (`space-sm` to `space-md`) to optimize data density.
- **Scrollable Sub-containers**: Elements like event ledgers or trace trackers must occupy fixed-height containers with thin, custom-styled scrollbars.
- **Compact Flex Alignments**: Use CSS Flexbox with `gap: 8px` or `gap: 12px` to group micro-telemetry cards without bloating the DOM structure.
- **Unified Borders**: Card borders should be thin (`1px`), clean, and semi-transparent (e.g., `rgba(255, 255, 255, 0.08)`) to maintain grid lines cleanly.
