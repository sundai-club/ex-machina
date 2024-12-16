import { useRouter } from 'next/router'
import styles from '../styles/Home.module.css'  // Changed this line

export default function Home() {
  const router = useRouter()

  return (
    <div className={styles.container}>
      <h1>Steal or Split</h1>
      <div className={styles.description}>
        <p>
          Welcome to Steal or Split! This game pits you against an AI in a battle
          of trust and strategy over 200 rounds.
        </p>
        <p>
          In each round, both players choose to either "Steal" or "Split" the prize:
          • If both SPLIT: Each player gets 5 points
          • If one STEALS and one SPLITS: The stealer gets 10 points
          • If both STEAL: Nobody gets points
        </p>
      </div>
      <button 
        className={styles.startButton}
        onClick={() => router.push('/game')}
      >
        Start Game
      </button>
    </div>
  )
}