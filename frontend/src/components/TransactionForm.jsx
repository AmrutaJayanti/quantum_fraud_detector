import React, { useState, useEffect } from "react";
import FraudResultCard from "./FraudResultCard";
import { createOrUpdateTransaction, getTransaction } from "../services/api";

export default function TransactionForm({ onSaved, existingTransaction }) {
  const isEdit = !!existingTransaction;

  const [txId, setTxId] = useState("");
  const [form, setForm] = useState({
    card_id: "",
    device_id: "",
    merchant_id: "",
    amount: 0,
    timestamp: "",
    merchant_category: "other",
    is_high_risk_merchant: 0,
    location_distance_km: 0
  });
  const [fraudResult, setFraudResult] = useState(null);

  useEffect(() => {
    if (existingTransaction) {
      setTxId(existingTransaction.tx_id);
      setForm({
        ...existingTransaction,
        timestamp: existingTransaction.timestamp?.slice(0, 16)
      });
    }
  }, [existingTransaction]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const saved = await createOrUpdateTransaction({
      ...form,
      tx_id: txId || undefined,
      amount: parseFloat(form.amount),
      is_high_risk_merchant: parseInt(form.is_high_risk_merchant),
      location_distance_km: parseFloat(form.location_distance_km)
    });

    if (!isEdit) setFraudResult(saved);

    onSaved?.(saved);
  };

  return (
    <div className="p-4 bg-white shadow rounded mb-4">
      <h2 className="text-xl font-bold mb-4">
        {isEdit ? "Edit Transaction" : "New Transaction"}
      </h2>

      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {!isEdit && (
          <div>
            <label>Transaction ID</label>
            <input
              type="text"
              value={txId}
              onChange={e => setTxId(e.target.value)}
              placeholder="Existing or leave blank"
              className="border rounded p-2 w-full"
            />
          </div>
        )}

        {["card_id","device_id","merchant_id"].map(name => (
          <div key={name}>
            <label>{name.replace("_", " ").toUpperCase()}</label>
            <input
              name={name}
              value={form[name]}
              onChange={handleChange}
              required
              className="border rounded p-2 w-full"
            />
          </div>
        ))}

        <div>
          <label>Amount</label>
          <input type="number" name="amount" value={form.amount}
            onChange={handleChange} className="border rounded p-2 w-full" />
        </div>

        <div>
          <label>Timestamp</label>
          <input type="datetime-local" name="timestamp" value={form.timestamp}
            onChange={handleChange} className="border rounded p-2 w-full" />
        </div>

        <div>
          <label>Merchant Category</label>
          <select name="merchant_category" value={form.merchant_category}
            onChange={handleChange} className="border rounded p-2 w-full">
            {["entertainment","electronics","fashion","food","grocery","travel","health","other"]
              .map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>

        <div>
          <label>High Risk Merchant?</label>
          <select name="is_high_risk_merchant" value={form.is_high_risk_merchant}
            onChange={handleChange} className="border rounded p-2 w-full">
            <option value={0}>No</option>
            <option value={1}>Yes</option>
          </select>
        </div>

        <div>
          <label>Location Distance (km)</label>
          <input type="number" step="0.01" name="location_distance_km"
            value={form.location_distance_km}
            onChange={handleChange} className="border rounded p-2 w-full" />
        </div>

        <div className="md:col-span-2">
          <button className="bg-blue-600 text-white px-4 py-2 rounded">
            {isEdit ? "Update" : "Submit"}
          </button>
        </div>
      </form>

      {!isEdit && fraudResult && <FraudResultCard result={fraudResult} />}
    </div>
  );
}
