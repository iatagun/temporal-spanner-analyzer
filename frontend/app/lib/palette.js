// Single source of truth for clique/series colors across GraphViewer,
// TrendsView, SpannerView and CompareView. Previously utils.js and
// TrendsView.js each hardcoded their own 15-color list -- different hexes,
// so the same clique got a different color depending on which view you
// were looking at, and both wrapped past their length (two unrelated
// cliques could land on the identical color).
//
// This is the dataviz skill's validated 8-hue categorical palette
// (references/palette.md) -- CVD-checked as a set via
// scripts/validate_palette.js for both the light and dark surface. A 9th+
// clique deliberately does NOT get a generated hue (that's the anti-pattern
// the skill calls out); it folds into a shared neutral "Diğer" (Other).

export const CLIQUE_PALETTE = [
  { name: 'blue', light: '#2a78d6', dark: '#3987e5' },
  { name: 'aqua', light: '#1baf7a', dark: '#199e70' },
  { name: 'yellow', light: '#eda100', dark: '#c98500' },
  { name: 'green', light: '#008300', dark: '#008300' },
  { name: 'violet', light: '#4a3aa7', dark: '#9085e9' },
  { name: 'red', light: '#e34948', dark: '#e66767' },
  { name: 'magenta', light: '#e87ba4', dark: '#d55181' },
  { name: 'orange', light: '#eb6834', dark: '#d95926' },
];

export const CLIQUE_OTHER_COLOR = { light: '#898781', dark: '#898781' };

export function prefersDark() {
  return typeof window !== 'undefined'
    && window.matchMedia?.('(prefers-color-scheme: dark)').matches;
}

// Index-stable: clique 0 always gets slot 0's hue, regardless of how many
// total cliques there are. Only indices >= 8 fold into the neutral "Other".
export function getCliqueColor(index, isDark = prefersDark()) {
  const slot = CLIQUE_PALETTE[index];
  if (!slot) return isDark ? CLIQUE_OTHER_COLOR.dark : CLIQUE_OTHER_COLOR.light;
  return isDark ? slot.dark : slot.light;
}

export function isOverflowClique(index) {
  return index >= CLIQUE_PALETTE.length;
}
