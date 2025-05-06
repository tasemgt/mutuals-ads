import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Users } from "lucide-react"

export default function WelcomePage() {
  return (
    <div className="flex min-h-[calc(100vh-4rem)] flex-col items-center justify-center bg-background p-4">
      <div className="w-full max-w-md space-y-8 text-center">
        <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-primary/10">
          <Users className="h-10 w-10 text-primary" />
        </div>

        <div>
          <h1 className="text-4xl font-bold tracking-tight text-foreground">Welcome to Mutuals</h1>
          <p className="mt-3 text-muted-foreground">Connect with people who share your interests</p>
        </div>

        <div className="rounded-lg border bg-card p-6 shadow-sm">
          <div className="flex flex-col gap-4">
            <Button asChild size="lg" className="w-full">
              <Link href="/register">Get Started</Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="w-full">
              <Link href="/login">View My Dashboard</Link>
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
