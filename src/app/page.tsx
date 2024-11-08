import { Button } from "@/components/ui/button"
import { ArrowRight } from "lucide-react"
import Link from "next/link"

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center space-y-8 text-center">
      <h1 className="text-4xl font-bold">Welcome to Smile Agent</h1>
      <p className="text-xl text-muted-foreground max-w-2xl">
        Your intelligent AWS Architecture Assistant. Design, validate, and optimize
        your cloud infrastructure with AI-powered tools.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-4xl">
        <Link href="/well-architected">
          <div className="group relative rounded-lg border p-6 hover:border-primary transition-colors">
            <h3 className="font-semibold mb-2">Well-Architected Review</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Evaluate your architecture against AWS best practices.
            </p>
            <ArrowRight className="h-4 w-4 absolute bottom-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
        </Link>
        <Link href="/diagram">
          <div className="group relative rounded-lg border p-6 hover:border-primary transition-colors">
            <h3 className="font-semibold mb-2">Diagram Generator</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Create professional AWS architecture diagrams instantly.
            </p>
            <ArrowRight className="h-4 w-4 absolute bottom-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
        </Link>
        <Link href="/code">
          <div className="group relative rounded-lg border p-6 hover:border-primary transition-colors">
            <h3 className="font-semibold mb-2">Code Generator</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Generate infrastructure as code from your designs.
            </p>
            <ArrowRight className="h-4 w-4 absolute bottom-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
        </Link>
      </div>
    </div>
  )
}