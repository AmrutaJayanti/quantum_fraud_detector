import React from "react";

export default function TransactionsTable({
  transactions,
  fetchTransactions,
  page,
  setPage,
  onSelectTransaction,
  onEditTransaction,
  onDeleteTransaction
}) {

  return (
    <div className="bg-white p-4 rounded shadow">
      <table className="min-w-full border">
        <thead className="bg-gray-100">
          <tr>
            <th className="px-4 py-2 border">Tx ID</th>
            <th className="px-4 py-2 border">Card</th>
            <th className="px-4 py-2 border">Device</th>
            <th className="px-4 py-2 border">Merchant</th>
            <th className="px-4 py-2 border">Amount</th>
            <th className="px-4 py-2 border">Category</th>
            <th className="px-4 py-2 border">High Risk</th>
            <th className="px-4 py-2 border">Fraud</th>
            <th className="px-4 py-2 border">Graph</th>
            <th className="px-4 py-2 border">Actions</th>
          </tr>
        </thead>

        <tbody>
          {transactions.map(tx => (
            <tr key={tx.tx_id} className="text-center">
              <td className="border px-2 py-1">{tx.tx_id}</td>
              <td className="border px-2 py-1">{tx.card_id}</td>
              <td className="border px-2 py-1">{tx.device_id}</td>
              <td className="border px-2 py-1">{tx.merchant_id}</td>
              <td className="border px-2 py-1">{tx.amount.toFixed(2)}</td>
              <td className="border px-2 py-1">{tx.merchant_category}</td>
              <td className="border px-2 py-1">{tx.is_high_risk_merchant ? "Yes" : "No"}</td>

              <td className="border px-2 py-1">
                {(tx.label || tx.is_fraud) ? "Yes" : "No"}
              </td>

              <td className="border px-2 py-1">
                <button
                  onClick={() => onSelectTransaction(tx.tx_id)}
                  className="bg-green-500 text-white px-2 py-1 rounded"
                >
                  View
                </button>
              </td>

              <td className="border px-2 py-1 space-x-1">
                <button
                  onClick={() => onEditTransaction(tx)}
                  className="bg-blue-500 text-white px-2 py-1 rounded"
                >
                  Edit
                </button>

                <button
                  onClick={() => onDeleteTransaction(tx)}
                  className="bg-red-500 text-white px-2 py-1 rounded"
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="mt-2 flex justify-between">
        <button onClick={() => setPage(p => Math.max(1, p - 1))} className="px-2 py-1 border rounded">Prev</button>
        <span>Page {page}</span>
        <button onClick={() => setPage(p => p + 1)} className="px-2 py-1 border rounded">Next</button>
      </div>
    </div>
  );
}
