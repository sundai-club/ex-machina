import { useRouter } from 'next/router'
import { useEffect, useState } from 'react'
import styles from '@/styles/Summary.module.css'

export default function Summary() {
  const router = useRouter()
  const [gameData, setGameData] = useState(null)

  useEffect(() => {
    if (router.query.gameState) {
      setGameData(JSON.parse(router.query.gameState))
    }
  }, [router.query])

  if (!gameData) return <div>Loading...</div>

  return (
    <div className={styles.summaryContainer}>
      <h1>Game Summary</h1>
      
      <div className={styles.finalScores}>
        <h2>Final Scores</h2>
        <p>Your Score: {gameData.userScore}</p>
        <p>AI Score: {gameData.llmScore}</p>
      </div>

      <div className={styles.statistics}>
        <h2>Game Statistics</h2>
        <p>Total Rounds Played: {gameData.history.length}</p>
        <p>Times You Split: {
          gameData.history.filter(round => round.userChoice === 'Split').length
        }</p>
        <p>Times You Stole: {
          gameData.history.filter(round => round.userChoice === 'Steal').length
        }</p>
        <p>Times AI Split: {
          gameData.history.filter(round => round.llmChoice === 'Split').length
        }</p>
        <p>Times AI Stole: {
          gameData.history.filter(round => round.llmChoice === 'Steal').length
        }</p>
      </div>

      <button 
        className={styles.playAgain}
        onClick={() => router.push('/')}
      >
        Play Again
      </button>
    </div>
  )
}