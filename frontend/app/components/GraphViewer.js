'use client';

import { useRef, useEffect, useMemo } from 'react';
import dynamic from 'next/dynamic';
import { prefersDark } from '../lib/palette';

const CytoscapeComponent = dynamic(
  () => import('react-cytoscapejs'),
  { ssr: false, loading: () => <div className="h-[400px] flex items-center justify-center bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg text-sm text-gray-400 dark:text-gray-500">Yükleniyor...</div> }
);

// Cytoscape's stylesheet is a plain JS object, not a Tailwind class, so it
// can't pick up `dark:` automatically -- it reads the same
// prefers-color-scheme signal palette.js uses for clique colors.
function buildCyStyles(isDark) {
  return [
    {
      selector: 'node',
      style: {
        'background-color': isDark ? '#9ca3af' : '#4b5563',
        label: 'data(id)',
        'font-size': '11px',
        'text-valign': 'bottom',
        'text-halign': 'center',
        color: isDark ? '#e5e7eb' : '#111827',
        width: 28,
        height: 28,
        'border-width': 1,
        'border-color': isDark ? '#6b7280' : '#374151',
      }
    },
    {
      selector: 'edge',
      style: {
        width: 1.5,
        'line-color': isDark ? '#6b7280' : '#9ca3af',
        'curve-style': 'bezier',
        label: 'data(label)',
        'font-size': '9px',
        'text-rotation': 'autorotate',
        color: isDark ? '#9ca3af' : '#6b7280',
      }
    },
  ];
}

const layout = {
  name: 'cose',
  animate: false,
  nodeRepulsion: 400000,
  idealEdgeLength: 100,
};

export default function GraphViewer({ graph, label, height = 400, colorMap }) {
  const cyRef = useRef(null);
  const isDark = prefersDark();
  const cyStyles = useMemo(() => buildCyStyles(isDark), [isDark]);
  const borderColor = isDark ? '#9ca3af' : '#1f2937';

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

  const elements = useMemo(() => {
    if (!graph || !graph.vertices || !graph.edges) return [];
    const nodes = graph.vertices.map(v => ({ data: { id: v } }));
    const edges = graph.edges.map((e, i) => ({
      data: { id: `e${i}`, source: e.u, target: e.v, label: e.label != null ? e.label.toFixed(2) : '' }
    }));
    return [...nodes, ...edges];
  }, [graph]);

  if (!graph || !graph.vertices) {
    return (
      <div style={{ height }} className="flex items-center justify-center bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg text-sm text-gray-400 dark:text-gray-500">
        Veri yok
      </div>
    );
  }

  return (
    <div>
      <div className="mb-1.5 text-xs text-gray-500 dark:text-gray-400">{label}</div>
      <div style={{ height }} className="border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden bg-white dark:bg-gray-950">
        <CytoscapeComponent
          elements={elements}
          style={{ width: '100%', height: '100%' }}
          stylesheet={cyStyles}
          layout={layout}
          cy={(cy) => { cyRef.current = cy; }}
        />
      </div>
    </div>
  );
}
