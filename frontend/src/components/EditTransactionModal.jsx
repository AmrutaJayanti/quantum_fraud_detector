import TransactionForm from "./TransactionForm";

export default function EditTransactionModal({ tx, onClose, onUpdated }) {
  if (!tx) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-20 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-[650px] p-4 shadow-xl">
        <div className="flex justify-between mb-3">
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-red-600 font-bold text-lg"
          >
            ✕
          </button>
        </div>

        <TransactionForm
          existingTransaction={tx}
          onSaved={() => {
            onUpdated();
            onClose();
          }}
        />
      </div>
    </div>
  );
}
