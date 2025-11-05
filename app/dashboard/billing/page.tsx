"use client";

import React, { useState, useMemo } from "react";
import {
  DollarSign,
  FileText,
  TrendingUp,
  AlertCircle,
  Search,
  Filter,
  Plus,
  Download,
  CheckCircle,
  XCircle,
  Clock,
  Send,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { allMockClaims, cptCodes, icd10Codes } from "@/lib/utils/mockData";
import type { Claim } from "@/lib/types";

export default function BillingPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [selectedClaim, setSelectedClaim] = useState<Claim | null>(null);
  const [showNewClaim, setShowNewClaim] = useState(false);

  // Filter claims
  const filteredClaims = useMemo(() => {
    let filtered = allMockClaims;

    // Status filter
    if (statusFilter !== "all") {
      filtered = filtered.filter((c) => c.status === statusFilter);
    }

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (c) =>
          c.claimNumber.toLowerCase().includes(query) ||
          c.patientName.toLowerCase().includes(query) ||
          c.providerName.toLowerCase().includes(query)
      );
    }

    return filtered;
  }, [searchQuery, statusFilter]);

  // Calculate financial stats
  const stats = useMemo(() => {
    const totalBilled = allMockClaims.reduce((sum, c) => sum + c.billedAmount, 0);
    const totalPaid = allMockClaims.reduce((sum, c) => sum + c.paidAmount, 0);
    const totalPending = allMockClaims
      .filter((c) => c.status === "submitted" || c.status === "accepted")
      .reduce((sum, c) => sum + (c.billedAmount - c.paidAmount), 0);
    const totalRejected = allMockClaims
      .filter((c) => c.status === "rejected")
      .reduce((sum, c) => sum + c.billedAmount, 0);

    return { totalBilled, totalPaid, totalPending, totalRejected };
  }, []);

  const getStatusIcon = (status: Claim["status"]) => {
    switch (status) {
      case "paid":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "accepted":
        return <CheckCircle className="h-4 w-4 text-blue-500" />;
      case "submitted":
        return <Send className="h-4 w-4 text-blue-500" />;
      case "rejected":
        return <XCircle className="h-4 w-4 text-red-500" />;
      case "draft":
        return <FileText className="h-4 w-4 text-gray-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: Claim["status"]) => {
    const variants: Record<Claim["status"], "default" | "secondary" | "destructive"> = {
      paid: "default",
      accepted: "default",
      submitted: "secondary",
      rejected: "destructive",
      draft: "secondary",
      appealed: "secondary",
    };
    return <Badge variant={variants[status]}>{status}</Badge>;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Billing & Claims</h1>
          <p className="text-muted-foreground">
            Manage claims, payments, and revenue cycle
          </p>
        </div>
        <Button onClick={() => setShowNewClaim(true)}>
          <Plus className="mr-2 h-4 w-4" />
          New Claim
        </Button>
      </div>

      {/* Financial Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Total Billed
              </p>
              <p className="text-2xl font-bold">
                ${stats.totalBilled.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
            </div>
            <DollarSign className="h-8 w-8 text-muted-foreground" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Total Collected
              </p>
              <p className="text-2xl font-bold text-green-600">
                ${stats.totalPaid.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
            </div>
            <TrendingUp className="h-8 w-8 text-green-600" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Pending
              </p>
              <p className="text-2xl font-bold text-orange-600">
                ${stats.totalPending.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
            </div>
            <Clock className="h-8 w-8 text-orange-600" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Rejected
              </p>
              <p className="text-2xl font-bold text-red-600">
                ${stats.totalRejected.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
            </div>
            <AlertCircle className="h-8 w-8 text-red-600" />
          </div>
        </Card>
      </div>

      {/* Search and Filters */}
      <Card className="p-4">
        <div className="flex flex-col gap-4 md:flex-row md:items-center">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search by claim number, patient, or provider..."
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
                <SelectItem value="draft">Draft</SelectItem>
                <SelectItem value="submitted">Submitted</SelectItem>
                <SelectItem value="accepted">Accepted</SelectItem>
                <SelectItem value="rejected">Rejected</SelectItem>
                <SelectItem value="paid">Paid</SelectItem>
                <SelectItem value="appealed">Appealed</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
        </div>
      </Card>

      {/* Claims Tabs */}
      <Tabs defaultValue="claims">
        <TabsList>
          <TabsTrigger value="claims">Claims</TabsTrigger>
          <TabsTrigger value="codes">CPT/ICD Codes</TabsTrigger>
          <TabsTrigger value="reports">Reports</TabsTrigger>
        </TabsList>

        <TabsContent value="claims" className="space-y-4">
          <Card>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Claim #</TableHead>
                  <TableHead>Patient</TableHead>
                  <TableHead>Provider</TableHead>
                  <TableHead>Service Date</TableHead>
                  <TableHead>Billed</TableHead>
                  <TableHead>Paid</TableHead>
                  <TableHead>Balance</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredClaims.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={9} className="text-center h-24">
                      <div className="flex flex-col items-center justify-center text-muted-foreground">
                        <p>No claims found</p>
                      </div>
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredClaims.slice(0, 50).map((claim) => (
                    <TableRow
                      key={claim.id}
                      className="cursor-pointer hover:bg-muted/50"
                      onClick={() => setSelectedClaim(claim)}
                    >
                      <TableCell className="font-mono text-sm">
                        {claim.claimNumber}
                      </TableCell>
                      <TableCell>{claim.patientName}</TableCell>
                      <TableCell>{claim.providerName}</TableCell>
                      <TableCell>
                        {claim.serviceDate.toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        ${claim.billedAmount.toFixed(2)}
                      </TableCell>
                      <TableCell className="text-green-600">
                        ${claim.paidAmount.toFixed(2)}
                      </TableCell>
                      <TableCell>
                        ${(claim.billedAmount - claim.paidAmount).toFixed(2)}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {getStatusIcon(claim.status)}
                          {getStatusBadge(claim.status)}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedClaim(claim);
                          }}
                        >
                          View
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
            {filteredClaims.length > 50 && (
              <div className="p-4 text-center text-sm text-muted-foreground border-t">
                Showing first 50 of {filteredClaims.length} claims
              </div>
            )}
          </Card>
        </TabsContent>

        <TabsContent value="codes">
          <div className="grid gap-4 md:grid-cols-2">
            {/* CPT Codes */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">CPT Codes</h3>
              <div className="space-y-2 max-h-[500px] overflow-y-auto">
                {cptCodes.map((code) => (
                  <div
                    key={code.code}
                    className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50"
                  >
                    <div className="flex-1">
                      <p className="font-mono font-semibold">{code.code}</p>
                      <p className="text-sm text-muted-foreground">
                        {code.description}
                      </p>
                    </div>
                    <Badge variant="outline">${code.fee}</Badge>
                  </div>
                ))}
              </div>
            </Card>

            {/* ICD-10 Codes */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">ICD-10 Codes</h3>
              <div className="space-y-2 max-h-[500px] overflow-y-auto">
                {icd10Codes.map((code) => (
                  <div
                    key={code.code}
                    className="flex items-start gap-3 p-3 border rounded-lg hover:bg-muted/50"
                  >
                    <Badge variant="secondary" className="font-mono mt-0.5">
                      {code.code}
                    </Badge>
                    <p className="text-sm text-muted-foreground flex-1">
                      {code.description}
                    </p>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="reports">
          <Card className="p-6">
            <div className="text-center py-12">
              <TrendingUp className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">Financial Reports</h3>
              <p className="text-muted-foreground mb-4">
                Advanced reporting and analytics coming soon
              </p>
              <Button variant="outline">
                <Download className="mr-2 h-4 w-4" />
                Export Current Data
              </Button>
            </div>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Claim Detail Dialog */}
      {selectedClaim && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-3xl p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex items-start justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold mb-1">Claim Details</h2>
                <p className="text-muted-foreground font-mono">
                  {selectedClaim.claimNumber}
                </p>
              </div>
              <div className="flex items-center gap-2">
                {getStatusIcon(selectedClaim.status)}
                {getStatusBadge(selectedClaim.status)}
              </div>
            </div>

            <div className="space-y-6">
              {/* Patient & Provider Info */}
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <h3 className="font-semibold">Patient Information</h3>
                  <p className="text-sm">
                    <span className="text-muted-foreground">Name:</span>{" "}
                    {selectedClaim.patientName}
                  </p>
                </div>
                <div className="space-y-2">
                  <h3 className="font-semibold">Provider Information</h3>
                  <p className="text-sm">
                    <span className="text-muted-foreground">Name:</span>{" "}
                    {selectedClaim.providerName}
                  </p>
                </div>
              </div>

              {/* Financial Summary */}
              <div className="border-t pt-6">
                <h3 className="font-semibold mb-4">Financial Summary</h3>
                <div className="grid gap-3 md:grid-cols-2">
                  <div className="flex justify-between p-3 bg-muted/50 rounded">
                    <span className="text-sm">Service Date:</span>
                    <span className="font-medium">
                      {selectedClaim.serviceDate.toLocaleDateString()}
                    </span>
                  </div>
                  {selectedClaim.submittedDate && (
                    <div className="flex justify-between p-3 bg-muted/50 rounded">
                      <span className="text-sm">Submitted:</span>
                      <span className="font-medium">
                        {selectedClaim.submittedDate.toLocaleDateString()}
                      </span>
                    </div>
                  )}
                  <div className="flex justify-between p-3 bg-muted/50 rounded">
                    <span className="text-sm">Billed Amount:</span>
                    <span className="font-medium">
                      ${selectedClaim.billedAmount.toFixed(2)}
                    </span>
                  </div>
                  <div className="flex justify-between p-3 bg-muted/50 rounded">
                    <span className="text-sm">Allowed Amount:</span>
                    <span className="font-medium">
                      ${selectedClaim.allowedAmount.toFixed(2)}
                    </span>
                  </div>
                  <div className="flex justify-between p-3 bg-green-50 rounded">
                    <span className="text-sm">Paid Amount:</span>
                    <span className="font-medium text-green-600">
                      ${selectedClaim.paidAmount.toFixed(2)}
                    </span>
                  </div>
                  <div className="flex justify-between p-3 bg-orange-50 rounded">
                    <span className="text-sm">Patient Responsibility:</span>
                    <span className="font-medium text-orange-600">
                      ${selectedClaim.patientResponsibility.toFixed(2)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Diagnosis Codes */}
              <div className="border-t pt-6">
                <h3 className="font-semibold mb-4">Diagnosis Codes</h3>
                <div className="space-y-2">
                  {selectedClaim.diagnosisCodes.map((dx, idx) => (
                    <div key={idx} className="flex items-start gap-3 p-3 border rounded">
                      <Badge variant={dx.isPrimary ? "default" : "secondary"}>
                        {dx.code}
                      </Badge>
                      <div className="flex-1">
                        <p className="text-sm">{dx.description}</p>
                        {dx.isPrimary && (
                          <Badge variant="outline" className="mt-1 text-xs">
                            Primary
                          </Badge>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Procedure Codes */}
              <div className="border-t pt-6">
                <h3 className="font-semibold mb-4">Procedure Codes</h3>
                <div className="space-y-2">
                  {selectedClaim.procedureCodes.map((proc, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 border rounded">
                      <div className="flex items-center gap-3">
                        <Badge variant="secondary">{proc.code}</Badge>
                        <span className="text-sm">{proc.description}</span>
                      </div>
                      <div className="text-right text-sm">
                        <p className="text-muted-foreground">
                          Qty: {proc.quantity} × ${proc.unitPrice.toFixed(2)}
                        </p>
                        <p className="font-medium">
                          ${(proc.quantity * proc.unitPrice).toFixed(2)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-2 mt-6 pt-6 border-t">
              <Button
                variant="outline"
                onClick={() => setSelectedClaim(null)}
              >
                Close
              </Button>
              {selectedClaim.status === "draft" && (
                <Button>Submit Claim</Button>
              )}
              {selectedClaim.status === "rejected" && (
                <Button variant="destructive">Appeal Claim</Button>
              )}
            </div>
          </Card>
        </div>
      )}

      {/* New Claim Dialog */}
      {showNewClaim && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-2xl p-6">
            <h2 className="text-2xl font-bold mb-6">Create New Claim</h2>
            <div className="text-center py-12">
              <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground mb-4">
                Claim creation wizard will be implemented here
              </p>
              <p className="text-sm text-muted-foreground">
                This would include patient selection, procedure codes, diagnosis
                codes, and insurance verification
              </p>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setShowNewClaim(false)}>
                Cancel
              </Button>
              <Button onClick={() => setShowNewClaim(false)}>
                Create Claim
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
