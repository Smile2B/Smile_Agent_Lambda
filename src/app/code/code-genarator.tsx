// src/components/features/code/generator.tsx
"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Loader2, Copy, Check } from "lucide-react"
import { cn } from "@/lib/utils"

const codeTypes = [
  { value: "lambda", label: "AWS Lambda Function" },
  { value: "cdk", label: "AWS CDK Infrastructure" },
  { value: "cloudformation", label: "CloudFormation Template" },
  { value: "terraform", label: "Terraform Configuration" },
  { value: "api", label: "API Implementation" },
  { value: "client", label: "Client SDK" },
] as const

const languages = [
  { value: "python", label: "Python" },
  { value: "typescript", label: "TypeScript" },
  { value: "javascript", label: "JavaScript" },
  { value: "go", label: "Go" },
  { value: "java", label: "Java" },
] as const

type CodeType = typeof codeTypes[number]["value"]
type Language = typeof languages[number]["value"]

interface GeneratedCode {
  code: string;
  language: Language;
  explanation: string;
  dependencies?: string[];
}

// Update with your API Gateway URL
const API_URL = process.env.NEXT_PUBLIC_API_GATEWAY_URL || 'https://your-api-gateway-url.amazonaws.com/prod';

export function CodeGenerator() {
  const [loading, setLoading] = useState(false)
  const [generatedCode, setGeneratedCode] = useState<GeneratedCode | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setLoading(true)
    setError(null)
    setGeneratedCode(null)

    const formData = new FormData(event.currentTarget)
    const data = {
      description: formData.get("description"),
      type: formData.get("type"),
      language: formData.get("language"),
    }

    try {
      const response = await fetch(`${API_URL}/generate-code`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || "Failed to generate code")
      }

      const result = await response.json()
      setGeneratedCode(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong")
      console.error("Code generation error:", err)
    } finally {
      setLoading(false)
    }
  }

  async function copyToClipboard(text: string) {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error("Failed to copy:", err)
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <div>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="type">Code Type</Label>
            <Select name="type" defaultValue="lambda">
              <SelectTrigger>
                <SelectValue placeholder="Select code type" />
              </SelectTrigger>
              <SelectContent>
                {codeTypes.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="language">Programming Language</Label>
            <Select name="language" defaultValue="python">
              <SelectTrigger>
                <SelectValue placeholder="Select language" />
              </SelectTrigger>
              <SelectContent>
                {languages.map((lang) => (
                  <SelectItem key={lang.value} value={lang.value}>
                    {lang.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              name="description"
              placeholder="Describe what you want the code to do..."
              className="h-32"
              required
            />
          </div>

          <Button type="submit" className="w-full" disabled={loading}>
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Generate Code
          </Button>

          {error && (
            <p className="text-sm text-red-500 mt-2">{error}</p>
          )}
        </form>

        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Tips for better results</CardTitle>
            <CardDescription>
              Follow these guidelines for optimal code generation
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-48">
              <ul className="space-y-2 text-sm">
                <li>• Be specific about functionality requirements</li>
                <li>• Mention error handling needs</li>
                <li>• Specify input/output formats</li>
                <li>• Include any performance requirements</li>
                <li>• Note any specific AWS services to use</li>
                <li>• Mention security requirements</li>
                <li>• Specify any dependencies or frameworks</li>
                <li>• Include logging requirements</li>
              </ul>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>

      <div>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <div>
              <CardTitle>Generated Code</CardTitle>
              <CardDescription>
                {generatedCode?.language && `${generatedCode.language} implementation`}
              </CardDescription>
            </div>
            {generatedCode && (
              <Button
                variant="outline"
                size="icon"
                onClick={() => copyToClipboard(generatedCode.code)}
                className="h-8 w-8"
              >
                {copied ? (
                  <Check className="h-4 w-4" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </Button>
            )}
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex items-center justify-center h-96">
                <Loader2 className="h-8 w-8 animate-spin" />
              </div>
            ) : generatedCode ? (
              <div className="space-y-4">
                <ScrollArea className="h-96 w-full rounded-md border">
                  <pre className="p-4">
                    <code>{generatedCode.code}</code>
                  </pre>
                </ScrollArea>
                {generatedCode.explanation && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Explanation</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground">
                        {generatedCode.explanation}
                      </p>
                      {generatedCode.dependencies && (
                        <div className="mt-4">
                          <h4 className="font-medium mb-2">Dependencies</h4>
                          <ul className="list-disc list-inside text-sm text-muted-foreground">
                            {generatedCode.dependencies.map((dep, index) => (
                              <li key={index}>{dep}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )}
              </div>
            ) : (
              <div className="flex items-center justify-center h-96 border rounded-lg bg-muted/50">
                <p className="text-sm text-muted-foreground">
                  Your code will appear here
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}