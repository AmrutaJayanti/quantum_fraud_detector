import React from "react";
import ReactFlow, { MiniMap, Controls } from "reactflow";
import 'reactflow/dist/style.css';

export default function GraphCanvas({ graph }) {

   if (
    !graph ||
    !graph.nodes ||
    !graph.edges ||
    graph.nodes.length === 0 ||
    graph.edges.length === 0
  ) {
    return (
      <div className="h-[400px] flex items-center justify-center text-gray-500 border rounded">
        No Graph Available for this Transaction
      </div>
    );
  }
  const nodes = graph.nodes.map(n => ({
    id: n.id,
    data: { label: n.id + (n.is_fraud ? " (Fraud)" : "") },
    position: { x: Math.random() * 400, y: Math.random() * 400 },
    style: { background: n.is_fraud  ? "#f87171" : "#60a5fa", color: "white", padding: 5 }
  }));

  const edges = graph.edges.map(e => ({
    id: `${e.from}-${e.to}`,
    source: e.from,
    target: e.to,
    label: e.label,
    animated: true
  }));

  return <div style={{ height: 400 }}><ReactFlow nodes={nodes} edges={edges}><MiniMap /><Controls /></ReactFlow></div>;
}
