import { Configuration, OpenAIApi } from 'openai'

const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
})
const openai = new OpenAIApi(configuration)

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' })
  }

  const { userChoice, gameHistory, currentRound } = req.body

  try {
    const prompt = `
      You are playing a game of Steal or Split. Here's the current situation:
      
      Current round: ${currentRound}/200
      User's choice this round: ${userChoice}
      
      Previous rounds:
      ${gameHistory.map(round => `
        Round ${round.round}:
        User chose: ${round.userChoice}
        AI chose: ${round.llmChoice}
        Outcome: User +${round.userScore}, AI +${round.llmScore}
      `).join('\n')}
      
      Based on this information:
      1. Choose either "Steal" or "Split"
      2. Provide a brief explanation for your choice
      3. Make a prediction about the user's next move
      
      Respond in JSON format:
      {
        "llmChoice": "Steal/Split",
        "explanation": "your explanation",
        "prediction": "your prediction"
      }
    `

    const completion = await openai.createCompletion({
      model: "text-davinci-003",
      prompt,
      max_tokens: 150,
      temperature: 0.7,
    })

    const response = JSON.parse(completion.data.choices[0].text.trim())
    res.status(200).json(response)
  } catch (error) {
    console.error('Error:', error)
    res.status(500).json({ message: 'Error processing request' })
  }
}