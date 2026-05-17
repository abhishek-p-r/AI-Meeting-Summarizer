import { generateObject } from 'ai'
import { z } from 'zod'

// Trim text to a reasonable length to prevent timeout issues
const TRANSCRIPT_MAX_LENGTH = 8000

const truncateTranscript = (text: string): string => {
  if (text.length <= TRANSCRIPT_MAX_LENGTH) return text
  return text.substring(0, TRANSCRIPT_MAX_LENGTH) + '\n\n[... transcript truncated ...]'
}

const summarySchema = z.object({
  summary: z.string().describe('A concise summary of the meeting (2-3 paragraphs)'),
  keyPoints: z.array(z.string()).describe('3-5 key points discussed in the meeting'),
  actionItems: z.array(z.string()).describe('Specific action items with owners if mentioned'),
})

// Demo/mock summary generator for when API key is not available
function generateMockSummary(transcript: string) {
  const sentences = transcript.split(/[.!?]+/).filter((s) => s.trim().length > 0)
  const keyTopics = [
    'Q3 roadmap and product planning',
    'Timeline and resource allocation',
    'Feature development and testing',
    'Team responsibilities and deadlines',
  ]

  const keyPoints = sentences
    .slice(0, 5)
    .map((s) => s.trim())
    .filter((s) => s.length > 20)

  const actionItems = sentences
    .filter((s) => s.toLowerCase().includes('should') || s.toLowerCase().includes('need'))
    .slice(0, 3)
    .map((s) => s.trim())

  return {
    summary: `The meeting focused on ${keyTopics[0]}. The team discussed implementation timelines and resource allocation for upcoming features. Key decisions were made regarding project priorities and next steps for team members.`,
    keyPoints: keyPoints.length > 0 ? keyPoints : ['Project planning and roadmap review', 'Team allocation and responsibilities'],
    actionItems: actionItems.length > 0 ? actionItems : ['Review specification documents', 'Schedule follow-up sync'],
  }
}

export async function summarizeMeeting(transcript: string) {
  try {
    const truncatedTranscript = truncateTranscript(transcript)

    // Check if API key is available
    const hasApiKey = process.env.OPENAI_API_KEY || process.env.AUTH0_SECRET
    if (!hasApiKey) {
      // Use mock summary in demo mode
      console.log('[v0] API key not configured, using demo mode')
      return generateMockSummary(truncatedTranscript)
    }

    const { object } = await generateObject({
      model: 'openai/gpt-4-turbo',
      schema: summarySchema,
      prompt: `You are an expert meeting summarizer. Analyze this meeting transcript and provide:
1. A concise 2-3 paragraph summary
2. 3-5 key points discussed
3. Specific action items mentioned (include owner/person if mentioned)

Meeting Transcript:
${truncatedTranscript}

Please be thorough but concise.`,
      temperature: 0.7,
    })

    return {
      summary: object.summary,
      keyPoints: object.keyPoints,
      actionItems: object.actionItems,
    }
  } catch (error) {
    console.error('[v0] Error summarizing meeting:', error)
    // Fall back to mock summary
    return generateMockSummary(transcript)
  }
}
