/** Chart colours. Status colours are reserved for states and always shown with a text label. */
export const chartTheme = {
  series: '#2a78d6',
  /** Second categorical series (validated against `series` for colour-vision deficiency). */
  series2: '#eb6834',
  grid: '#e2e8f0',
  axis: '#64748b',
  ink: '#0f172a',
  stockStatus: {
    'In Stock': '#0ca30c',
    'Low Stock': '#fab219',
    Critical: '#ec835a',
    'Out of Stock': '#d03b3b',
  } as Record<string, string>,
}
