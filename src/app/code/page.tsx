import { CodeGenerator } from "@/app/code/code-genarator"

export default function CodePage() {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Code Generator</h1>
      <CodeGenerator />
    </div>
  )
}