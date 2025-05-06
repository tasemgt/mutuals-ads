"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { format } from "date-fns"
import { CalendarIcon, CheckIcon, ChevronsUpDown, Users } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command"
import { cn } from "@/lib/utils"
import { toast } from "@/components/ui/use-toast"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

// Form schema
const formSchema = z.object({
  name: z.string().min(2, { message: "Name must be at least 2 characters" }),
  gender: z.string().min(1, { message: "Please select a gender" }),
  dateOfBirth: z.date({ required_error: "Please select a date of birth" }),
  interests: z.array(z.string()).min(1, { message: "Select at least one interest" }),
  city: z.string().min(2, { message: "City must be at least 2 characters" }),
  occupation: z.string().min(2, { message: "Occupation must be at least 2 characters" }),
  budget: z.coerce.number().min(0, { message: "Budget must be a positive number" }),
})

export default function RegisterPage() {
  const router = useRouter()
  const [interests, setInterests] = useState<{ id: string; name: string }[]>([])
  const [isLoading, setIsLoading] = useState(false)

  // Initialize form
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      gender: "",
      interests: [],
      city: "",
      occupation: "",
      budget: 0,
    },
  })

  // Fetch interests from API
  useEffect(() => {
    const fetchInterests = async () => {
      try {
        // In a real app, this would be a fetch to your API
        const response = await fetch('http://localhost:8000/api/interests');
        const data = await response.json();

        console.log("INterests > ", data);

        // For demo purposes, we'll use mock data
        let mockInterests = [
          { id: "1", name: "Sports" },
          { id: "2", name: "Music" },
          { id: "3", name: "Movies" },
          { id: "7", name: "Books" },
          { id: "5", name: "Travel" },
          { id: "6", name: "Food" },
          { id: "4", name: "Technology" },
          { id: "8", name: "Art" },
        ]

        mockInterests = [...data];

        setInterests(mockInterests);
      } catch (error) {
        console.error("Failed to fetch interests:", error)
        toast({
          title: "Error",
          description: "Failed to load interests. Please try again.",
          variant: "destructive",
        })
      }
    }

    fetchInterests()
  }, [])

  // Form submission handler
  async function onSubmit(values: z.infer<typeof formSchema>) {
    setIsLoading(true)

    try {

      
      const payload = {
        ...values,
        dob: format(values.dateOfBirth, 'yyyy-MM-dd'),
        interest_ids: values.interests
      };
      
      console.log("VALS >", payload);

      // In a real app, this would be a fetch to your API
      const response = await fetch('http://localhost:8000/api/users/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      console.log("created user >", data);

      // For demo purposes, we'll simulate a successful response
      // const mockUserId = "user_" + Math.floor(Math.random() * 10000)
      
      const userId = data.user_id;

      toast({
        title: "Registration Successful",
        description: "You have been registered successfully!",
      })

      // Redirect to dashboard with the returned user ID
      router.push(`/dashboard/${userId}`)
    } catch (error) {
      console.error("Registration failed:", error)
      toast({
        title: "Registration Failed",
        description: "There was an error during registration. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="container mx-auto max-w-2xl py-8 px-4">
      <div className="mb-8 text-center">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
          <Users className="h-8 w-8 text-primary" />
        </div>
        <h1 className="mt-4 text-3xl font-bold">Create Your Profile</h1>
        <p className="mt-2 text-muted-foreground">Join our community and connect with like-minded people</p>
      </div>

      <Card className="border-primary/20">
        <CardHeader>
          <CardTitle>Personal Information</CardTitle>
          <CardDescription>Fill in your details to get started</CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Name</FormLabel>
                    <FormControl>
                      <Input placeholder="Enter your name" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                <FormField
                  control={form.control}
                  name="gender"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Gender</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select your gender" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="male">Male</SelectItem>
                          <SelectItem value="female">Female</SelectItem>
                          <SelectItem value="other">Other</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="dateOfBirth"
                  render={({ field }) => (
                    <FormItem className="flex flex-col">
                      <FormLabel>Date of Birth</FormLabel>
                      <div className="flex gap-2">
                        <Select
                          onValueChange={(day) => {
                            const currentDate = field.value || new Date()
                            const newDate = new Date(currentDate)
                            newDate.setDate(Number.parseInt(day))
                            field.onChange(newDate)
                          }}
                          value={field.value ? field.value.getDate().toString() : ""}
                        >
                          <FormControl>
                            <SelectTrigger className="w-full">
                              <SelectValue placeholder="Day" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {Array.from({ length: 31 }, (_, i) => i + 1).map((day) => (
                              <SelectItem key={day} value={day.toString()}>
                                {day}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>

                        <Select
                          onValueChange={(month) => {
                            const currentDate = field.value || new Date()
                            const newDate = new Date(currentDate)
                            newDate.setMonth(Number.parseInt(month) - 1)
                            field.onChange(newDate)
                          }}
                          value={field.value ? (field.value.getMonth() + 1).toString() : ""}
                        >
                          <FormControl>
                            <SelectTrigger className="w-full">
                              <SelectValue placeholder="Month" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {[
                              { value: "1", label: "January" },
                              { value: "2", label: "February" },
                              { value: "3", label: "March" },
                              { value: "4", label: "April" },
                              { value: "5", label: "May" },
                              { value: "6", label: "June" },
                              { value: "7", label: "July" },
                              { value: "8", label: "August" },
                              { value: "9", label: "September" },
                              { value: "10", label: "October" },
                              { value: "11", label: "November" },
                              { value: "12", label: "December" },
                            ].map((month) => (
                              <SelectItem key={month.value} value={month.value}>
                                {month.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>

                        <Select
                          onValueChange={(year) => {
                            const currentDate = field.value || new Date()
                            const newDate = new Date(currentDate)
                            newDate.setFullYear(Number.parseInt(year))
                            field.onChange(newDate)
                          }}
                          value={field.value ? field.value.getFullYear().toString() : ""}
                        >
                          <FormControl>
                            <SelectTrigger className="w-full">
                              <SelectValue placeholder="Year" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent className="max-h-[200px]">
                          {Array.from({ length: 100 }, (_, i) => 2006 - i).map((year) => (
                            <SelectItem key={year} value={year.toString()}>
                              {year}
                            </SelectItem>
                          ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                <FormField
                  control={form.control}
                  name="city"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>City</FormLabel>
                      <FormControl>
                        <Input placeholder="Enter your city" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="occupation"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Occupation</FormLabel>
                      <FormControl>
                        <Input placeholder="Enter your occupation" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="budget"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Budget</FormLabel>
                    <FormControl>
                      <Input type="number" placeholder="Enter your budget" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="interests"
                render={({ field }) => (
                  <FormItem className="flex flex-col">
                    <FormLabel>Interests</FormLabel>
                    <Popover>
                      <PopoverTrigger asChild>
                        <FormControl>
                          <Button
                            variant="outline"
                            role="combobox"
                            className={cn("w-full justify-between", !field.value.length && "text-muted-foreground")}
                          >
                            {field.value.length > 0 ? `${field.value.length} selected` : "Select interests"}
                            <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                          </Button>
                        </FormControl>
                      </PopoverTrigger>
                      <PopoverContent className="w-full p-0">
                        <Command>
                          <CommandInput placeholder="Search interests..." />
                          <CommandList>
                            <CommandEmpty>No interest found.</CommandEmpty>
                            <CommandGroup>
                              {interests.map((interest) => (
                                <CommandItem
                                  value={interest.name}
                                  key={interest.id.toString()}
                                  onSelect={() => {
                                    const currentValues = new Set(field.value)
                                    if (currentValues.has(interest.id.toString())) {
                                      currentValues.delete(interest.id.toString())
                                    } else {
                                      currentValues.add(interest.id.toString())
                                    }
                                    field.onChange(Array.from(currentValues))
                                  }}
                                >
                                  <CheckIcon
                                    className={cn(
                                      "mr-2 h-4 w-4",
                                      field.value.includes(interest.id.toString()) ? "opacity-100" : "opacity-0",
                                    )}
                                  />
                                  {interest.name}
                                </CommandItem>
                              ))}
                            </CommandGroup>
                          </CommandList>
                        </Command>
                      </PopoverContent>
                    </Popover>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? "Submitting..." : "Register"}
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  )
}
