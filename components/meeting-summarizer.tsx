'use client'

import { useState, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Loader2, Upload, Zap, Copy, Check } from 'lucide-react'
import { summarizeMeeting } from '@/lib/summarize'
import { toast } from 'sonner'

interface SummaryResult {
  summary: string
  keyPoints: string[]
  actionItems: string[]
  participants?: string[]
}

export function MeetingSummarizer() {
  const [isLoading, setIsLoading] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [result, setResult] = useState<SummaryResult | null>(null)
  const [copied, setCopied] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file size (max 25MB for most APIs)
    if (file.size > 25 * 1024 * 1024) {
      toast.error('File is too large. Maximum size is 25MB.')
      return
    }

    setIsLoading(true)
    setResult(null)

    try {
      // Convert audio to text (placeholder - would use actual API in production)
      const text = await new Promise<string>((resolve) => {
        // For demo purposes, use a sample transcript
        setTimeout(() => {
          resolve(`Good morning everyone. Let's start with the Q3 roadmap review. 
            First, I want to discuss our upcoming product launches. We have three major features planned.
            Sarah, can you walk us through the timeline? We need to finalize the requirements by next week.
            The engineering team estimates 6 weeks for implementation. We should allocate resources from the mobile team.
            We also need to discuss the timeline for the customer onboarding improvements.
            Let's aim for a soft launch in early September. After that, we need marketing to prepare the campaign.
            John, can you update us on the analytics dashboard? The redesign is almost complete.
            We're seeing good feedback from beta users. The performance improvements are significant.
            Action items: Everyone should review the spec document by Thursday. 
            We'll have a follow-up sync on Friday to finalize everything. Thanks everyone.`)
        }, 500)
      })

      setTranscript(text)

      // Get summary from AI
      setIsLoading(true)
      const summary = await summarizeMeeting(text)
      setResult(summary)
      toast.success('Meeting summarized successfully!')
    } catch (error) {
      console.error('Error processing meeting:', error)
      toast.error('Failed to summarize meeting. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleTextInput = async () => {
    if (!transcript.trim()) {
      toast.error('Please enter meeting transcript')
      return
    }

    setIsLoading(true)
    setResult(null)

    try {
      const summary = await summarizeMeeting(transcript)
      setResult(summary)
      toast.success('Meeting summarized successfully!')
    } catch (error) {
      console.error('Error processing meeting:', error)
      toast.error('Failed to summarize meeting. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
    toast.success('Copied to clipboard!')
  }

  return (
    <div className="max-w-4xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="text-center mb-12">
        <div className="flex items-center justify-center gap-2 mb-4">
          <Zap className="w-8 h-8 text-primary" />
          <h1 className="text-4xl font-bold text-foreground">Meeting Summarizer</h1>
        </div>
        <p className="text-lg text-muted-foreground">
          Transform your meeting transcripts into actionable summaries in seconds
        </p>
      </div>

      {/* Input Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* File Upload */}
        <Card className="p-6 border-dashed border-2 border-primary/20 hover:border-primary/40 transition-colors">
          <div className="flex flex-col items-center justify-center gap-4 min-h-48">
            <Upload className="w-12 h-12 text-primary/60" />
            <div className="text-center">
              <h3 className="font-semibold text-foreground mb-1">Upload Audio</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Upload an audio file to transcribe and summarize
              </p>
              <Button
                onClick={() => fileInputRef.current?.click()}
                variant="outline"
                size="sm"
                disabled={isLoading}
              >
                Choose File
              </Button>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept="audio/*,video/*"
              onChange={handleFileUpload}
              className="hidden"
              disabled={isLoading}
            />
          </div>
        </Card>

        {/* Text Input */}
        <Card className="p-6 flex flex-col">
          <h3 className="font-semibold text-foreground mb-3">Paste Transcript</h3>
          <textarea
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
            placeholder="Paste your meeting transcript here..."
            className="flex-1 p-3 bg-secondary/20 border border-border rounded-md text-foreground placeholder-muted-foreground resize-none focus:outline-none focus:ring-2 focus:ring-primary/50 mb-3"
            disabled={isLoading}
          />
          <Button
            onClick={handleTextInput}
            disabled={isLoading || !transcript.trim()}
            className="w-full"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Processing...
              </>
            ) : (
              'Summarize'
            )}
          </Button>
        </Card>
      </div>

      {/* Results Section */}
      {result && (
        <div className="space-y-6 animate-in fade-in-50 duration-500">
          {/* Summary */}
          <Card className="p-6 border-primary/20">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold text-foreground">Summary</h2>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => copyToClipboard(result.summary)}
              >
                {copied ? (
                  <Check className="w-4 h-4 text-green-500" />
                ) : (
                  <Copy className="w-4 h-4" />
                )}
              </Button>
            </div>
            <p className="text-muted-foreground leading-relaxed whitespace-pre-wrap">
              {result.summary}
            </p>
          </Card>

          {/* Key Points */}
          <Card className="p-6">
            <h3 className="text-xl font-bold text-foreground mb-4">Key Points</h3>
            <ul className="space-y-2">
              {result.keyPoints.map((point, i) => (
                <li key={i} className="flex gap-3">
                  <span className="text-primary font-bold flex-shrink-0">•</span>
                  <span className="text-muted-foreground">{point}</span>
                </li>
              ))}
            </ul>
          </Card>

          {/* Action Items */}
          {result.actionItems.length > 0 && (
            <Card className="p-6 border-primary/30 bg-primary/5">
              <h3 className="text-xl font-bold text-foreground mb-4">Action Items</h3>
              <ul className="space-y-2">
                {result.actionItems.map((item, i) => (
                  <li key={i} className="flex gap-3">
                    <span className="text-primary font-bold flex-shrink-0">↗</span>
                    <span className="text-muted-foreground">{item}</span>
                  </li>
                ))}
              </ul>
            </Card>
          )}

          {/* Export Options */}
          <div className="flex gap-3">
            <Button
              onClick={() => copyToClipboard(result.summary)}
              variant="outline"
              className="flex-1"
            >
              <Copy className="w-4 h-4 mr-2" />
              Copy Summary
            </Button>
            <Button
              onClick={() => {
                const content = `Meeting Summary\n\n${result.summary}\n\nKey Points:\n${result.keyPoints.map((p) => `- ${p}`).join('\n')}\n\nAction Items:\n${result.actionItems.map((a) => `- ${a}`).join('\n')}`
                copyToClipboard(content)
              }}
              variant="outline"
              className="flex-1"
            >
              <Zap className="w-4 h-4 mr-2" />
              Export Full
            </Button>
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <Loader2 className="w-12 h-12 animate-spin text-primary mx-auto mb-4" />
            <p className="text-muted-foreground">Processing your meeting...</p>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!result && !isLoading && !transcript && (
        <Card className="p-12 text-center border-dashed">
          <h3 className="text-lg font-semibold text-muted-foreground mb-2">
            No meeting data yet
          </h3>
          <p className="text-sm text-muted-foreground">
            Upload an audio file or paste a transcript to get started
          </p>
        </Card>
      )}
    </div>
  )
}
