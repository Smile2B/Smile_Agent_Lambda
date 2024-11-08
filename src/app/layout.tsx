// src/app/layout.tsx
import { Inter } from "next/font/google"
import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import { MainNav } from "@/components/layout/main-nav"
import { UserNav } from "@/components/layout/user-nav"
import { ModeToggle } from "@/components/mode-toggle"
import { Providers } from "@/components/providers/Providers"

const inter = Inter({ subsets: ["latin"] })

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>
          <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange
          >
            <div className="min-h-screen flex flex-col">
              <header className="border-b">
                <div className="container flex h-16 items-center">
                  <h1 className="text-2xl font-bold mr-6">Smile Agent</h1>
                  <MainNav />
                  <div className="ml-auto flex items-center space-x-4">
                    <ModeToggle />
                    <UserNav />
                  </div>
                </div>
              </header>
              <main className="flex-1 container py-6">{children}</main>
            </div>
          </ThemeProvider>
        </Providers>
      </body>
    </html>
  )
}