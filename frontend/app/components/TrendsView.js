'use client';

import { useRef, useEffect, useMemo, useState } from 'react';
import * as d3 from 'd3';
import { formatTime } from '../lib/utils';

const COLORS = ['#dc2626','#16a34a','#ca8a04','#2563eb','#9333ea','#0891b2','#ea580c','#4f46e5','#0d9488','#db2777','#65a30d','#a855f7','#eab308','#3b82f6','#64748b'];

export default function TrendsView({ data, height = 300 }) {
  const svgRef = useRef(null);
  const lineSvgRef = useRef(null);
  const [showLines, setShowLines] = useState(true);

  const timelines = useMemo(() => data?.timelines || [], [data]);
  const timeRange = useMemo(() => data?.time_range || [0, 1], [data]);
  const windowEdges = useMemo(() => data?.window_edges || [], [data]);

  useEffect(() => {
    if (!svgRef.current || timelines.length === 0) return;
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();
    const margin = { top: 20, right: 20, bottom: 40, left: 120 };
    const width = svgRef.current.clientWidth - margin.left - margin.right;
    const gHeight = height - margin.top - margin.bottom;
    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);
    const xScale = d3.scaleLinear().domain(timeRange).range([0, width]);
    const yScale = d3.scaleBand().domain(timelines.map(t => t.label)).range([0, gHeight]).padding(0.15);
    const maxSize = d3.max(timelines, t => t.max_size) || 1;
    const colorScale = d3.scaleSequential(d3.interpolateBlues).domain([1, maxSize]);

    g.append('g').attr('transform', `translate(0,${gHeight})`)
      .call(d3.axisBottom(xScale).ticks(8).tickFormat(formatTime)).attr('font-size', '10px');
    g.append('g').call(d3.axisLeft(yScale)).attr('font-size', '10px');
    g.append('text').attr('x', width / 2).attr('y', gHeight + 35)
      .attr('text-anchor', 'middle').attr('font-size', '11px').attr('fill', '#6b7280').text('Zaman');

    timelines.forEach(tl => {
      tl.snapshots.forEach(s => {
        const y = yScale(tl.label);
        if (y == null) return;
        g.append('rect').attr('x', xScale(s.window_start)).attr('y', y)
          .attr('width', Math.max(xScale(s.window_end) - xScale(s.window_start), 2))
          .attr('height', yScale.bandwidth()).attr('fill', colorScale(s.size))
          .attr('stroke', '#1e40af').attr('stroke-width', 0.5).attr('rx', 1)
          .append('title').text(`${tl.label}\n${s.size} uye\n${s.members.slice(0,5).join(', ')}`);
      });
    });
  }, [timelines, timeRange, height]);

  useEffect(() => {
    if (!lineSvgRef.current || timelines.length === 0 || !showLines) return;
    const svg = d3.select(lineSvgRef.current);
    svg.selectAll('*').remove();
    const margin = { top: 20, right: 20, bottom: 40, left: 50 };
    const width = lineSvgRef.current.clientWidth - margin.left - margin.right;
    const lHeight = 200 - margin.top - margin.bottom;
    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);
    const xScale = d3.scaleLinear().domain(timeRange).range([0, width]);
    const allSizes = timelines.flatMap(tl => tl.snapshots.map(s => s.size));
    const yScale = d3.scaleLinear().domain([0, d3.max(allSizes) || 1]).range([lHeight, 0]);

    g.append('g').attr('transform', `translate(0,${lHeight})`)
      .call(d3.axisBottom(xScale).ticks(6).tickFormat(formatTime)).attr('font-size', '10px');
    g.append('g').call(d3.axisLeft(yScale).ticks(5)).attr('font-size', '10px');
    g.append('text').attr('x', width / 2).attr('y', lHeight + 35)
      .attr('text-anchor', 'middle').attr('font-size', '11px').attr('fill', '#6b7280').text('Zaman');

    const lineGen = d3.line().x(d => d.x).y(d => d.y).curve(d3.curveMonotoneX);
    timelines.forEach((tl, i) => {
      const pts = tl.snapshots.map(s => ({ x: xScale((s.window_start + s.window_end) / 2), y: yScale(s.size) }));
      g.append('path').datum(pts).attr('fill', 'none')
        .attr('stroke', COLORS[i % COLORS.length]).attr('stroke-width', 2).attr('d', lineGen);
    });
  }, [timelines, timeRange, showLines]);

  if (!data || timelines.length === 0) {
    return <div style={{ height }} className="flex items-center justify-center bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-400">Trend verisi yok</div>;
  }

  return (
    <div>
      <div className="flex gap-4 mb-4 flex-wrap items-center text-xs text-gray-500">
        <span><strong className="text-gray-900">{timelines.length}</strong> klik zamansali</span>
        <span>{formatTime(timeRange[0])} &mdash; {formatTime(timeRange[1])}</span>
        <span><strong className="text-gray-900">{windowEdges.length}</strong> pencere</span>
        <label className="flex items-center gap-1.5 cursor-pointer hover:text-gray-700">
          <input type="checkbox" checked={showLines} onChange={e => setShowLines(e.target.checked)} className="w-3 h-3" />
          Boyut egrisi
        </label>
      </div>
      <div className="border border-gray-200 rounded-lg overflow-hidden bg-white">
        <svg ref={svgRef} width="100%" height={height} className="block" />
      </div>
      {showLines && (
        <div className="border border-gray-200 rounded-lg overflow-hidden bg-white mt-3">
          <svg ref={lineSvgRef} width="100%" height={200} className="block" />
        </div>
      )}
      <div className="mt-4">
        <div className="text-sm font-medium text-gray-900 mb-3">Klik Detaylari</div>
        <div className="flex flex-col gap-1.5">
          {timelines.map((tl, i) => (
            <div key={tl.id} className="border border-gray-200 rounded-lg p-3 bg-white text-sm"
              style={{ borderLeft: `3px solid ${COLORS[i % COLORS.length]}` }}>
              <div className="flex justify-between mb-1.5">
                <strong>{tl.label}</strong>
                <span className="text-gray-400 text-xs">
                  {formatTime(tl.birth)} &mdash; {tl.death ? formatTime(tl.death) : 'devam'}
                  {' | '}max {tl.max_size}
                </span>
              </div>
              <div className="flex gap-1 flex-wrap">
                {tl.snapshots.map((s, j) => (
                  <span key={j} className="px-1.5 py-0.5 bg-gray-100 rounded text-xs text-gray-600"
                    title={s.members.join(', ')}>
                    w{s.window} ({s.size})
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
