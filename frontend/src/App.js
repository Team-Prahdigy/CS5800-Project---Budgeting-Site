// src/App.js
import React, { useEffect, useState } from 'react';

function App() {
  const [message, setMessage] = useState('Loading...');

  useEffect(() => {
    fetch('http://127.0.0.1:5000/api/hello')
      .then(res => res.json())
      .then(data => setMessage(data.message))
      .catch(err => {
        console.error(err);
        setMessage('Error loading message');
      });
  }, []);

  return (
    <div style={{ textAlign: 'center', marginTop: '3rem' }}>
      <h1>{message}</h1>
    </div>
  );
}

export default App;
