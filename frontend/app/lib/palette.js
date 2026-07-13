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

// Chart chrome (axis/grid/node/edge colors) for GraphViewer's cytoscape
// stylesheet and TrendsView's D3 axes/bars -- both set colors as plain JS
// hex (cytoscape style objects and D3 .attr() calls can't read `dark:`
// Tailwind variants), so they used to hardcode their own cool-gray hexes
// independently of each other and of the page's actual palette. This is
// the single place those live now, tuned to sit on the warm "paper"
// surface (globals.css --page-bg) instead of the old flat white/black.
// Deliberately NOT part of CLIQUE_PALETTE -- these are UI chrome, not
// CVD-checked categorical data colors.
export const CHART_CHROME = {
  node: {
    fill: { light: '#57524a', dark: '#c9c2b4' },
    border: { light: '#3a362f', dark: '#8f8775' },
    label: { light: '#1c1a16', dark: '#f3efe6' },
  },
  edge: {
    line: { light: '#b8b0a0', dark: '#5c5648' },
    label: { light: '#6b6457', dark: '#a39c8f' },
  },
  axis: { light: '#6b6457', dark: '#a39c8f' },
  // Same values as globals.css's --color-accent / dark-mode override --
  // kept as a literal pair here since D3 .attr() needs a plain string.
  barStroke: { light: '#28507e', dark: '#8fb0d8' },
};
