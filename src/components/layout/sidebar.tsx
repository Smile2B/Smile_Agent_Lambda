import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { cn } from "@/lib/utils"
import Link from "next/link"
import { usePathname } from "next/navigation"

const tools = [
  {
    name: "AWS Well-Architected",
    href: "/tools/well-architected",
  },
  {
    name: "Architecture Diagram",
    href: "/tools/diagram",
  },
  {
    name: "Code Generator",
    href: "/tools/code",
  },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <ScrollArea className="h-full py-6 pl-8 pr-6 lg:pl-10">
      <div className="space-y-4">
        <div className="py-2">
          <h2 className="mb-2 px-4 text-lg font-semibold">Tools</h2>
          <div className="space-y-1">
            {tools.map((tool) => (
              <Button
                key={tool.href}
                variant={pathname === tool.href ? "secondary" : "ghost"}
                className={cn(
                  "w-full justify-start",
                  pathname === tool.href && "bg-muted"
                )}
                asChild
              >
                <Link href={tool.href}>{tool.name}</Link>
              </Button>
            ))}
          </div>
        </div>
      </div>
    </ScrollArea>
  )
}
