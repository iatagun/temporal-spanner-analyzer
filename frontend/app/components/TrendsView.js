'use client';

import { useRef, useEffect, useMemo, useState } from 'react';
import * as d3 from 'd3';
import { formatTime } from '../lib/utils';

const COLORS = ['#ef4444','#22c55e','#f59e0b','#3b82f6','#8b5cf6','#06b6d4','#f97316','#6366f1','#14b8a6','#ec4899','#84cc16','#a855f7','#eab308','#3b82f6','#64748b'];

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
    const yScale = d3.scaleBand()
      .domain(timelines.map(t => t.label))
      .range([0, gHeight])
      .padding(0.15);

    const maxSize = d3.max(timelines, t => t.max_size) || 1;
    const colorScale = d3.scaleSequential(d3.interpolateBlues).domain([1, maxSize]);

    g.append('g')
      .attr('transform', `translate(0,${gHeight})`)
      .call(d3.axisBottom(xScale).ticks(8).tickFormat(d => formatTime(d)))
      .attr('font-size', '10px');

    g.append('g')
      .call(d3.axisLeft(yScale))
      .attr('font-size', '10px');

    g.append('text')
      .attr('x', width / 2)
      .attr('y', gHeight + 35)
      .attr('text-anchor', 'middle')
      .attr('font-size', '11px')
      .attr('fill', '#64748b')
      .text('Time');

    timelines.forEach(tl => {
      tl.snapshots.forEach(s => {
        const y = yScale(tl.label);
        if (y == null) return;
        const x1 = xScale(s.window_start);
        const x2 = xScale(s.window_end);
        const barWidth = Math.max(x2 - x1, 2);

        g.append('rect')
          .attr('x', x1)
          .attr('y', y)
          .attr('width', barWidth)
          .attr('height', yScale.bandwidth())
          .attr('fill', colorScale(s.size))
          .attr('stroke', '#1e40af')
          .attr('stroke-width', 0.5)
          .attr('rx', 2)
          .attr('ry', 2)
          .append('title')
          .text(`${tl.label}\nSize: ${s.size}\nMembers: ${s.members.join(', ')}\n${formatTime(s.window_start)} - ${formatTime(s.window_end)}`);
      });
    });

    if (maxSize > 1) {
      const legendW = 120; const legendH = 12;
      const legendX = width - legendW - 10; const legendY = -12;
      const defs = svg.append('defs');
      const gradId = 'size-grad';
      defs.append('linearGradient').attr('id', gradId)
        .attr('x1', '0%').attr('y1', '0%').attr('x2', '100%').attr('y2', '0%')
        .selectAll('stop').data(d3.range(0, 1.01, 0.1)).enter().append('stop')
        .attr('offset', d => `${d * 100}%`).attr('stop-color', d => colorScale(d * maxSize));

      svg.append('rect').attr('x', legendX).attr('y', legendY)
        .attr('width', legendW).attr('height', legendH).style('fill', `url(#${gradId})`);
      svg.append('text').attr('x', legendX).attr('y', legendY - 3)
        .attr('font-size', '9px').attr('fill', '#64748b').text('Clique Size');
    }
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
      .call(d3.axisBottom(xScale).ticks(6).tickFormat(d => formatTime(d)))
      .attr('font-size', '10px');

    g.append('g').call(d3.axisLeft(yScale).ticks(5)).attr('font-size', '10px');

    g.append('text').attr('x', width / 2).attr('y', lHeight + 35)
      .attr('text-anchor', 'middle').attr('font-size', '11px').attr('fill', '#64748b').text('Time');

    g.append('text').attr('x', -35).attr('y', 10)
      .attr('text-anchor', 'middle').attr('font-size', '11px').attr('fill', '#64748b')
      .attr('transform', 'rotate(-90)').text('Members');

    const lineGen = d3.line().x(d => d.x).y(d => d.y).curve(d3.curveMonotoneX);

    timelines.forEach((tl, i) => {
      const pts = tl.snapshots.map(s => ({
        x: xScale((s.window_start + s.window_end) / 2),
        y: yScale(s.size),
      }));

      g.append('path').datum(pts).attr('fill', 'none')
        .attr('stroke', COLORS[i % COLORS.length]).attr('stroke-width', 2).attr('d', lineGen);

      pts.forEach((p, j) => {
        g.append('circle').attr('cx', p.x).attr('cy', p.y).attr('r', 3)
          .attr('fill', COLORS[i % COLORS.length])
          .append('title').text(`${tl.label}: ${tl.snapshots[j].size} members`);
      });
    });
  }, [timelines, timeRange, showLines]);

  if (!data || timelines.length === 0) {
    return (
      <div style={{ height }} className="flex items-center justify-center bg-slate-50 rounded-xl text-text-muted text-sm">
        No trend data — upload a CSV and compute trends first
      </div>
    );
  }

  return (
    <div>
      <div className="flex gap-4 mb-4 flex-wrap items-center text-sm text-text-muted">
        <span><strong className="text-text">{timelines.length}</strong> clique timelines</span>
        <span>Time: <strong className="text-text">{formatTime(timeRange[0])}</strong> — <strong className="text-text">{formatTime(timeRange[1])}</strong></span>
        <span>Windows: <strong className="text-text">{windowEdges.length}</strong></span>
        <label className="flex items-center gap-2 cursor-pointer text-text hover:text-primary transition-colors">
          <input type="checkbox" checked={showLines} onChange={e => setShowLines(e.target.checked)}
            className="w-3.5 h-3.5 rounded border-border text-primary focus:ring-primary" />
          Size trends
        </label>
      </div>

      <div className="border border-border rounded-xl overflow-hidden bg-white shadow-sm">
        <svg ref={svgRef} width="100%" height={height} className="block" />
      </div>

      {showLines && (
        <div className="border border-border rounded-xl overflow-hidden bg-white shadow-sm mt-3">
          <svg ref={lineSvgRef} width="100%" height={200} className="block" />
        </div>
      )}

      <div className="mt-5">
        <div className="text-sm font-semibold text-text mb-3">Clique Details</div>
        <div className="flex flex-col gap-2">
          {timelines.map((tl, i) => (
            <div key={tl.id} className="p-3 border border-border rounded-lg bg-white hover:shadow-sm transition-shadow"
              style={{ borderLeft: `3px solid ${COLORS[i % COLORS.length]}` }}>
              <div className="flex justify-between mb-2 text-sm">
                <strong className="text-text">{tl.label}</strong>
                <span className="text-text-muted">
                  {formatTime(tl.birth)} — {tl.death ? formatTime(tl.death) : 'present'}
                  {' | '}max {tl.max_size} members
                </span>
              </div>
              <div className="flex gap-1.5 flex-wrap">
                {tl.snapshots.map((s, j) => (
                  <span key={j} className="px-2 py-1 rounded-md text-xs bg-primary/10 text-primary font-medium"
                    title={s.members.join(', ')}>
                    w{s.window} ({s.size}): [{s.members.slice(0, 3).join(', ')}{s.members.length > 3 ? '…' : ''}]
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
