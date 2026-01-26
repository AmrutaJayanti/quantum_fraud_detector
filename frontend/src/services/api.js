const BASE_URL = "http://localhost:8000"; 

export async function getTransactions(skip = 0, limit = 10) {
  const res = await fetch(`${BASE_URL}/transactions?skip=${skip}&limit=${limit}`);
  return await res.json();
}

export async function getTransaction(tx_id) {
  const res = await fetch(`${BASE_URL}/transactions/${tx_id}`);
  return await res.json();
}

export async function createOrUpdateTransaction(tx) {
  if (tx.tx_id) {
    const res = await fetch(`${BASE_URL}/transactions/${tx.tx_id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(tx)
    });
    return await res.json();
  } else {
    const res = await fetch(`${BASE_URL}/transactions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(tx)
    });
    return await res.json();
  }
}

export async function deleteTransaction(tx_id) {
  const res = await fetch(`${BASE_URL}/transactions/${tx_id}`, {
    method: "DELETE"
  });
  return await res.json();
}

export async function getGraphByTx(tx_id) {
  const res = await fetch(`${BASE_URL}/graph/transaction/${tx_id}`);
  if (!res.ok) return null;
  return await res.json();
}

export async function predictTransaction(tx) {
  const res = await fetch(`${BASE_URL}/predict/single`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(tx)
  });
  return await res.json();
}

export async function predictBatch(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${BASE_URL}/predict/batch`, {
    method: "POST",
    body: formData
  });
  return await res.json();
}
