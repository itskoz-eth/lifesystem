import { useState, useEffect } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)
  const [values, setValues] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function fetchValues() {
      try {
        // The backend runs on port 8000, and the frontend on 5173 (or similar).
        // We need to specify the full URL to the backend API.
        // In a production setup, we'd configure a proxy or use environment variables.
        const response = await fetch('http://127.0.0.1:8000/api/v1/values/')
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        const data = await response.json()
        setValues(data)
      } catch (e) {
        setError(e.message)
        console.error("Failed to fetch values:", e)
      } finally {
        setLoading(false)
      }
    }

    fetchValues()
  }, []) // Empty dependency array means this effect runs once on mount

  return (
    <>
      <div>
        <a href="https://vitejs.dev" target="_blank" rel="noreferrer">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank" rel="noreferrer">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.jsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>

      <div className="values-section">
        <h2>My Values</h2>
        {loading && <p>Loading values...</p>}
        {error && <p style={{ color: 'red' }}>Error fetching values: {error}</p>}
        {!loading && !error && (
          <>
            {values.length > 0 ? (
              <ul>
                {values.map((value) => (
                  <li key={value.id}>
                    <strong>{value.name}</strong>: {value.description}
                  </li>
                ))}
              </ul>
            ) : (
              <p>No values found. You can add some via the API!</p>
            )}
          </>
        )}
      </div>
    </>
  )
}

export default App
