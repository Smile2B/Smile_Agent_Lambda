import { WellArchitectedForm } from "@/app/well-architected/form"

export default function WellArchitectedPage() {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Well-Architected Review</h1>
      <WellArchitectedForm />
    </div>
  )
}
