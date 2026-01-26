import React, { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from "recharts";

export default function LiveTransactionChart({ transactions }) {
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    const data = transactions
      .slice(-20) 
      .map((tx) => ({
        tx_id: tx.tx_id,
        amount: tx.amount,
        time: new Date(tx.timestamp).toLocaleTimeString(),
        is_fraud: tx.is_fraud,
        risk_score: tx.risk_score
      }));
    setChartData(data);
  }, [transactions]);

  return (
    <div className="bg-white p-4 rounded shadow mt-4">
      <h2 className="text-xl font-semibold mb-2">Live Transaction Chart</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis />
          <Tooltip 
            formatter={(value, name, props) => {
              if(name === "amount") return [`$${value}`, "Amount"];
              if(name === "risk_score") return [`${value.toFixed(2)}%`, "Risk Score"];
              return [value, name];
            }}
          />
          <Line
            type="monotone"
            dataKey="amount"
            stroke="#1d4ed8"
            strokeWidth={2}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
          />
          <Line
            type="monotone"
            dataKey="risk_score"
            stroke="#f59e0b"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
