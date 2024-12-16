import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import styles from '../styles/Game.module.css'

// Simple AI logic
const getAIChoice = (history) => {
  // Simple strategy: Mostly split, occasionally steal
  const randomNum = Math.random()
  const choice = randomNum < 0.7 ? 'Split' : 'Steal'
  
  return {
    llmChoice: choice,
    explanation: choice === 'Split' 
      ? "I choose to split to build trust." 
      : "I decided to steal this time to mix up my strategy.",
    prediction: "The user might choose split next round."
  }
}

export default function Game() {
  const router = useRouter()
  const [gameState, setGameState] = useState({
    round: 1,
    userScore: 0,
    llmScore: 0,
    history: []
  })
  const [loading, setLoading] = useState(false)

  const makeChoice = async (choice) => {
    setLoading(true)
    
    // Get AI's response locally instead of from API
    const aiResponse = getAIChoice(gameState.history)
    
    // Calculate scores
    let userScoreAdd = 0
    let llmScoreAdd = 0
    
    if (choice === 'Split' && aiResponse.llmChoice === 'Split') {
      userScoreAdd = 5
      llmScoreAdd = 5
    } else if (choice === 'Steal' && aiResponse.llmChoice === 'Split') {
      userScoreAdd = 10
    } else if (choice === 'Split' && aiResponse.llmChoice === 'Steal') {
      llmScoreAdd = 10
    }

    setGameState(prev => ({
      ...prev,
      round: prev.round + 1,
      userScore: prev.userScore + userScoreAdd,
      llmScore: prev.llmScore + llmScoreAdd,
      history: [...prev.history, {
        round: prev.round,
        userChoice: choice,
        llmChoice: aiResponse.llmChoice,
        explanation: aiResponse.explanation,
        prediction: aiResponse.prediction,
        userScore: prev.userScore + userScoreAdd,
        llmScore: prev.llmScore + llmScoreAdd
      }]
    }))
    
    setLoading(false)
  }

  useEffect(() => {
    if (gameState.round > 200) {
      router.push({
        pathname: '/summary',
        query: { gameState: JSON.stringify(gameState) }
      })
    }
  }, [gameState.round])

  return (
    <div className={styles.gameContainer}>
      <header className={styles.header}>
        <div>Round: {gameState.round}/200</div>
        <div>Your Score: {gameState.userScore}</div>
        <div>AI Score: {gameState.llmScore}</div>
      </header>

      <div className={styles.gameControls}>
        <button 
          onClick={() => makeChoice('Split')}
          disabled={loading}
          className={styles.button}
        >
          Split
        </button>
        <button 
          onClick={() => makeChoice('Steal')}
          disabled={loading}
          className={styles.button}
        >
          Steal
        </button>
      </div>

      <div className={styles.chatWindow}>
        {gameState.history.slice(-3).map((round, index) => (
          <div key={index} className={styles.chatMessage}>
            <p>Round {round.round}:</p>
            <p>You chose: {round.userChoice}</p>
            <p>AI chose: {round.llmChoice}</p>
            <p>AI's explanation: {round.explanation}</p>
            <p>AI's prediction: {round.prediction}</p>
          </div>
        ))}
      </div>

      <div className={styles.gameLog}>
        <h3>Game History</h3>
        <div className={styles.logEntries}>
          {gameState.history.map((round, index) => (
            <div key={index} className={styles.logEntry}>
              Round {round.round}: You {round.userChoice}, AI {round.llmChoice}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}