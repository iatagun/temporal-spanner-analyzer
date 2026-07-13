'use client';

import { useRef, useEffect, useMemo } from 'react';
import dynamic from 'next/dynamic';
import { prefersDark, CHART_CHROME } from '../lib/palette';

const CytoscapeComponent = dynamic(
  () => import('react-cytoscapejs'),
  { ssr: false, loading: () => <div className="h-[400px] flex items-center justify-center bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg text-sm text-gray-400 dark:text-gray-500">Yükleniyor...</div> }
);

// Cytoscape's stylesheet is a plain JS object, not a Tailwind class, so it
// can't pick up `dark:` automatically -- it reads the same
// prefers-color-scheme signal palette.js uses for clique colors.
function buildCyStyles(isDark) {
  const mode = isDark ? 'dark' : 'light';
  return [
    {
      selector: 'node',
      style: {
        'background-color': CHART_CHROME.node.fill[mode],
        label: 'data(id)',
        'font-size': '11px',
        'text-valign': 'bottom',
        'text-halign': 'center',
        color: CHART_CHROME.node.label[mode],
        width: 28,
        height: 28,
        'border-width': 1,
        'border-color': CHART_CHROME.node.border[mode],
      }
    },
    {
      selector: 'edge',
      style: {
        width: 1.5,
        'line-color': CHART_CHROME.edge.line[mode],
        'curve-style': 'bezier',
        label: 'data(label)',
        'font-size': '9px',
        'text-rotation': 'autorotate',
        color: CHART_CHROME.edge.label[mode],
      }
    },
  ];
}

// cytoscape's 'cose' layout is a force-directed physics simulation --
// benchmarked at ~200ms for 100 nodes, ~4s for 500, ~16s for 1000, and
// ~62s for 2000 (roughly O(n^2)). A few-thousand-vertex corpus graph
// would take minutes and hang the tab.
const COSE_NODE_LIMIT = 300;
// A plain grid of everything above that limit is fast but visually
// useless -- a wall of same-size dots with no way to tell what matters.
// Showing only the most-connected TOP_N nodes with the real cose layout
// instead stays fast (well under COSE_NODE_LIMIT) *and* is the part of a
// large graph a linguist is most likely to care about.
const TOP_N_FOR_LARGE_GRAPHS = 150;

const COSE_LAYOUT = { name: 'cose', animate: false, nodeRepulsion: 400000, idealEdgeLength: 100 };

function reduceToTopDegreeNodes(graph, topN) {
  const degree = new Map();
  graph.vertices.forEach(v => degree.set(v, 0));
  graph.edges.forEach(e => {
    degree.set(e.u, (degree.get(e.u) || 0) + 1);
    degree.set(e.v, (degree.get(e.v) || 0) + 1);
  });
  const kept = new Set(
    [...graph.vertices].sort((a, b) => (degree.get(b) || 0) - (degree.get(a) || 0)).slice(0, topN)
  );
  return {
    vertices: graph.vertices.filter(v => kept.has(v)),
    edges: graph.edges.filter(e => kept.has(e.u) && kept.has(e.v)),
  };
}

export default function GraphViewer({ graph, label, height = 400, colorMap }) {
  const cyRef = useRef(null);
  const isDark = prefersDark();
  const cyStyles = useMemo(() => buildCyStyles(isDark), [isDark]);
  const borderColor = CHART_CHROME.node.border[isDark ? 'dark' : 'light'];

  useEffect(() => {
    if (cyRef.current && colorMap) {
      cyRef.current.nodes().forEach(n => {
        const c = colorMap[n.id()];
        if (c) {
          n.style('background-color', c);
          n.style('border-color', borderColor);
          n.style('border-width', 2);
        }
      });
    }
  }, [colorMap, borderColor]);

  const isLarge = !!graph && graph.vertices && graph.vertices.length > COSE_NODE_LIMIT;

  const displayGraph = useMemo(() => {
    if (!graph || !graph.vertices) return graph;
    if (!isLarge) return graph;
    return reduceToTopDegreeNodes(graph, TOP_N_FOR_LARGE_GRAPHS);
  }, [graph, isLarge]);

  const elements = useMemo(() => {
    if (!displayGraph || !displayGraph.vertices || !displayGraph.edges) return [];
    const nodes = displayGraph.vertices.map(v => ({ data: { id: v } }));
    const edges = displayGraph.edges.map((e, i) => ({
      data: { id: `e${i}`, source: e.u, target: e.v, label: e.label != null ? e.label.toFixed(2) : '' }
    }));
    return [...nodes, ...edges];
  }, [displayGraph]);

  if (!graph || !graph.vertices) {
    return (
      <div style={{ height }} className="flex items-center justify-center bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg text-sm text-gray-400 dark:text-gray-500">
        Veri yok
      </div>
    );
  }

  return (
    <div>
      <div className="mb-1.5 text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1.5">
        {label}
        {isLarge && (
          <span
            className="text-gray-400 dark:text-gray-500"
            title="Büyük grafiklerde tarayıcıyı kilitleyen fizik-tabanlı yerleşim yerine, en çok bağlantılı düğümlerin küçük bir alt kümesi gösterilir."
          >
            (büyük grafik: en bağlantılı {TOP_N_FOR_LARGE_GRAPHS}/{graph.vertices.length} düğüm)
          </span>
        )}
      </div>
      <div style={{ height }} className="border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden bg-white dark:bg-gray-950">
        <CytoscapeComponent
          elements={elements}
          style={{ width: '100%', height: '100%' }}
          stylesheet={cyStyles}
          layout={COSE_LAYOUT}
          cy={(cy) => { cyRef.current = cy; }}
        />
      </div>
    </div>
  );
}
