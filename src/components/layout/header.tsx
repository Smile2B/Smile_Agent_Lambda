import { ModeToggle } from "@/components/mode-toggle"
import { Button } from "@/components/ui/button"
import Link from "next/link"

export function Header() {
  return (
    <header className="border-b">
      <div className="container flex h-16 items-center justify-between">
        <div className="flex items-center gap-6">
          <Link href="/">
            <h1 className="text-2xl font-bold">Smile Agent</h1>
          </Link>
          <nav className="hidden md:flex gap-6">
            <Link href="/tools">
              <Button variant="ghost">Tools</Button>
            </Link>
            <Link href="/about">
              <Button variant="ghost">About</Button>
            </Link>
          </nav>
        </div>
        <div className="flex items-center gap-4">
          <ModeToggle />
        </div>
      </div>
    </header>
  )
}
