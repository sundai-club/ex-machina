import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import { v4 as uuidv4 } from 'uuid'
import styles from '../styles/Game.module.css'

export default function Game() {
  const router = useRouter()
  const [mounted, setMounted] = useState(false)
  const [sessionId, setSessionId] = useState('')
  const [gameState, setGameState] = useState({
    round: 1,
    userScore: 0,
    llmScore: 0,
    history: [],
    chatHistory: []  // Added for chat functionality
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [chatInput, setChatInput] = useState('')  // Added for chat input

  // Initialize new session when component mounts
  useEffect(() => {
    setMounted(true)
    setSessionId(uuidv4())
    setGameState({
      round: 1,
      userScore: 0,
      llmScore: 0,
      history: [],
      chatHistory: []
    })
  }, [])

  // Check for game end
  useEffect(() => {
    if (gameState.round > 200) {
      router.push({
        pathname: '/summary',
        query: { gameState: JSON.stringify(gameState) }
      })
    }
  }, [gameState.round, router])

  const calculateScores = (userChoice, llmChoice) => {
    let userScoreAdd = 0
    let llmScoreAdd = 0
    
    if (userChoice === 'Split' && llmChoice === 'Split') {
      userScoreAdd = 5
      llmScoreAdd = 5
    } else if (userChoice === 'Steal' && llmChoice === 'Split') {
      userScoreAdd = 10
    } else if (userChoice === 'Split' && llmChoice === 'Steal') {
      llmScoreAdd = 10
    }
    
    return { userScoreAdd, llmScoreAdd }
  }

  const makeChoice = async (choice) => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await fetch('/api/llm-interact', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userChoice: choice,
          gameHistory: gameState.history,
          sessionId: sessionId,
          chatHistory: gameState.chatHistory  // Include chat history in the request
        })
      })

      if (!response.ok) {
        throw new Error('Failed to get AI response')
      }

      const aiResponse = await response.json()
      
      const { userScoreAdd, llmScoreAdd } = calculateScores(choice, aiResponse.llmChoice)

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

    } catch (err) {
      setError('Failed to get AI response. Please try again.')
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  // New function for handling chat
  const sendChatMessage = async (message) => {
    try {
      setLoading(true)
      
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          sessionId,
          gameHistory: gameState.history,
          chatHistory: gameState.chatHistory
        })
      })

      if (!response.ok) {
        throw new Error('Failed to send message')
      }

      const data = await response.json()

      setGameState(prev => ({
        ...prev,
        chatHistory: [...prev.chatHistory, 
          { role: 'user', content: message },
          { role: 'assistant', content: data.response }
        ]
      }))

      setChatInput('')
    } catch (err) {
      setError('Failed to send message')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const resetGame = () => {
    setSessionId(uuidv4())
    setGameState({
      round: 1,
      userScore: 0,
      llmScore: 0,
      history: [],
      chatHistory: []  // Reset chat history too
    })
  }

  if (!mounted) {
    return <div>Loading...</div>
  }

  return (
    <div className={styles.container}>
      <div className={styles.gameContainer}>
        <header className={styles.header}>
          <div>Round: {gameState.round}/200</div>
          <div>Your Score: {gameState.userScore}</div>
          <div>AI Score: {gameState.llmScore}</div>
          <button 
            onClick={resetGame}
            className={styles.resetButton}
          >
            New Game
          </button>
        </header>

        {error && <div className={styles.error}>{error}</div>}

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

        {/* Chat Interface */}
        <div className={styles.chatContainer}>
          <div className={styles.chatMessages}>
            {gameState.chatHistory.map((message, index) => (
              <div 
                key={index} 
                className={`${styles.chatMessage} ${
                  message.role === 'user' ? styles.userMessage : styles.aiMessage
                }`}
              >
                <strong>{message.role === 'user' ? 'You' : 'AI'}:</strong> {message.content}
              </div>
            ))}
          </div>
          
          <div className={styles.chatInput}>
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && chatInput.trim()) {
                  sendChatMessage(chatInput.trim())
                }
              }}
              placeholder="Type your message..."
              disabled={loading}
            />
            <button 
              onClick={() => chatInput.trim() && sendChatMessage(chatInput.trim())}
              disabled={loading || !chatInput.trim()}
              className={styles.chatButton}
            >
              Send
            </button>
          </div>
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
    </div>
  )
}