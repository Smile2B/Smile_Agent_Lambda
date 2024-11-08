// src/app/well-architected/form.tsx
"use client"

import { useState } from "react"
import { 
  LayoutDashboard,
  Settings,
  Shield,
  HeartPulse,
  Gauge,
  DollarSign,
  Leaf 
} from "lucide-react"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
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
import { Badge } from "@/components/ui/badge"

const pillars = [
  {
    value: "comprehensive",
    label: "Comprehensive Analysis",
    description: "Complete analysis across all Well-Architected pillars",
    icon: LayoutDashboard
  },
  {
    value: "operational-excellence",
    label: "Operational Excellence",
    description: "Running and monitoring systems to deliver business value",
    icon: Settings
  },
  {
    value: "security",
    label: "Security",
    description: "Protecting information, systems, and assets",
    icon: Shield
  },
  {
    value: "reliability",
    label: "Reliability",
    description: "Ensuring a system performs its intended function correctly",
    icon: HeartPulse
  },
  {
    value: "performance-efficiency",
    label: "Performance Efficiency",
    description: "Using computing resources efficiently",
    icon: Gauge
  },
  {
    value: "cost-optimization",
    label: "Cost Optimization",
    description: "Avoiding unnecessary costs",
    icon: DollarSign
  },
  {
    value: "sustainability",
    label: "Sustainability",
    description: "Minimizing the environmental impacts of cloud workloads",
    icon: Leaf
  }
];

interface AnalysisResults {
  overallAssessment?: string;
  findings?: Array<{
    pillars: string[];
    finding: string;
    impact: string;
    recommendation: string;
    priority: 'High' | 'Medium' | 'Low';
  }>;
  implementationRoadmap?: Array<{
    phase: string;
    actions: string[];
    dependencies: string[];
  }>;
}

export function WellArchitectedForm() {
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<AnalysisResults | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [selectedPillar, setSelectedPillar] = useState("comprehensive")

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setLoading(true)
    setError(null)

    const formData = new FormData(event.currentTarget)
    const data = {
      projectName: formData.get("projectName"),
      pillar: formData.get("pillar"),
      description: formData.get("description")
    }

    // Debug log
    console.log('API URL:', process.env.NEXT_PUBLIC_API_GATEWAY_URL)
    console.log('Sending data:', data)

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_GATEWAY_URL}/well-architected`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify(data),
        mode: 'cors'  // Add this
      })

      // Debug log
      console.log('Response status:', response.status)
      
      if (!response.ok) {
        const errorText = await response.text()
        console.error('Error response:', errorText)
        throw new Error(errorText || "Failed to analyze architecture")
      }

      const analysisResults = await response.json()
      console.log('Success response:', analysisResults)
      setResults(analysisResults)
    } catch (err) {
      console.error('Fetch error:', err)
      setError(err instanceof Error ? err.message : "Network error - please try again")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <div>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="projectName">Project Name</Label>
            <Input
              id="projectName"
              name="projectName"
              placeholder="Enter your project name"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="pillar">Analysis Scope</Label>
            <Select 
              name="pillar" 
              defaultValue="comprehensive"
              onValueChange={setSelectedPillar}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select analysis scope" />
              </SelectTrigger>
              <SelectContent>
                {pillars.map((pillar) => (
                  <SelectItem
                    key={pillar.value}
                    value={pillar.value}
                  >
                    <div className="flex items-center gap-2">
                      <pillar.icon className="h-4 w-4" />
                      <span>{pillar.label}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-sm text-muted-foreground">
              {pillars.find(p => p.value === selectedPillar)?.description}
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Architecture Description</Label>
            <Textarea
              id="description"
              name="description"
              placeholder="Describe your current architecture and requirements..."
              className="h-32"
              required
            />
          </div>

          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "Analyzing..." : "Analyze Architecture"}
          </Button>

          {error && (
            <p className="text-sm text-red-500 mt-2">{error}</p>
          )}
        </form>

        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Analysis Guidelines</CardTitle>
            <CardDescription>
              Tips for better analysis results
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm">
              <li>• Describe your current architecture in detail</li>
              <li>• Include your main requirements and constraints</li>
              <li>• Mention any specific compliance needs</li>
              <li>• List your key performance indicators</li>
              <li>• Specify any cost or resource constraints</li>
            </ul>
          </CardContent>
        </Card>
      </div>

      <div>
        {results && (
          <Card>
            <CardHeader>
              <CardTitle>Analysis Results</CardTitle>
              <CardDescription>
                {selectedPillar === 'comprehensive' 
                  ? 'Comprehensive Well-Architected analysis'
                  : `Analysis for ${pillars.find(p => p.value === selectedPillar)?.label}`}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {results.overallAssessment && (
                <div className="space-y-4">
                  <div>
                    <h3 className="font-medium mb-2">Overall Assessment</h3>
                    <p className="text-sm text-muted-foreground">
                      {results.overallAssessment}
                    </p>
                  </div>

                  {results.findings && results.findings.length > 0 && (
                    <div>
                      <h3 className="font-medium mb-2">Key Findings</h3>
                      <div className="space-y-4">
                        {results.findings.map((finding, index) => (
                          <div key={index} className="border rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-2">
                              {finding.pillars.map(pillar => (
                                <Badge key={pillar} variant="secondary">
                                  {pillar}
                                </Badge>
                              ))}
                              <Badge 
                                variant={finding.priority === 'High' ? 'destructive' : 'outline'}
                              >
                                {finding.priority}
                              </Badge>
                            </div>
                            <p className="font-medium">{finding.finding}</p>
                            <p className="text-sm text-muted-foreground mt-1">
                              {finding.recommendation}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {results.implementationRoadmap && (
                    <div>
                      <h3 className="font-medium mb-2">Implementation Roadmap</h3>
                      <div className="space-y-4">
                        {results.implementationRoadmap.map((phase, index) => (
                          <div key={index} className="border-l-2 pl-4">
                            <h4 className="font-medium">{phase.phase}</h4>
                            <ul className="mt-2 space-y-2">
                              {phase.actions.map((action, actionIndex) => (
                                <li key={actionIndex} className="text-sm">
                                  {action}
                                </li>
                              ))}
                            </ul>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}