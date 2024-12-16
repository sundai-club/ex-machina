import OpenAI from "openai";

// Store session histories (in memory - will reset when server restarts)
const sessionHistories = new Map();

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  const { userChoice, gameHistory, sessionId } = req.body;

  try {
    // Initialize OpenAI with xAI configuration
    const openai = new OpenAI({
      apiKey: process.env.X_API_KEY,
      baseURL: "https://api.x.ai/v1",
    });

    // Get or initialize session history
    let sessionHistory = sessionHistories.get(sessionId) || [];
    if (!sessionHistories.has(sessionId)) {
      sessionHistories.set(sessionId, sessionHistory);
    }

    // Format history text
    const historyText = gameHistory.map(round => 
      `Round ${round.round}: User chose ${round.userChoice}, AI chose ${round.llmChoice}`
    ).join('\n');

    // Create prompt
    const prompt = `You are playing Split or Steal game. Here's the game history:

${historyText}

The user has just chosen: ${userChoice}

Based on this information, choose either "Split" or "Steal" for your next move.
Provide a brief explanation for your choice and a prediction about the user's next move.
Format your response exactly like this:
Choice: Split
Explanation: I choose split because of the pattern of cooperation.
Prediction: The user will likely split next round.`;

    // Make API call using the OpenAI SDK
    const completion = await openai.chat.completions.create({
      model: "grok-beta",
      messages: [
        {
          role: "system",
          content: "You are playing a game of Split or Steal. Respond with Choice, Explanation, and Prediction."
        },
        {
          role: "user",
          content: prompt
        }
      ]
    });

    // Get the response text
    const responseText = completion.choices[0].message.content;
    
    // Parse the response
    let llmChoice = 'Split';  // default
    let explanation = '';
    let prediction = '';

    try {
      const lines = responseText.trim().split('\n');
      for (const line of lines) {
        if (line.toLowerCase().startsWith('choice:')) {
          llmChoice = line.split(':')[1].trim();
        } else if (line.toLowerCase().startsWith('explanation:')) {
          explanation = line.split(':')[1].trim();
        } else if (line.toLowerCase().startsWith('prediction:')) {
          prediction = line.split(':')[1].trim();
        }
      }

      // Validate choice
      llmChoice = llmChoice.toLowerCase().includes('steal') ? 'Steal' : 'Split';

      // Update session history
      sessionHistory.push({
        round: gameHistory.length + 1,
        userChoice,
        llmChoice,
        explanation,
        prediction
      });

    } catch (parseError) {
      console.error('Error parsing model response:', parseError);
      throw new Error('Failed to parse model response');
    }

    res.status(200).json({
      llmChoice,
      explanation: explanation || 'No explanation provided',
      prediction: prediction || 'No prediction made'
    });

  } catch (error) {
    console.error('Error:', error);
    res.status(200).json({
      llmChoice: 'Split',
      explanation: `Error occurred: ${error.message}. Defaulting to Split.`,
      prediction: 'Unable to make prediction due to error.'
    });
  }
}