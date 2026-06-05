'use client';

import { useCallback, useRef, useEffect, useMemo, useState } from 'react';
import dynamic from 'next/dynamic';

const CytoscapeComponent = dynamic(
  () => import('react-cytoscapejs'),
  { ssr: false, loading: () => <div style={{ height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f5f5f5', borderRadius: 8 }}>Loading graph...</div> }
);

const CLIQUE_COLORS = [
  '#e74c3c', '#2ecc71', '#f39c12', '#3498db', '#9b59b6',
  '#1abc9c', '#e67e22', '#34495e', '#16a085', '#c0392b',
  '#27ae60', '#8e44ad', '#d35400', '#2980b9', '#2c3e50',
];

function nodeColor(v, colorMap) {
  return colorMap && colorMap[v] ? colorMap[v] : '#4a90d9';
}

const cyStyles = [
  {
    selector: 'node',
    style: {
      'background-color': '#4a90d9',
      label: 'data(id)',
      'font-size': '12px',
      'text-valign': 'bottom',
      'text-halign': 'center',
      width: 30,
      height: 30,
      'border-width': 1,
      'border-color': '#2c5f8a',
    }
  },
  {
    selector: 'edge',
    style: {
      width: 2,
      'line-color': '#888',
      'curve-style': 'bezier',
      label: 'data(label)',
      'font-size': '10px',
      'text-rotation': 'autorotate',
      color: '#666',
    }
  },
  {
    selector: 'edge.highlight',
    style: {
      'line-color': '#e74c3c',
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

export default function GraphViewer({ graph, label, height = 400, colorMap }) {
  const cyRef = useRef(null);

  useEffect(() => {
    if (cyRef.current && colorMap) {
      cyRef.current.nodes().forEach(n => {
        const c = colorMap[n.id()];
        if (c) {
          n.style('background-color', c);
          n.style('border-color', '#333');
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
    return <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f5f5f5', borderRadius: 8, color: '#999' }}>No graph data</div>;
  }

  return (
    <div>
      <div style={{ marginBottom: 6, fontWeight: 600, fontSize: 14, color: '#333' }}>{label}</div>
      <div style={{ height, border: '1px solid #ddd', borderRadius: 8, overflow: 'hidden' }}>
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
