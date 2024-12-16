import OpenAI from "openai";

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  const { message, gameHistory, chatHistory, sessionId } = req.body;

  try {
    const openai = new OpenAI({
      apiKey: process.env.X_API_KEY,
      baseURL: "https://api.x.ai/v1",
    });

    // Format game context
    const gameContext = gameHistory.map(round => 
      `Round ${round.round}: User chose ${round.userChoice}, AI chose ${round.llmChoice}`
    ).join('\n');

    // Create chat completion
    const completion = await openai.chat.completions.create({
      model: "grok-beta",
      messages: [
        {
          role: "system",
          content: `You are playing a Split or Steal game. Current game state:
${gameContext}
Engage in conversation with the user, but remember you're playing against them.
Be strategic but friendly. Don't reveal your next move directly.`
        },
        ...chatHistory.map(msg => ({
          role: msg.role,
          content: msg.content
        })),
        {
          role: "user",
          content: message
        }
      ]
    });

    res.status(200).json({
      response: completion.choices[0].message.content
    });

  } catch (error) {
    console.error('Error:', error);
    res.status(200).json({
      response: "Sorry, I couldn't process that message. Let's continue with the game."
    });
  }
}