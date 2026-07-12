'use client';

import { useRef, useEffect, useMemo, useState } from 'react';
import * as d3 from 'd3';
import { formatTime } from '../lib/utils';
import { getCliqueColor, prefersDark, CLIQUE_PALETTE } from '../lib/palette';
import TruncatedWarning from './TruncatedWarning';

export default function TrendsView({ data, height = 300 }) {
  const svgRef = useRef(null);
  const lineSvgRef = useRef(null);
  const [showLines, setShowLines] = useState(true);

  const timelines = useMemo(() => data?.timelines || [], [data]);
  const timeRange = useMemo(() => data?.time_range || [0, 1], [data]);
  const windowEdges = useMemo(() => data?.window_edges || [], [data]);

  useEffect(() => {
    if (!svgRef.current || timelines.length === 0) return;
    const isDark = prefersDark();
    const axisColor = isDark ? '#9ca3af' : '#6b7280';
    const barStroke = isDark ? '#60a5fa' : '#1e40af';

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();
    const margin = { top: 20, right: 20, bottom: 40, left: 120 };
    const width = svgRef.current.clientWidth - margin.left - margin.right;
    const gHeight = height - margin.top - margin.bottom;
    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);
    const xScale = d3.scaleLinear().domain(timeRange).range([0, Math.max(width, 1)]);
    const yScale = d3.scaleBand().domain(timelines.map(t => t.label)).range([0, gHeight]).padding(0.15);
    const maxSize = d3.max(timelines, t => t.max_size) || 1;
    const colorScale = d3.scaleSequential(d3.interpolateBlues).domain([1, maxSize]);

    const xAxis = g.append('g').attr('transform', `translate(0,${gHeight})`)
      .call(d3.axisBottom(xScale).ticks(8).tickFormat(d => formatTime(d))).attr('font-size', '10px');
    const yAxis = g.append('g').call(d3.axisLeft(yScale)).attr('font-size', '10px');
    [xAxis, yAxis].forEach(axis => {
      axis.selectAll('text').attr('fill', axisColor);
      axis.selectAll('.domain, line').attr('stroke', axisColor);
    });
    g.append('text').attr('x', Math.max(width, 1) / 2).attr('y', gHeight + 35)
      .attr('text-anchor', 'middle').attr('font-size', '11px').attr('fill', axisColor).text('Zaman');

    timelines.forEach(tl => {
      tl.snapshots.forEach(s => {
        const y = yScale(tl.label);
        if (y == null) return;
        g.append('rect').attr('x', xScale(s.window_start)).attr('y', y)
          .attr('width', Math.max(xScale(s.window_end) - xScale(s.window_start), 2))
          .attr('height', yScale.bandwidth()).attr('fill', colorScale(s.size))
          .attr('stroke', barStroke).attr('stroke-width', 0.5).attr('rx', 1)
          .append('title').text(`${tl.label}\n${s.size} üye\n${s.members.slice(0,5).join(', ')}`);
      });
    });
  }, [timelines, timeRange, height]);

  useEffect(() => {
    if (!lineSvgRef.current || timelines.length === 0 || !showLines) return;
    const isDark = prefersDark();
    const axisColor = isDark ? '#9ca3af' : '#6b7280';

    const svg = d3.select(lineSvgRef.current);
    svg.selectAll('*').remove();

    const margin = { top: 20, right: 20, bottom: 40, left: 50 };
    const width = lineSvgRef.current.clientWidth - margin.left - margin.right;
    const lHeight = 200 - margin.top - margin.bottom;

    const g = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

    const xScale = d3.scaleLinear().domain(timeRange).range([0, Math.max(width, 1)]);
    const allSizes = timelines.flatMap(tl => tl.snapshots.map(s => s.size));
    const maxSz = d3.max(allSizes) || 1;
    const yScale = d3.scaleLinear().domain([0, maxSz]).range([Math.max(lHeight, 1), 0]);

    const xAxis = g.append('g').attr('transform', `translate(0,${lHeight})`)
      .call(d3.axisBottom(xScale).ticks(6).tickFormat(d => formatTime(d))).attr('font-size', '10px');
    const yAxis = g.append('g').call(d3.axisLeft(yScale).ticks(5)).attr('font-size', '10px');
    [xAxis, yAxis].forEach(axis => {
      axis.selectAll('text').attr('fill', axisColor);
      axis.selectAll('.domain, line').attr('stroke', axisColor);
    });

    g.append('text').attr('x', Math.max(width, 1) / 2).attr('y', lHeight + 35)
      .attr('text-anchor', 'middle').attr('font-size', '11px').attr('fill', axisColor).text('Zaman');

    const lineGen = d3.line().x(d => d.x).y(d => d.y).curve(d3.curveMonotoneX);

    timelines.forEach((tl, i) => {
      const pts = tl.snapshots.map(s => ({
        x: xScale((s.window_start + s.window_end) / 2),
        y: yScale(s.size),
      }));
      const color = getCliqueColor(i);
      if (pts.length >= 2) {
        g.append('path').datum(pts).attr('fill', 'none')
          .attr('stroke', color).attr('stroke-width', 2).attr('d', lineGen);
      }
      pts.forEach((p, j) => {
        g.append('circle').attr('cx', p.x).attr('cy', p.y).attr('r', 3)
          .attr('fill', color)
          .append('title').text(`${tl.label}: ${tl.snapshots[j].size} members`);
      });
    });
  }, [timelines, timeRange, showLines]);

  if (!data || timelines.length === 0) {
    return <div style={{ height }} className="flex items-center justify-center bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-lg text-sm text-gray-400 dark:text-gray-500">Trend verisi yok</div>;
  }

  return (
    <div>
      {data.truncated && <TruncatedWarning />}
      <div className="flex gap-4 mb-4 flex-wrap items-center text-xs text-gray-500 dark:text-gray-400">
        <span><strong className="text-gray-900 dark:text-gray-100">{timelines.length}</strong> klik zamansalı</span>
        <span>{formatTime(timeRange[0])} &mdash; {formatTime(timeRange[1])}</span>
        <span><strong className="text-gray-900 dark:text-gray-100">{windowEdges.length}</strong> pencere</span>
        <label className="flex items-center gap-1.5 cursor-pointer hover:text-gray-700 dark:hover:text-gray-300">
          <input type="checkbox" checked={showLines} onChange={e => setShowLines(e.target.checked)} className="w-3 h-3" />
          Boyut eğrisi
        </label>
      </div>
      <div className="border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden bg-white dark:bg-gray-950">
        <svg ref={svgRef} width="100%" height={height} className="block" />
      </div>
      {showLines && (
        <div className="mt-3">
          <div className="flex flex-wrap gap-x-3 gap-y-1.5 mb-2 text-xs text-gray-600 dark:text-gray-400">
            {timelines.slice(0, CLIQUE_PALETTE.length).map((tl, i) => (
              <span key={tl.id} className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: getCliqueColor(i) }} />
                {tl.label}
              </span>
            ))}
            {timelines.length > CLIQUE_PALETTE.length && (
              <span className="flex items-center gap-1.5 text-gray-400 dark:text-gray-500">
                <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: getCliqueColor(CLIQUE_PALETTE.length) }} />
                Diğer ({timelines.length - CLIQUE_PALETTE.length})
              </span>
            )}
          </div>
          <div className="border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden bg-white dark:bg-gray-950">
            <svg ref={lineSvgRef} width="100%" height={200} className="block" />
          </div>
        </div>
      )}
      <div className="mt-4">
        <div className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">Klik Detayları</div>
        <div className="flex flex-col gap-1.5">
          {timelines.map((tl, i) => (
            <div key={tl.id} className="border border-gray-200 dark:border-gray-800 rounded-lg p-3 bg-white dark:bg-gray-950 text-sm dark:text-gray-200"
              style={{ borderLeft: `3px solid ${getCliqueColor(i)}` }}>
              <div className="flex justify-between mb-1.5">
                <strong>{tl.label}</strong>
                <span className="text-gray-400 dark:text-gray-500 text-xs">
                  {formatTime(tl.birth)} &mdash; {tl.death ? formatTime(tl.death) : 'devam'}
                  {' | '}max {tl.max_size}
                </span>
              </div>
              <div className="flex gap-1 flex-wrap">
                {tl.snapshots.map((s, j) => (
                  <span key={j} className="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-xs text-gray-600 dark:text-gray-400"
                    title={s.members.join(', ')}>
                    w{s.window} ({s.size}): [{s.members.slice(0, 4).join(', ')}{s.members.length > 4 ? '…' : ''}]
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
