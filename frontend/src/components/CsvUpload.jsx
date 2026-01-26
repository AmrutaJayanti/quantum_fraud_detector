import React, { useState } from "react";
import { predictBatch } from "../services/api";

export default function CSVUpload({ onBatchPredicted }) {
  const [file, setFile] = useState(null);

  const handleUpload = async () => {
    if (!file) return;
    const results = await predictBatch(file);
    onBatchPredicted(results);
  };

  return (
    <div className="bg-white p-4 rounded shadow mb-4">
      <h2 className="text-xl font-semibold mb-2">Risk Scorer (CSV)</h2>
      <div className="flex items-center">
        <input type="file" accept=".csv" onChange={e => setFile(e.target.files[0])} className="border p-2 rounded"/>
        <button onClick={handleUpload} className="ml-2 bg-blue-500 text-white px-4 py-2 rounded">Upload</button>
      </div>
    </div>
  );
}
