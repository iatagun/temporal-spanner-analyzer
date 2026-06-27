'use client';

import { useRef, useEffect, useMemo } from 'react';
import dynamic from 'next/dynamic';

const CytoscapeComponent = dynamic(
  () => import('react-cytoscapejs'),
  { ssr: false, loading: () => <div className="h-[400px] flex items-center justify-center bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-400">Yukleniyor...</div> }
);

const cyStyles = [
  {
    selector: 'node',
    style: {
      'background-color': '#4b5563',
      label: 'data(id)',
      'font-size': '11px',
      'text-valign': 'bottom',
      'text-halign': 'center',
      width: 28,
      height: 28,
      'border-width': 1,
      'border-color': '#374151',
    }
  },
  {
    selector: 'edge',
    style: {
      width: 1.5,
      'line-color': '#9ca3af',
      'curve-style': 'bezier',
      label: 'data(label)',
      'font-size': '9px',
      'text-rotation': 'autorotate',
      color: '#6b7280',
    }
  },
];

const layout = {
  name: 'cose',
  animate: false,
  nodeRepulsion: 400000,
  idealEdgeLength: 100,
};

export default function GraphViewer({ graph, label, height = 400, colorMap }) {
  const cyRef = useRef(null);

  useEffect(() => {
    if (cyRef.current && colorMap) {
      cyRef.current.nodes().forEach(n => {
        const c = colorMap[n.id()];
        if (c) {
          n.style('background-color', c);
          n.style('border-color', '#1f2937');
          n.style('border-width', 2);
        }
      });
    }
  }, [colorMap]);

  const elements = useMemo(() => {
    if (!graph || !graph.vertices || !graph.edges) return [];
    const nodes = graph.vertices.map(v => ({ data: { id: v } }));
    const edges = graph.edges.map((e, i) => ({
      data: { id: `e${i}`, source: e.u, target: e.v, label: e.label ? e.label.toFixed(2) : '' }
    }));
    return [...nodes, ...edges];
  }, [graph]);

  if (!graph || !graph.vertices) {
    return (
      <div style={{ height }} className="flex items-center justify-center bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-400">
        Veri yok
      </div>
    );
  }

  return (
    <div>
      <div className="mb-1.5 text-xs text-gray-500">{label}</div>
      <div style={{ height }} className="border border-gray-200 rounded-lg overflow-hidden bg-white">
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
