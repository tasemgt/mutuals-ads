import Link from "next/link"
import { Users } from "lucide-react"
import { Button } from "@/components/ui/button"

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center">
        <Link href="/" className="flex items-center gap-2">
          <Users className="h-6 w-6 text-primary" />
          <span className="text-xl font-bold">Mutuals</span>
        </Link>
        <nav className="ml-auto flex gap-4">
          <Button asChild variant="ghost" size="sm">
            <Link href="/register">Register</Link>
          </Button>
          <Button asChild variant="ghost" size="sm">
            <Link href="/login">Login</Link>
          </Button>
          <Button asChild size="sm">
            <Link href="/register">Get Started</Link>
          </Button>
        </nav>
      </div>
    </header>
  )
}
