"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { ArrowLeft, User, Users } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { toast } from "@/components/ui/use-toast"
import { Badge } from "@/components/ui/badge"

// Types
interface UserData {
  id: string
  name: string
  age: number
  city: string
  occupation: string
  interests: {
    id: string
    name: string
  }[]
  group: {
    name: string
  }
  subgroup: {
    name: string
  }
  subgroupMembers: {
    id: string
    name: string
    age: number
    occupation: string
  }[]
}

export default function DashboardPage() {
  const { userId } = useParams()
  const [userData, setUserData] = useState<UserData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        // In a real app, this would be a fetch to your API
        const response = await fetch(`http://localhost:8000/api/user-detail/${userId}/`);
        const data = await response.json();
        console.log('DATAAAAA >>> ', data);

        // For demo purposes, we'll use mock data
        let mockUserData: UserData = {
          id: userId as string,
          name: "Jane Doe",
          age: 28,
          city: "New York",
          occupation: "Software Engineer",
          interests: [
            { id: "1", name: "Technology" },
            { id: "2", name: "Music" },
            { id: "3", name: "Travel" },
            { id: "4", name: "Photography" },
            { id: "5", name: "Reading" },
          ],
          group: {
            name: "Tech Enthusiasts",
          },
          subgroup: {
            name: "Frontend Developers",
          },
          subgroupMembers: [
            {
              id: "user_1001",
              name: "John Smith",
              age: 32,
              occupation: "UX Designer",
            },
            {
              id: "user_1002",
              name: "Alice Johnson",
              age: 26,
              occupation: "Frontend Developer",
            },
            {
              id: "user_1003",
              name: "Bob Williams",
              age: 30,
              occupation: "Product Manager",
            },
          ],
        }

        mockUserData = data; //Comment out this line to see demo data and structure

        // Simulate API delay
        setTimeout(() => {
          setUserData(mockUserData)
          setIsLoading(false)
        }, 1000)
      } catch (error) {
        console.error("Failed to fetch user data:", error)
        toast({
          title: "Error",
          description: "Failed to load user data. Please try again.",
          variant: "destructive",
        })
        setIsLoading(false)
      }
    }

    if (userId) {
      fetchUserData()
    }
  }, [userId])

  if (isLoading) {
    return <DashboardSkeleton />
  }

  if (!userData) {
    return (
      <div className="flex min-h-[calc(100vh-4rem)] flex-col items-center justify-center p-4">
        <div className="text-center">
          <h1 className="text-2xl font-bold">User Not Found</h1>
          <p className="mt-2 text-muted-foreground">The user ID you provided was not found.</p>
          <Button asChild className="mt-4">
            <Link href="/">Return Home</Link>
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto max-w-4xl py-8 px-4">
      <div className="mb-6">
        <Button asChild variant="ghost" size="sm">
          <Link href="/">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Home
          </Link>
        </Button>
      </div>

      <div className="mb-8 text-center">
        <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-primary/10">
          <Users className="h-10 w-10 text-primary" />
        </div>
        <h1 className="mt-4 text-3xl font-bold">{userData.name}'s Dashboard</h1>
        <div className="mt-2 flex justify-center gap-2">
          <Badge variant="outline" className="bg-primary/5 text-primary">
            {userData.group.name}
          </Badge>
          <Badge variant="outline" className="bg-primary/5 text-primary">
            {userData.subgroup.name}
          </Badge>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="border-primary/20">
          <CardHeader className="bg-primary/5">
            <CardTitle>User Profile</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 pt-6">
            <div>
              <h3 className="font-medium text-muted-foreground">Name</h3>
              <p className="text-lg">{userData.name}</p>
            </div>
            <div>
              <h3 className="font-medium text-muted-foreground">Age</h3>
              <p className="text-lg">{userData.age}</p>
            </div>
            <div>
              <h3 className="font-medium text-muted-foreground">City</h3>
              <p className="text-lg">{userData.city}</p>
            </div>
            <div>
              <h3 className="font-medium text-muted-foreground">Occupation</h3>
              <p className="text-lg">{userData.occupation}</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-primary/20">
          <CardHeader className="bg-primary/5">
            <CardTitle>Your Interests</CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="flex flex-wrap gap-2">
              {userData.interests.map((interest) => (
                <Badge key={interest.id} variant="outline" className="bg-primary/5 text-primary py-1 px-3">
                  {interest.name}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="mt-6 border-primary/20">
        <CardHeader className="bg-primary/5">
          <CardTitle>Your Mutuals Group Info</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 pt-6">
          <div>
            <h3 className="font-medium text-muted-foreground">Group</h3>
            <p className="text-lg">{userData.group.name}</p>
          </div>
          <div>
            <h3 className="font-medium text-muted-foreground">Subgroup</h3>
            <p className="text-lg">{userData.subgroup.name}</p>
          </div>
        </CardContent>
      </Card>

      <Card className="mt-6 border-primary/20">
        <CardHeader className="bg-primary/5">
          <CardTitle>Your Fellow Mutuals</CardTitle>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {userData.subgroupMembers.map((member) => (
              <Card
                key={member.id}
                className="overflow-hidden border-primary/10 transition-all hover:border-primary/30 hover:shadow-md"
              >
                <CardContent className="p-4">
                  <div className="flex items-center space-x-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
                      <User className="h-6 w-6 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-medium">{member.name}</h3>
                      <p className="text-sm text-muted-foreground">
                        {member.age} • {member.occupation}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function DashboardSkeleton() {
  return (
    <div className="container mx-auto max-w-4xl py-8 px-4">
      <div className="mb-6">
        <Skeleton className="h-10 w-32" />
      </div>

      <div className="mb-8 flex flex-col items-center justify-center">
        <Skeleton className="h-20 w-20 rounded-full" />
        <Skeleton className="mt-4 h-8 w-48" />
        <div className="mt-2 flex justify-center gap-2">
          <Skeleton className="h-6 w-24" />
          <Skeleton className="h-6 w-24" />
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <Skeleton className="h-8 w-32" />
          </CardHeader>
          <CardContent className="space-y-4">
            {Array(4)
              .fill(null)
              .map((_, i) => (
                <div key={i}>
                  <Skeleton className="h-4 w-24 mb-2" />
                  <Skeleton className="h-6 w-full" />
                </div>
              ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <Skeleton className="h-8 w-32" />
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {Array(5)
                .fill(null)
                .map((_, i) => (
                  <Skeleton key={i} className="h-8 w-20" />
                ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="mt-6">
        <CardHeader>
          <Skeleton className="h-8 w-40" />
        </CardHeader>
        <CardContent className="space-y-4">
          {Array(2)
            .fill(null)
            .map((_, i) => (
              <div key={i}>
                <Skeleton className="h-4 w-24 mb-2" />
                <Skeleton className="h-6 w-full" />
              </div>
            ))}
        </CardContent>
      </Card>

      <Card className="mt-6">
        <CardHeader>
          <Skeleton className="h-8 w-40" />
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {Array(3)
              .fill(null)
              .map((_, i) => (
                <Card key={i} className="overflow-hidden">
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-4">
                      <Skeleton className="h-12 w-12 rounded-full" />
                      <div className="space-y-2">
                        <Skeleton className="h-4 w-24" />
                        <Skeleton className="h-3 w-32" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}