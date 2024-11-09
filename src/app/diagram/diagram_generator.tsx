// src/app/diagram/generator.tsx
"use client"
import { LambdaClient, InvokeCommand } from "@aws-sdk/client-lambda";
import { useAuth } from "@/hooks/useAuth";
import { useState } from "react"
import { Button } from "@/components/ui/button"
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
import { Loader2 } from "lucide-react"

const diagramTypes = [
  { value: "architecture", label: "Architecture Diagram" },
  { value: "sequence", label: "Sequence Diagram" },
  { value: "flow", label: "Flow Diagram" },
]

const API_URL = process.env.NEXT_PUBLIC_API_GATEWAY_URL || 'https://bla3r6rqe7.execute-api.us-east-1.amazonaws.com/prod';

export function DiagramGenerator() {
  const [loading, setLoading] = useState(false);
  const [diagram, setDiagram] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { getCredentials } = useAuth();

  async function generateDiagram(query: string) {
    try {
      const credentials = await getCredentials();
      
      const lambda = new LambdaClient({ 
        region: process.env.NEXT_PUBLIC_COGNITO_USER_POOL_REGION || 'us-east-1',
        credentials: {
          accessKeyId: credentials.accessKeyId,
          secretAccessKey: credentials.secretAccessKey,
          sessionToken: credentials.sessionToken
        }
      });

      // Prepare the payload to match the expected Lambda event structure
      const payload = {
        body: JSON.stringify({
          tool_type: "Diagram Tool",
          query: query
        })
      };

      const command = new InvokeCommand({
        FunctionName: process.env.NEXT_PUBLIC_LAMBDA_FUNCTION_NAME || 'claude3-agent-function',
        Payload: JSON.stringify(payload),  // Wrap the payload in the expected event structure
      });

      const response = await lambda.send(command);
      if (!response.Payload) {
        throw new Error("No response from Lambda");
      }
      const payloadResponse = JSON.parse(new TextDecoder().decode(response.Payload));
      
      if (payloadResponse.statusCode === 200) {
        const body = JSON.parse(payloadResponse.body);
        if (body.success && body.type === "diagram") {
          return body.data.image;
        }
        throw new Error(body.message || "Failed to generate diagram");
      } else {
        const errorBody = payloadResponse.body ? JSON.parse(payloadResponse.body) : {};
        throw new Error(errorBody.message || "Failed to generate diagram");
      }
    } catch (error) {
      console.error("Error generating diagram:", error);
      throw error;
    }
  
  }
  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    const formData = new FormData(event.currentTarget);
    const description = formData.get("description") as string;

    try {
      const image = await generateDiagram(description);
      setDiagram(image);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      console.error("Diagram generation error:", err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <div>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="type">Diagram Type</Label>
            <Select name="type" defaultValue="architecture">
              <SelectTrigger>
                <SelectValue placeholder="Select diagram type" />
              </SelectTrigger>
              <SelectContent>
                {diagramTypes.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
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
              placeholder="Describe your architecture (e.g., A web application using S3, Lambda, and API Gateway...)"
              className="h-32"
              required
            />
          </div>

          <Button type="submit" className="w-full" disabled={loading}>
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Generate Diagram
          </Button>

          {error && (
            <p className="text-sm text-red-500 mt-2">{error}</p>
          )}
        </form>

        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Tips for better results</CardTitle>
            <CardDescription>
              Follow these guidelines for optimal diagram generation
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-48">
              <ul className="space-y-2 text-sm">
                <li>• Be specific about service connections</li>
                <li>• Mention security and networking requirements</li>
                <li>• Specify any high availability needs</li>
                <li>• Include data flow directions</li>
                <li>• Mention specific AWS regions if relevant</li>
                <li>• Describe any auto-scaling requirements</li>
                <li>• Include disaster recovery considerations</li>
                <li>• Specify compliance requirements</li>
              </ul>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>

      <div>
        <Card>
          <CardHeader>
            <CardTitle>Generated Diagram</CardTitle>
            <CardDescription>
              Preview of your architecture diagram
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex items-center justify-center h-96">
                <Loader2 className="h-8 w-8 animate-spin" />
              </div>
            ) : diagram ? (
              <div className="border rounded-lg p-4">
                <img 
                  src={`data:image/svg+xml;base64,${diagram}`} 
                  alt="Generated Architecture Diagram"
                  className="w-full"
                />
              </div>
            ) : (
              <div className="flex items-center justify-center h-96 border rounded-lg bg-muted/50">
                <p className="text-sm text-muted-foreground">
                  Your diagram will appear here
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}