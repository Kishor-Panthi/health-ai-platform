"use client";

import React, { useMemo } from "react";
import {
  BarChart3,
  TrendingUp,
  Users,
  Calendar,
  DollarSign,
  Download,
  Filter,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
} from "recharts";
import {
  allMockAppointments,
  allMockPatients,
  allMockClaims,
  allMockReferrals,
  mockProviders,
} from "@/lib/utils/mockData";

export default function ReportsPage() {
  // Appointment Analytics
  const appointmentStats = useMemo(() => {
    const byStatus = allMockAppointments.reduce((acc, apt) => {
      acc[apt.status] = (acc[apt.status] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const byType = allMockAppointments.reduce((acc, apt) => {
      acc[apt.appointmentType] = (acc[apt.appointmentType] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const byProvider = mockProviders.map((provider) => ({
      name: `Dr. ${provider.lastName}`,
      appointments: allMockAppointments.filter(
        (apt) => apt.providerId === provider.id
      ).length,
    }));

    // Monthly trend (last 3 months)
    const monthlyTrend = Array.from({ length: 3 }, (_, i) => {
      const date = new Date();
      date.setMonth(date.getMonth() - (2 - i));
      const monthName = date.toLocaleString("default", { month: "short" });
      const count = allMockAppointments.filter((apt) => {
        const aptMonth = apt.date.getMonth();
        return aptMonth === date.getMonth();
      }).length;
      return { month: monthName, appointments: count };
    });

    return { byStatus, byType, byProvider, monthlyTrend };
  }, []);

  // Financial Analytics
  const financialStats = useMemo(() => {
    const totalBilled = allMockClaims.reduce((sum, c) => sum + c.billedAmount, 0);
    const totalCollected = allMockClaims.reduce((sum, c) => sum + c.paidAmount, 0);
    const collectionRate = (totalCollected / totalBilled) * 100;

    const monthlyRevenue = Array.from({ length: 3 }, (_, i) => {
      const date = new Date();
      date.setMonth(date.getMonth() - (2 - i));
      const monthName = date.toLocaleString("default", { month: "short" });
      const billed = allMockClaims
        .filter((c) => c.serviceDate.getMonth() === date.getMonth())
        .reduce((sum, c) => sum + c.billedAmount, 0);
      const collected = allMockClaims
        .filter((c) => c.serviceDate.getMonth() === date.getMonth())
        .reduce((sum, c) => sum + c.paidAmount, 0);
      return { month: monthName, billed, collected };
    });

    const byPayer = allMockClaims.reduce((acc, claim) => {
      const payer = claim.insurancePayer;
      if (!acc[payer]) {
        acc[payer] = { billed: 0, paid: 0, count: 0 };
      }
      acc[payer].billed += claim.billedAmount;
      acc[payer].paid += claim.paidAmount;
      acc[payer].count += 1;
      return acc;
    }, {} as Record<string, { billed: number; paid: number; count: number }>);

    return { totalBilled, totalCollected, collectionRate, monthlyRevenue, byPayer };
  }, []);

  // Patient Analytics
  const patientStats = useMemo(() => {
    const total = allMockPatients.length;
    const active = allMockPatients.filter((p) => p.status === "active").length;
    const newThisMonth = allMockPatients.filter((p) => {
      const createdMonth = p.createdAt.getMonth();
      return createdMonth === new Date().getMonth();
    }).length;

    const ageGroups = [
      { name: "0-17", min: 0, max: 17 },
      { name: "18-34", min: 18, max: 34 },
      { name: "35-54", min: 35, max: 54 },
      { name: "55-74", min: 55, max: 74 },
      { name: "75+", min: 75, max: 150 },
    ];

    const byAgeGroup = ageGroups.map((group) => {
      const count = allMockPatients.filter((p) => {
        const age = new Date().getFullYear() - p.dateOfBirth.getFullYear();
        return age >= group.min && age <= group.max;
      }).length;
      return { name: group.name, value: count };
    });

    const byGender = [
      {
        name: "Male",
        value: allMockPatients.filter((p) => p.gender === "male").length,
      },
      {
        name: "Female",
        value: allMockPatients.filter((p) => p.gender === "female").length,
      },
    ];

    return { total, active, newThisMonth, byAgeGroup, byGender };
  }, []);

  // Provider Productivity
  const providerStats = useMemo(() => {
    return mockProviders.map((provider) => {
      const appointments = allMockAppointments.filter(
        (apt) => apt.providerId === provider.id
      );
      const completed = appointments.filter((apt) => apt.status === "completed").length;
      const noShows = appointments.filter((apt) => apt.status === "no-show").length;
      const revenue = allMockClaims
        .filter((c) => c.providerId === provider.id && c.status === "paid")
        .reduce((sum, c) => sum + c.paidAmount, 0);

      return {
        name: `Dr. ${provider.lastName}`,
        appointments: appointments.length,
        completed,
        noShows,
        revenue,
      };
    });
  }, []);

  const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ef4444"];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Reports & Analytics
          </h1>
          <p className="text-muted-foreground">
            Practice performance insights and metrics
          </p>
        </div>
        <div className="flex gap-2">
          <Select defaultValue="90days">
            <SelectTrigger className="w-[150px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="30days">Last 30 Days</SelectItem>
              <SelectItem value="90days">Last 90 Days</SelectItem>
              <SelectItem value="1year">Last Year</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
        </div>
      </div>

      {/* Executive Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Total Patients
              </p>
              <p className="text-2xl font-bold">{patientStats.total}</p>
              <p className="text-xs text-green-600 mt-1">
                +{patientStats.newThisMonth} this month
              </p>
            </div>
            <Users className="h-8 w-8 text-muted-foreground" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Appointments
              </p>
              <p className="text-2xl font-bold">{allMockAppointments.length}</p>
              <p className="text-xs text-muted-foreground mt-1">All time</p>
            </div>
            <Calendar className="h-8 w-8 text-muted-foreground" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Revenue Collected
              </p>
              <p className="text-2xl font-bold">
                ${financialStats.totalCollected.toLocaleString()}
              </p>
              <p className="text-xs text-green-600 mt-1">
                {financialStats.collectionRate.toFixed(1)}% collection rate
              </p>
            </div>
            <DollarSign className="h-8 w-8 text-muted-foreground" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Active Referrals
              </p>
              <p className="text-2xl font-bold">
                {
                  allMockReferrals.filter(
                    (r) => r.status !== "completed" && r.status !== "cancelled"
                  ).length
                }
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                {allMockReferrals.filter((r) => r.status === "completed").length}{" "}
                completed
              </p>
            </div>
            <TrendingUp className="h-8 w-8 text-muted-foreground" />
          </div>
        </Card>
      </div>

      {/* Detailed Analytics */}
      <Tabs defaultValue="appointments" className="space-y-4">
        <TabsList>
          <TabsTrigger value="appointments">Appointments</TabsTrigger>
          <TabsTrigger value="financial">Financial</TabsTrigger>
          <TabsTrigger value="patients">Patients</TabsTrigger>
          <TabsTrigger value="providers">Providers</TabsTrigger>
        </TabsList>

        {/* Appointment Analytics */}
        <TabsContent value="appointments" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Monthly Trend</h3>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={appointmentStats.monthlyTrend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Area
                    type="monotone"
                    dataKey="appointments"
                    stroke="#3b82f6"
                    fill="#3b82f6"
                    fillOpacity={0.6}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">By Provider</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={appointmentStats.byProvider}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="appointments" fill="#10b981" />
                </BarChart>
              </ResponsiveContainer>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">By Status</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={Object.entries(appointmentStats.byStatus).map(
                      ([name, value]) => ({ name, value })
                    )}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry) => `${entry.name}: ${entry.value}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {Object.keys(appointmentStats.byStatus).map((_, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={COLORS[index % COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">By Type</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={Object.entries(appointmentStats.byType).map(
                    ([name, value]) => ({ name, value })
                  )}
                  layout="vertical"
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="name" type="category" />
                  <Tooltip />
                  <Bar dataKey="value" fill="#8b5cf6" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </div>
        </TabsContent>

        {/* Financial Analytics */}
        <TabsContent value="financial" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">
                Revenue Trend (3 Months)
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={financialStats.monthlyRevenue}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="billed"
                    stroke="#3b82f6"
                    name="Billed"
                  />
                  <Line
                    type="monotone"
                    dataKey="collected"
                    stroke="#10b981"
                    name="Collected"
                  />
                </LineChart>
              </ResponsiveContainer>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">By Insurance Payer</h3>
              <div className="space-y-3 max-h-[300px] overflow-y-auto">
                {Object.entries(financialStats.byPayer)
                  .sort((a, b) => b[1].paid - a[1].paid)
                  .slice(0, 10)
                  .map(([payer, data]) => (
                    <div key={payer} className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span className="font-medium">{payer}</span>
                        <span className="text-green-600">
                          ${data.paid.toLocaleString()}
                        </span>
                      </div>
                      <div className="flex justify-between text-xs text-muted-foreground">
                        <span>{data.count} claims</span>
                        <span>
                          {((data.paid / data.billed) * 100).toFixed(1)}%
                          collection
                        </span>
                      </div>
                      <div className="h-2 bg-muted rounded-full overflow-hidden">
                        <div
                          className="h-full bg-green-500"
                          style={{
                            width: `${(data.paid / data.billed) * 100}%`,
                          }}
                        />
                      </div>
                    </div>
                  ))}
              </div>
            </Card>
          </div>
        </TabsContent>

        {/* Patient Analytics */}
        <TabsContent value="patients" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Age Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={patientStats.byAgeGroup}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Gender Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={patientStats.byGender}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry) => `${entry.name}: ${entry.value}`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {patientStats.byGender.map((_, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={COLORS[index % COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Card>
          </div>
        </TabsContent>

        {/* Provider Productivity */}
        <TabsContent value="providers" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Provider Productivity</h3>
            <div className="space-y-4">
              {providerStats.map((provider) => (
                <div key={provider.name} className="border-b pb-4 last:border-0">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold">{provider.name}</h4>
                    <span className="text-sm text-green-600 font-medium">
                      ${provider.revenue.toLocaleString()} revenue
                    </span>
                  </div>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Appointments</p>
                      <p className="font-medium">{provider.appointments}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Completed</p>
                      <p className="font-medium">{provider.completed}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">No-Shows</p>
                      <p className="font-medium text-red-600">
                        {provider.noShows}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
