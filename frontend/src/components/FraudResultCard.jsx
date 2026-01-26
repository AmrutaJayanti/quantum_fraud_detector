export default function FraudResultCard({ result }) {
  if (!result) return null;
  const getRiskColor = (score) => {
  if (score > 70) return "bg-red-500 text-white";    
  if (score > 40) return "bg-yellow-400 text-black"; 
  return "bg-green-500 text-white";                  
};

  return (
    <div className="mt-6 rounded-xl border p-4 bg-slate-50">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-500">Prediction Result</p>
          <p className="text-lg font-semibold">
            {result.is_fraud ? "Fraud Detected" : "Legitimate Transaction"}
          </p>
        </div>

        <span
          className={`px-4 py-2 rounded-full text-sm font-semibold ${
            result.is_fraud ? "bg-red-500 text-white" : "bg-green-500 text-white"
          }`}
        >
          {result.is_fraud ? "Fraud" : "Safe"}
        </span>
      </div>

      {result.risk_score !== undefined && (
        <p className={`px-4 py-2 rounded-full text-sm font-semibold ${getRiskColor(result.risk_score)}`}>
          Risk Score: <b>{result.risk_score.toFixed(2)}%</b>
        </p>
      )}
    </div>
  );
}
