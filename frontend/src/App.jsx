import { useState } from 'react'
import Landing from './components/Landing'

export default function App() {
  const [started, setStarted] = useState(false)
  
  if (started) return <div style={{color:'white',padding:40}}>Chat coming soon!</div>
  return <Landing onEnter={() => setStarted(true)} />
}