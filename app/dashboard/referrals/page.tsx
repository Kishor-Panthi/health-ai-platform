"use client";

import React, { useState, useMemo } from "react";
import {
  Send,
  Users,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  Search,
  Filter,
  Plus,
  FileText,
  User,
  Calendar,
  Phone,
  Mail,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  allMockReferrals,
  mockSpecialists,
  allMockPatients,
  mockProviders,
} from "@/lib/utils/mockData";
import type { Referral } from "@/lib/types";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";

export default function ReferralsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [selectedReferral, setSelectedReferral] = useState<Referral | null>(
    null
  );
  const [showNewReferral, setShowNewReferral] = useState(false);

  // Filter referrals
  const filteredReferrals = useMemo(() => {
    let filtered = allMockReferrals;

    // Status filter
    if (statusFilter !== "all") {
      filtered = filtered.filter((r) => r.status === statusFilter);
    }

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (r) =>
          r.patientName.toLowerCase().includes(query) ||
          r.specialistName.toLowerCase().includes(query) ||
          r.specialty.toLowerCase().includes(query) ||
          r.reason.toLowerCase().includes(query)
      );
    }

    return filtered;
  }, [searchQuery, statusFilter]);

  // Group by status for Kanban view
  const groupedReferrals = useMemo(() => {
    return {
      pending: filteredReferrals.filter((r) => r.status === "pending"),
      sent: filteredReferrals.filter((r) => r.status === "sent"),
      accepted: filteredReferrals.filter((r) => r.status === "accepted"),
      completed: filteredReferrals.filter((r) => r.status === "completed"),
      declined: filteredReferrals.filter((r) => r.status === "declined"),
      cancelled: filteredReferrals.filter((r) => r.status === "cancelled"),
    };
  }, [filteredReferrals]);

  const getStatusIcon = (status: Referral["status"]) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "accepted":
        return <CheckCircle className="h-4 w-4 text-blue-500" />;
      case "sent":
        return <Send className="h-4 w-4 text-blue-500" />;
      case "declined":
        return <XCircle className="h-4 w-4 text-red-500" />;
      case "cancelled":
        return <XCircle className="h-4 w-4 text-gray-500" />;
      default:
        return <Clock className="h-4 w-4 text-orange-500" />;
    }
  };

  const getPriorityBadge = (priority: Referral["priority"]) => {
    const variants: Record<
      Referral["priority"],
      { variant: "default" | "destructive" | "secondary"; label: string }
    > = {
      routine: { variant: "secondary", label: "Routine" },
      urgent: { variant: "default", label: "Urgent" },
      stat: { variant: "destructive", label: "STAT" },
    };
    const config = variants[priority];
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Referrals</h1>
          <p className="text-muted-foreground">
            Manage specialist referrals and track outcomes
          </p>
        </div>
        <Button onClick={() => setShowNewReferral(true)}>
          <Plus className="mr-2 h-4 w-4" />
          New Referral
        </Button>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-6">
        <Card className="p-6">
          <div className="text-2xl font-bold">{allMockReferrals.length}</div>
          <p className="text-sm text-muted-foreground">Total</p>
        </Card>
        <Card className="p-6">
          <div className="text-2xl font-bold text-orange-600">
            {groupedReferrals.pending.length}
          </div>
          <p className="text-sm text-muted-foreground">Pending</p>
        </Card>
        <Card className="p-6">
          <div className="text-2xl font-bold text-blue-600">
            {groupedReferrals.sent.length}
          </div>
          <p className="text-sm text-muted-foreground">Sent</p>
        </Card>
        <Card className="p-6">
          <div className="text-2xl font-bold text-blue-600">
            {groupedReferrals.accepted.length}
          </div>
          <p className="text-sm text-muted-foreground">Accepted</p>
        </Card>
        <Card className="p-6">
          <div className="text-2xl font-bold text-green-600">
            {groupedReferrals.completed.length}
          </div>
          <p className="text-sm text-muted-foreground">Completed</p>
        </Card>
        <Card className="p-6">
          <div className="text-2xl font-bold text-red-600">
            {groupedReferrals.declined.length}
          </div>
          <p className="text-sm text-muted-foreground">Declined</p>
        </Card>
      </div>

      {/* Search and Filters */}
      <Card className="p-4">
        <div className="flex flex-col gap-4 md:flex-row md:items-center">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search by patient, specialist, or specialty..."
              className="pl-9"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-muted-foreground" />
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="sent">Sent</SelectItem>
                <SelectItem value="accepted">Accepted</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="declined">Declined</SelectItem>
                <SelectItem value="cancelled">Cancelled</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </Card>

      {/* Kanban Board */}
      <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-4">
        {/* Pending Column */}
        <Card className="p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold flex items-center gap-2">
              <Clock className="h-4 w-4 text-orange-500" />
              Pending ({groupedReferrals.pending.length})
            </h3>
          </div>
          <div className="space-y-3 max-h-[600px] overflow-y-auto">
            {groupedReferrals.pending.map((referral) => (
              <Card
                key={referral.id}
                className="p-3 cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => setSelectedReferral(referral)}
              >
                <div className="space-y-2">
                  <div className="flex items-start justify-between">
                    <p className="font-medium text-sm">
                      {referral.patientName}
                    </p>
                    {getPriorityBadge(referral.priority)}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {referral.specialty}
                  </p>
                  <p className="text-xs text-muted-foreground line-clamp-2">
                    {referral.reason}
                  </p>
                  <div className="text-xs text-muted-foreground">
                    {referral.createdAt.toLocaleDateString()}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </Card>

        {/* Sent/Accepted Column */}
        <Card className="p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold flex items-center gap-2">
              <Send className="h-4 w-4 text-blue-500" />
              In Progress (
              {groupedReferrals.sent.length + groupedReferrals.accepted.length})
            </h3>
          </div>
          <div className="space-y-3 max-h-[600px] overflow-y-auto">
            {[...groupedReferrals.sent, ...groupedReferrals.accepted].map(
              (referral) => (
                <Card
                  key={referral.id}
                  className="p-3 cursor-pointer hover:shadow-md transition-shadow"
                  onClick={() => setSelectedReferral(referral)}
                >
                  <div className="space-y-2">
                    <div className="flex items-start justify-between">
                      <p className="font-medium text-sm">
                        {referral.patientName}
                      </p>
                      <Badge variant="secondary">{referral.status}</Badge>
                    </div>
                    <p className="text-xs font-medium">
                      {referral.specialistName}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {referral.specialty}
                    </p>
                    <p className="text-xs text-muted-foreground line-clamp-2">
                      {referral.reason}
                    </p>
                    {referral.sentAt && (
                      <div className="text-xs text-muted-foreground">
                        Sent: {referral.sentAt.toLocaleDateString()}
                      </div>
                    )}
                  </div>
                </Card>
              )
            )}
          </div>
        </Card>

        {/* Completed Column */}
        <Card className="p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              Completed ({groupedReferrals.completed.length})
            </h3>
          </div>
          <div className="space-y-3 max-h-[600px] overflow-y-auto">
            {groupedReferrals.completed.map((referral) => (
              <Card
                key={referral.id}
                className="p-3 cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => setSelectedReferral(referral)}
              >
                <div className="space-y-2">
                  <div className="flex items-start justify-between">
                    <p className="font-medium text-sm">
                      {referral.patientName}
                    </p>
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  </div>
                  <p className="text-xs font-medium">
                    {referral.specialistName}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {referral.specialty}
                  </p>
                  {referral.completedAt && (
                    <div className="text-xs text-muted-foreground">
                      {referral.completedAt.toLocaleDateString()}
                    </div>
                  )}
                </div>
              </Card>
            ))}
          </div>
        </Card>

        {/* Declined/Cancelled Column */}
        <Card className="p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold flex items-center gap-2">
              <XCircle className="h-4 w-4 text-red-500" />
              Closed (
              {groupedReferrals.declined.length +
                groupedReferrals.cancelled.length}
              )
            </h3>
          </div>
          <div className="space-y-3 max-h-[600px] overflow-y-auto">
            {[...groupedReferrals.declined, ...groupedReferrals.cancelled].map(
              (referral) => (
                <Card
                  key={referral.id}
                  className="p-3 cursor-pointer hover:shadow-md transition-shadow opacity-75"
                  onClick={() => setSelectedReferral(referral)}
                >
                  <div className="space-y-2">
                    <div className="flex items-start justify-between">
                      <p className="font-medium text-sm">
                        {referral.patientName}
                      </p>
                      <Badge variant="destructive">{referral.status}</Badge>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {referral.specialty}
                    </p>
                    <p className="text-xs text-muted-foreground line-clamp-2">
                      {referral.reason}
                    </p>
                  </div>
                </Card>
              )
            )}
          </div>
        </Card>
      </div>

      {/* Referral Detail Dialog */}
      {selectedReferral && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-2xl p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex items-start justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold mb-2">Referral Details</h2>
                <div className="flex items-center gap-2">
                  {getStatusIcon(selectedReferral.status)}
                  <Badge>{selectedReferral.status}</Badge>
                  {getPriorityBadge(selectedReferral.priority)}
                </div>
              </div>
            </div>

            <div className="space-y-6">
              {/* Patient Information */}
              <div>
                <h3 className="font-semibold mb-3 flex items-center gap-2">
                  <User className="h-4 w-4" />
                  Patient Information
                </h3>
                <div className="grid gap-3 md:grid-cols-2">
                  <div className="p-3 bg-muted/50 rounded">
                    <p className="text-sm text-muted-foreground">Name</p>
                    <p className="font-medium">{selectedReferral.patientName}</p>
                  </div>
                  <div className="p-3 bg-muted/50 rounded">
                    <p className="text-sm text-muted-foreground">
                      Referring Provider
                    </p>
                    <p className="font-medium">
                      {selectedReferral.referringProviderName}
                    </p>
                  </div>
                </div>
              </div>

              {/* Specialist Information */}
              <div>
                <h3 className="font-semibold mb-3 flex items-center gap-2">
                  <Users className="h-4 w-4" />
                  Specialist Information
                </h3>
                <div className="grid gap-3 md:grid-cols-2">
                  <div className="p-3 bg-muted/50 rounded">
                    <p className="text-sm text-muted-foreground">Name</p>
                    <p className="font-medium">
                      {selectedReferral.specialistName}
                    </p>
                  </div>
                  <div className="p-3 bg-muted/50 rounded">
                    <p className="text-sm text-muted-foreground">Specialty</p>
                    <p className="font-medium">{selectedReferral.specialty}</p>
                  </div>
                </div>
              </div>

              {/* Referral Details */}
              <div>
                <h3 className="font-semibold mb-3 flex items-center gap-2">
                  <FileText className="h-4 w-4" />
                  Referral Details
                </h3>
                <div className="space-y-3">
                  <div className="p-3 bg-muted/50 rounded">
                    <p className="text-sm text-muted-foreground mb-1">Reason</p>
                    <p className="font-medium">{selectedReferral.reason}</p>
                  </div>
                  {selectedReferral.notes && (
                    <div className="p-3 bg-muted/50 rounded">
                      <p className="text-sm text-muted-foreground mb-1">Notes</p>
                      <p className="text-sm">{selectedReferral.notes}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Timeline */}
              <div>
                <h3 className="font-semibold mb-3 flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  Timeline
                </h3>
                <div className="space-y-2">
                  <div className="flex items-center gap-3 p-3 bg-muted/50 rounded">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium">Created</p>
                      <p className="text-sm text-muted-foreground">
                        {selectedReferral.createdAt.toLocaleString()}
                      </p>
                    </div>
                  </div>
                  {selectedReferral.sentAt && (
                    <div className="flex items-center gap-3 p-3 bg-muted/50 rounded">
                      <Send className="h-4 w-4 text-blue-500" />
                      <div>
                        <p className="text-sm font-medium">Sent</p>
                        <p className="text-sm text-muted-foreground">
                          {selectedReferral.sentAt.toLocaleString()}
                        </p>
                      </div>
                    </div>
                  )}
                  {selectedReferral.completedAt && (
                    <div className="flex items-center gap-3 p-3 bg-muted/50 rounded">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <div>
                        <p className="text-sm font-medium">Completed</p>
                        <p className="text-sm text-muted-foreground">
                          {selectedReferral.completedAt.toLocaleString()}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-2 mt-6 pt-6 border-t">
              <Button
                variant="outline"
                onClick={() => setSelectedReferral(null)}
              >
                Close
              </Button>
              {selectedReferral.status === "pending" && (
                <Button>Send Referral</Button>
              )}
            </div>
          </Card>
        </div>
      )}

      {/* New Referral Dialog */}
      {showNewReferral && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-2xl p-6 max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-6">Create New Referral</h2>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                alert("Referral created! (mock)");
                setShowNewReferral(false);
              }}
              className="space-y-4"
            >
              <div className="space-y-2">
                <Label>Patient *</Label>
                <Select required>
                  <SelectTrigger>
                    <SelectValue placeholder="Select patient..." />
                  </SelectTrigger>
                  <SelectContent>
                    {allMockPatients.slice(0, 20).map((patient) => (
                      <SelectItem key={patient.id} value={patient.id}>
                        {patient.firstName} {patient.lastName} ({patient.mrn})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Specialist *</Label>
                <Select required>
                  <SelectTrigger>
                    <SelectValue placeholder="Select specialist..." />
                  </SelectTrigger>
                  <SelectContent>
                    {mockSpecialists.map((specialist) => (
                      <SelectItem key={specialist.id} value={specialist.id}>
                        Dr. {specialist.firstName} {specialist.lastName} -{" "}
                        {specialist.specialty}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Priority *</Label>
                <Select defaultValue="routine" required>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="routine">Routine</SelectItem>
                    <SelectItem value="urgent">Urgent</SelectItem>
                    <SelectItem value="stat">STAT</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Reason for Referral *</Label>
                <Input
                  required
                  placeholder="e.g., Chest pain evaluation"
                />
              </div>

              <div className="space-y-2">
                <Label>Notes</Label>
                <Textarea
                  placeholder="Additional notes for the specialist..."
                  rows={4}
                />
              </div>

              <div className="flex justify-end gap-2 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowNewReferral(false)}
                >
                  Cancel
                </Button>
                <Button type="submit">
                  <Send className="mr-2 h-4 w-4" />
                  Create Referral
                </Button>
              </div>
            </form>
          </Card>
        </div>
      )}
    </div>
  );
}
