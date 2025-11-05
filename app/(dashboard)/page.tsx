"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Calendar,
  Users,
  DollarSign,
  TrendingUp,
  Clock,
  AlertCircle,
  Plus,
  Activity,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";

export default function DashboardPage() {
  // Mock data
  const metrics = [
    {
      title: "Today's Appointments",
      value: "12",
      change: "+2 from yesterday",
      icon: Calendar,
      trend: "up",
    },
    {
      title: "New Patients",
      value: "3",
      change: "This week",
      icon: Users,
      trend: "up",
    },
    {
      title: "Revenue (MTD)",
      value: "$45,231",
      change: "+12.5% from last month",
      icon: DollarSign,
      trend: "up",
    },
    {
      title: "Pending Tasks",
      value: "8",
      change: "3 urgent",
      icon: AlertCircle,
      trend: "down",
    },
  ];

  const upcomingAppointments = [
    {
      id: "1",
      time: "09:00 AM",
      patient: "John Doe",
      type: "Consultation",
      provider: "Dr. Smith",
      status: "confirmed",
    },
    {
      id: "2",
      time: "10:30 AM",
      patient: "Jane Smith",
      type: "Follow-up",
      provider: "Dr. Johnson",
      status: "checked-in",
    },
    {
      id: "3",
      time: "02:00 PM",
      patient: "Robert Brown",
      type: "Physical Exam",
      provider: "Dr. Smith",
      status: "scheduled",
    },
  ];

  const recentActivity = [
    {
      id: "1",
      action: "New appointment booked",
      patient: "Emily Davis",
      time: "5 minutes ago",
    },
    {
      id: "2",
      action: "Patient checked in",
      patient: "Michael Wilson",
      time: "15 minutes ago",
    },
    {
      id: "3",
      action: "Insurance verified",
      patient: "Sarah Anderson",
      time: "1 hour ago",
    },
    {
      id: "4",
      action: "Claim submitted",
      patient: "David Martinez",
      time: "2 hours ago",
    },
  ];

  const urgentItems = [
    {
      id: "1",
      type: "Lab Results",
      patient: "John Doe",
      priority: "high",
      due: "Today",
    },
    {
      id: "2",
      type: "Insurance Verification",
      patient: "Jane Smith",
      priority: "urgent",
      due: "Today",
    },
    {
      id: "3",
      type: "Prescription Refill",
      patient: "Robert Brown",
      priority: "high",
      due: "Tomorrow",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back! Here's what's happening today.
          </p>
        </div>
        <div className="flex gap-2">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Book Appointment
          </Button>
          <Button variant="outline">
            <Users className="mr-2 h-4 w-4" />
            Add Patient
          </Button>
        </div>
      </div>

      {/* Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {metrics.map((metric) => (
          <Card key={metric.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {metric.title}
              </CardTitle>
              <metric.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metric.value}</div>
              <p className="text-xs text-muted-foreground">{metric.change}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main content */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Upcoming Appointments */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Upcoming Appointments</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {upcomingAppointments.map((apt) => (
                <div
                  key={apt.id}
                  className="flex items-center justify-between border-b pb-4 last:border-0"
                >
                  <div className="flex items-center gap-3">
                    <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                      <Clock className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <p className="font-medium">{apt.patient}</p>
                      <p className="text-sm text-muted-foreground">
                        {apt.type} - {apt.provider}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">{apt.time}</p>
                    <Badge
                      variant={
                        apt.status === "checked-in"
                          ? "default"
                          : apt.status === "confirmed"
                          ? "secondary"
                          : "outline"
                      }
                      className="mt-1"
                    >
                      {apt.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
            <Button variant="outline" className="mt-4 w-full">
              View All Appointments
            </Button>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((activity) => (
                <div
                  key={activity.id}
                  className="flex items-center gap-3 border-b pb-4 last:border-0"
                >
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted">
                    <Activity className="h-4 w-4" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{activity.action}</p>
                    <p className="text-sm text-muted-foreground">
                      {activity.patient}
                    </p>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {activity.time}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Urgent Items */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Urgent Items Requiring Attention</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {urgentItems.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between rounded-lg border p-4"
                >
                  <div className="flex items-center gap-3">
                    <AlertCircle
                      className={`h-5 w-5 ${
                        item.priority === "urgent"
                          ? "text-destructive"
                          : "text-orange-500"
                      }`}
                    />
                    <div>
                      <p className="font-medium">{item.type}</p>
                      <p className="text-sm text-muted-foreground">
                        Patient: {item.patient}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Badge
                      variant={
                        item.priority === "urgent" ? "destructive" : "default"
                      }
                    >
                      {item.priority}
                    </Badge>
                    <p className="text-sm text-muted-foreground">
                      Due: {item.due}
                    </p>
                    <Button size="sm">Review</Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
