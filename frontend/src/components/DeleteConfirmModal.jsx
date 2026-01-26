export default function DeleteConfirmModal({ tx, onCancel, onConfirm }) {
  if (!tx) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-20 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-[420px] p-5 shadow-xl">
        
        <h2 className="text-xl font-bold text-red-600 mb-2">
          Confirm Deletion
        </h2>

        <p className="text-gray-700 mb-4">
          Are you sure you want to delete transaction
          <span className="font-semibold"> {tx.tx_id}</span>?
          <br />
          This action cannot be undone.
        </p>

        <div className="flex justify-end space-x-2">
          <button
            onClick={onCancel}
            className="px-4 py-2 rounded border hover:bg-gray-100"
          >
            Cancel
          </button>

          <button
            onClick={() => onConfirm(tx.tx_id)}
            className="px-4 py-2 rounded bg-red-600 text-white hover:bg-red-700"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}
