import React, { useState, useEffect } from "react";
import TransactionsTable from "../components/TransactionsTable";
import TransactionForm from "../components/TransactionForm";
import EditTransactionModal from "../components/EditTransactionModal";
import DeleteConfirmModal from "../components/DeleteConfirmModal";
import CsvUpload from "../components/CsvUpload";
import GraphCanvas from "../components/GraphCanvas";
import { getTransactions, getGraphByTx, deleteTransaction } from "../services/api";
import useRealtimeTransactions from "../hooks/useRealtimeTransactions";
import LiveTransactionChart from "../components/LiveTransactionChart";

export default function Dashboard() {
  const [transactions, setTransactions] = useState([]);
  const [page, setPage] = useState(1);
  const [selectedGraph, setSelectedGraph] = useState(null);
  const [editingTx, setEditingTx] = useState(null);
  const [deletingTx, setDeletingTx] = useState(null);

  const fetchTransactions = async () => {
    const data = await getTransactions((page - 1) * 5, 5);
    setTransactions(data);
  };

  useEffect(() => { fetchTransactions(); }, [page]);

  useRealtimeTransactions((msg) => {
    console.log("WS message:", msg);
    if (msg.type === "NEW_TRANSACTION") {
      setTransactions(prev => {
        if (prev.find(t => t.tx_id === msg.data.tx_id)) return prev;
        return [msg.data, ...prev];
      });
    }
  });

  const handleSelectGraph = async (tx_id) => {
    try {
      const graph = await getGraphByTx(tx_id);

      if (!graph || !graph.nodes || graph.nodes.length === 0) {
        setSelectedGraph({ empty: true });
      } else {
        setSelectedGraph(graph);
      }
    } catch (err) {
      console.error("Graph fetch failed:", err);
      setSelectedGraph({ empty: true });
    }
  };

  //Confirms delete
  const handleDeleteConfirm = async (tx_id) => {
    await deleteTransaction(tx_id);
    setDeletingTx(null);
    fetchTransactions();
  };

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-3xl font-extrabold text-gray-800">
          🚨 Real-Time Fraud Detection
        </h1>
        <span className="inline-flex items-center px-3 py-1 bg-green-100 text-green-800 text-sm font-medium rounded-full animate-pulse">
          Live
        </span>
      </div>

      <div className="flex gap-6 mt-2 md:mt-0">
        <p className="text-gray-600 font-semibold">
          Total Transactions: <span className="text-gray-900">{transactions.length}</span>
        </p>
        <p className="text-gray-600 font-semibold">
          Fraud Transactions:{" "}
          <span className="text-red-600">
            {transactions.filter(t => t.is_fraud || t.label).length}
          </span>
        </p>
      </div>

      <LiveTransactionChart transactions={transactions} />

      <TransactionForm onSaved={fetchTransactions} />

      <CsvUpload onBatchPredicted={setTransactions} />

      <TransactionsTable
        transactions={transactions}
        fetchTransactions={fetchTransactions}
        page={page}
        setPage={setPage}
        onSelectTransaction={handleSelectGraph}
        onEditTransaction={setEditingTx}
        onDeleteTransaction={setDeletingTx}
      />

      {selectedGraph && (
        <div className="bg-white p-4 rounded shadow">
          <h2 className="text-xl font-semibold mb-2">
            Transaction Relationship Graph
          </h2>

          {selectedGraph.empty ? (
            <div className="h-[400px] flex items-center justify-center text-gray-500 border rounded">
              No Graph Available for this Transaction
            </div>
          ) : (
            <GraphCanvas graph={selectedGraph} />
          )}
        </div>
      )}


      <EditTransactionModal
        tx={editingTx}
        onClose={() => setEditingTx(null)}
        onUpdated={fetchTransactions}
      />

      <DeleteConfirmModal
        tx={deletingTx}
        onCancel={() => setDeletingTx(null)}
        onConfirm={handleDeleteConfirm}
      />
    </div>
  );
}
