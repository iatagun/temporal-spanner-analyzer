'use client';

import { useRef, useEffect, useMemo, useState } from 'react';
import * as d3 from 'd3';

function formatTime(t) {
  if (t == null) return '';
  if (t > 1e10) return new Date(t * 1000).toISOString().slice(0, 7);
  return Number(t).toFixed(2);
}

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

    const margin = { top: 20, right: 20, bottom: 40, left: 100 };
    const width = svgRef.current.clientWidth - margin.left - margin.right;
    const gHeight = height - margin.top - margin.bottom;

    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

    const xScale = d3.scaleLinear()
      .domain(timeRange)
      .range([0, width]);

    const yScale = d3.scaleBand()
      .domain(timelines.map(t => t.label))
      .range([0, gHeight])
      .padding(0.15);

    const maxSize = d3.max(timelines, t => t.max_size) || 1;
    const colorScale = d3.scaleSequential(d3.interpolateBlues)
      .domain([1, maxSize]);

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
      .attr('fill', '#666')
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
          .attr('stroke', '#2c5f8a')
          .attr('stroke-width', 0.5)
          .attr('rx', 2)
          .attr('ry', 2)
          .append('title')
          .text(`${tl.label}\nSize: ${s.size}\nMembers: ${s.members.join(', ')}\n${formatTime(s.window_start)} - ${formatTime(s.window_end)}`);
      });
    });

    if (maxSize > 1) {
      const legendW = 120;
      const legendH = 12;
      const legendX = width - legendW - 10;
      const legendY = -12;

      const defs = svg.append('defs');
      const gradId = 'size-grad';
      defs.append('linearGradient')
        .attr('id', gradId)
        .attr('x1', '0%').attr('y1', '0%')
        .attr('x2', '100%').attr('y2', '0%')
        .selectAll('stop')
        .data(d3.range(0, 1.01, 0.1))
        .enter()
        .append('stop')
        .attr('offset', d => `${d * 100}%`)
        .attr('stop-color', d => colorScale(d * maxSize));

      svg.append('rect')
        .attr('x', legendX)
        .attr('y', legendY)
        .attr('width', legendW)
        .attr('height', legendH)
        .style('fill', `url(#${gradId})`);

      svg.append('text')
        .attr('x', legendX)
        .attr('y', legendY - 3)
        .attr('font-size', '9px')
        .attr('fill', '#666')
        .text('Clique Size');
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

    const xScale = d3.scaleLinear()
      .domain(timeRange)
      .range([0, width]);

    const allSizes = timelines.flatMap(tl => tl.snapshots.map(s => s.size));
    const yScale = d3.scaleLinear()
      .domain([0, d3.max(allSizes) || 1])
      .range([lHeight, 0]);

    g.append('g')
      .attr('transform', `translate(0,${lHeight})`)
      .call(d3.axisBottom(xScale).ticks(6).tickFormat(d => formatTime(d)))
      .attr('font-size', '10px');

    g.append('g')
      .call(d3.axisLeft(yScale).ticks(5))
      .attr('font-size', '10px');

    g.append('text')
      .attr('x', width / 2)
      .attr('y', lHeight + 35)
      .attr('text-anchor', 'middle')
      .attr('font-size', '11px')
      .attr('fill', '#666')
      .text('Time');

    g.append('text')
      .attr('x', -35)
      .attr('y', 10)
      .attr('text-anchor', 'middle')
      .attr('font-size', '11px')
      .attr('fill', '#666')
      .attr('transform', 'rotate(-90)')
      .text('Members');

    const lineGen = d3.line()
      .x(d => d.x)
      .y(d => d.y)
      .curve(d3.curveMonotoneX);

    const colors = ['#e74c3c','#2ecc71','#f39c12','#3498db','#9b59b6','#1abc9c','#e67e22','#34495e','#16a085','#c0392b','#27ae60','#8e44ad','#d35400','#2980b9','#2c3e50'];

    timelines.forEach((tl, i) => {
      const pts = tl.snapshots.map(s => ({
        x: xScale((s.window_start + s.window_end) / 2),
        y: yScale(s.size),
      }));

      g.append('path')
        .datum(pts)
        .attr('fill', 'none')
        .attr('stroke', colors[i % colors.length])
        .attr('stroke-width', 2)
        .attr('d', lineGen);

      pts.forEach(p => {
        g.append('circle')
          .attr('cx', p.x)
          .attr('cy', p.y)
          .attr('r', 3)
          .attr('fill', colors[i % colors.length])
          .append('title')
          .text(`${tl.label}: ${tl.snapshots[pts.indexOf(p)].size} members`);
      });
    });

  }, [timelines, timeRange, showLines]);

  if (!data || timelines.length === 0) {
    return (
      <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f5f5f5', borderRadius: 8, color: '#999' }}>
        No trend data — upload a CSV and compute trends first
      </div>
    );
  }

  return (
    <div>
      <div style={{ display: 'flex', gap: 16, marginBottom: 12, flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ fontSize: 13, color: '#555' }}>
          <strong>{timelines.length}</strong> clique timelines
        </div>
        <div style={{ fontSize: 13, color: '#555' }}>
          Time: <strong>{formatTime(timeRange[0])}</strong> — <strong>{formatTime(timeRange[1])}</strong>
        </div>
        <div style={{ fontSize: 13, color: '#555' }}>
          Windows: <strong>{windowEdges.length}</strong>
        </div>
        <label htmlFor="size-trends" style={{ fontSize: 12, color: '#555', display: 'flex', alignItems: 'center', gap: 4, cursor: 'pointer' }}>
          <input id="size-trends" name="size-trends" type="checkbox" checked={showLines} onChange={e => setShowLines(e.target.checked)} />
          Size trends
        </label>
      </div>

      <div style={{
        border: '1px solid #ddd', borderRadius: 8, overflow: 'hidden',
        background: '#fff',
      }}>
        <svg ref={svgRef} width="100%" height={height} style={{ display: 'block' }} />
      </div>

      {showLines && (
        <div style={{
          border: '1px solid #ddd', borderRadius: 8, overflow: 'hidden',
          background: '#fff', marginTop: 12,
        }}>
          <svg ref={lineSvgRef} width="100%" height={200} style={{ display: 'block' }} />
        </div>
      )}

      <div style={{ marginTop: 16 }}>
        <div style={{ fontWeight: 600, fontSize: 14, color: '#333', marginBottom: 8 }}>Clique Details</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          {timelines.map((tl, i) => {
            const colors = ['#e74c3c','#2ecc71','#f39c12','#3498db','#9b59b6','#1abc9c','#e67e22','#34495e','#16a085','#c0392b','#27ae60','#8e44ad','#d35400','#2980b9','#2c3e50'];
            return (
            <div key={tl.id} style={{
              padding: '10px 14px', border: '1px solid #eee', borderRadius: 6,
              background: '#fafafa', fontSize: 13,
              borderLeft: `3px solid ${colors[i % colors.length]}`,
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                <strong>{tl.label}</strong>
                <span style={{ color: '#666' }}>
                  {formatTime(tl.birth)} — {tl.death ? formatTime(tl.death) : 'present'}
                  {' | '}max {tl.max_size} members
                </span>
              </div>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {tl.snapshots.map((s, j) => (
                  <span key={j} style={{
                    padding: '2px 8px', borderRadius: 4, fontSize: 11,
                    background: '#e8f0fe', color: '#1a56db',
                  }} title={s.members.join(', ')}>
                    w{s.window} ({s.size}): [{s.members.slice(0, 3).join(', ')}{s.members.length > 3 ? '…' : ''}]
                  </span>
                ))}
              </div>
            </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
