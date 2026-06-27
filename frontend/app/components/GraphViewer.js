'use client';

import { useRef, useEffect, useMemo } from 'react';
import dynamic from 'next/dynamic';

const CytoscapeComponent = dynamic(
  () => import('react-cytoscapejs'),
  { ssr: false, loading: () => <div className="h-[400px] flex items-center justify-center bg-slate-50 rounded-xl">Loading graph...</div> }
);

const cyStyles = [
  {
    selector: 'node',
    style: {
      'background-color': '#6366f1',
      label: 'data(id)',
      'font-size': '12px',
      'text-valign': 'bottom',
      'text-halign': 'center',
      width: 30,
      height: 30,
      'border-width': 1,
      'border-color': '#4338ca',
    }
  },
  {
    selector: 'edge',
    style: {
      width: 2,
      'line-color': '#94a3b8',
      'curve-style': 'bezier',
      label: 'data(label)',
      'font-size': '10px',
      'text-rotation': 'autorotate',
      color: '#64748b',
    }
  },
  {
    selector: 'edge.highlight',
    style: {
      'line-color': '#ef4444',
      width: 3,
    }
  },
];

const layout = {
  name: 'cose',
  animate: false,
  nodeRepulsion: 400000,
  idealEdgeLength: 100,
};

export default function GraphViewer({ graph, label, height = 400, colorMap, icon }) {
  const cyRef = useRef(null);

  useEffect(() => {
    if (cyRef.current && colorMap) {
      cyRef.current.nodes().forEach(n => {
        const c = colorMap[n.id()];
        if (c) {
          n.style('background-color', c);
          n.style('border-color', '#1e293b');
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
      <div style={{ height }} className="flex items-center justify-center bg-slate-50 rounded-xl text-text-muted text-sm">
        No graph data
      </div>
    );
  }

  return (
    <div>
      <div className="mb-2 flex items-center gap-2">
        {icon && <span className="text-primary">{icon}</span>}
        <span className="text-sm font-semibold text-text">{label}</span>
      </div>
      <div style={{ height }} className="border border-border rounded-xl overflow-hidden bg-white shadow-sm">
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
