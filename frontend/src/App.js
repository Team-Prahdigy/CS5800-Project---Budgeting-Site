import React, { useEffect, useState } from "react";
import axios from "axios";

const BASE_URL =
  process.env.NODE_ENV === "production"
    ? "" // In Render or production, same domain
    : "http://127.0.0.1:5000"; // Local development

function App() {
  const [transactions, setTransactions] = useState([]);
  const [type, setType] = useState("expense");
  const [category, setCategory] = useState("");
  const [amount, setAmount] = useState("");
  const [note, setNote] = useState("");

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [token, setToken] = useState(localStorage.getItem("token") || "");

  // Attach token to every request if logged in
  const api = axios.create({
    baseURL: BASE_URL,
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });

  const fetchTransactions = async () => {
    if (!token) return; // Don't fetch until logged in
    try {
      const res = await api.get("/api/transactions");
      setTransactions(res.data);
    } catch (err) {
      console.error(err.response?.data || err.message);
    }
  };

  const addTransaction = async () => {
    try {
      await api.post("/api/transactions", {
        type,
        category,
        amount,
        note,
      });
      setCategory("");
      setAmount("");
      setNote("");
      fetchTransactions();
    } catch (err) {
      console.error(err.response?.data || err.message);
    }
  };

  const deleteTransaction = async (id) => {
    try {
      await api.delete(`/api/transactions/${id}`);
      fetchTransactions();
    } catch (err) {
      console.error(err.response?.data || err.message);
    }
  };

  const handleAuth = async () => {
    try {
      const endpoint = isLoginMode ? "/api/login" : "/api/register";
      const res = await axios.post(BASE_URL + endpoint, { username, password });

      if (isLoginMode) {
        const jwtToken = res.data.token;
        localStorage.setItem("token", jwtToken);
        setToken(jwtToken);
        fetchTransactions();
      } else {
        alert("Registration successful. Please log in.");
        setIsLoginMode(true);
      }
    } catch (err) {
      alert(err.response?.data?.error || "Auth failed");
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken("");
    setTransactions([]);
  };

  useEffect(() => {
    fetchTransactions();
  }, [token]);

  // ---- UI ----
  if (!token) {
    return (
      <div style={{ padding: "2rem", fontFamily: "Arial" }}>
        <h1>{isLoginMode ? "Login" : "Register"}</h1>
        <input
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <br />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <br />
        <button onClick={handleAuth}>
          {isLoginMode ? "Login" : "Register"}
        </button>
        <p
          style={{ cursor: "pointer", color: "blue" }}
          onClick={() => setIsLoginMode(!isLoginMode)}
        >
          {isLoginMode
            ? "Don't have an account? Register"
            : "Already have an account? Login"}
        </p>
      </div>
    );
  }

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial" }}>
      <h1>Budget Tracker (Per User)</h1>
      <button onClick={logout}>Logout</button>

      <div style={{ marginBottom: "1rem", marginTop: "1rem" }}>
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
      {transactions.length === 0 ? (
        <p>No transactions yet.</p>
      ) : (
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
      )}
    </div>
  );
}

export default App;
