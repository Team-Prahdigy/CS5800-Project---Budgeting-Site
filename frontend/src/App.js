import React, { useEffect, useState } from "react";
import axios from "axios";

const API_URL =
  process.env.NODE_ENV === "production"
    ? "/api/transactions" // In Render or production
    : "http://127.0.0.1:5000/api/transactions"; // Local development


function App() {
  const [transactions, setTransactions] = useState([]);
  const [type, setType] = useState("expense");
  const [category, setCategory] = useState("");
  const [amount, setAmount] = useState("");
  const [note, setNote] = useState("");

  const fetchTransactions = async () => {
    const res = await axios.get(API_URL);
    setTransactions(res.data);
  };

  const addTransaction = async () => {
    await axios.post(API_URL, {
      type,
      category,
      amount,
      note,
    });
    setCategory("");
    setAmount("");
    setNote("");
    fetchTransactions();
  };

  const deleteTransaction = async (id) => {
    await axios.delete(${API_URL}/${id});
    fetchTransactions();
  };

  useEffect(() => {
    fetchTransactions();
  }, []);

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial" }}>
      <h1>Budget Tracker</h1>

      <div style={{ marginBottom: "1rem" }}>
        <select value={type} onChange={(e) => setType(e.target.value)}>
          <option value="expense">Expense</option>
          <option value="income">Income</option>
        </select>
        <input
          placeholder="Category"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        />
        <input
          placeholder="Amount"
          type="number"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
        />
        <input
          placeholder="Note (optional)"
          value={note}
          onChange={(e) => setNote(e.target.value)}
        />
        <button onClick={addTransaction}>Add</button>
      </div>

      <h3>Transactions</h3>
      <table border="1" cellPadding="8">
        <thead>
          <tr>
            <th>Type</th>
            <th>Category</th>
            <th>Amount</th>
            <th>Note</th>
            <th>Date</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((t) => (
            <tr key={t.id}>
              <td>{t.type}</td>
              <td>{t.category}</td>
              <td>${t.amount.toFixed(2)}</td>
              <td>{t.note}</td>
              <td>{new Date(t.date).toLocaleDateString()}</td>
              <td>
                <button onClick={() => deleteTransaction(t.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;