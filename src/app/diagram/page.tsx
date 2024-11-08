import { DiagramGenerator } from "@/app/diagram/diagram_generator"
import AuthWrapper from "@/components/auth-wrapper"


export default function DiagramPage() {
  return (
    <AuthWrapper>
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Diagram Generator</h1>
        <DiagramGenerator />
      </div>
    </AuthWrapper>
  )
}