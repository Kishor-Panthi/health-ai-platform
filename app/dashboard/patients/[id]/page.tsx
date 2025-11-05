"use client";

import React from "react";
import { useRouter } from "next/navigation";
import {
  ArrowLeft,
  Mail,
  Phone,
  MapPin,
  Calendar,
  User,
  CreditCard,
  FileText,
  Edit,
  Activity,
  AlertCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { allMockPatients, allMockAppointments } from "@/lib/utils/mockData";
import type { Patient } from "@/lib/types";

interface PatientDetailPageProps {
  params: {
    id: string;
  };
}

export default function PatientDetailPage({ params }: PatientDetailPageProps) {
  const router = useRouter();
  const patient = allMockPatients.find((p) => p.id === params.id);

  if (!patient) {
    return (
      <div className="flex flex-col items-center justify-center h-[400px]">
        <AlertCircle className="h-12 w-12 text-muted-foreground mb-4" />
        <h2 className="text-2xl font-bold mb-2">Patient Not Found</h2>
        <p className="text-muted-foreground mb-4">
          The patient you're looking for doesn't exist.
        </p>
        <Button onClick={() => router.push("/dashboard/patients")}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Patients
        </Button>
      </div>
    );
  }

  const patientAppointments = allMockAppointments.filter(
    (apt) => apt.patientId === patient.id
  );

  const calculateAge = (dob: Date) => {
    const today = new Date();
    const birthDate = new Date(dob);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (
      monthDiff < 0 ||
      (monthDiff === 0 && today.getDate() < birthDate.getDate())
    ) {
      age--;
    }
    return age;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => router.push("/dashboard/patients")}
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              {patient.firstName} {patient.lastName}
            </h1>
            <p className="text-muted-foreground">MRN: {patient.mrn}</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Calendar className="mr-2 h-4 w-4" />
            Book Appointment
          </Button>
          <Button>
            <Edit className="mr-2 h-4 w-4" />
            Edit Patient
          </Button>
        </div>
      </div>

      {/* Patient Overview */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="p-6">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
              <User className="h-6 w-6 text-primary" />
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Demographics
              </p>
              <p className="text-lg font-semibold">
                {calculateAge(patient.dateOfBirth)} years,{" "}
                {patient.gender === "male" ? "Male" : "Female"}
              </p>
            </div>
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-green-500/10">
              <Activity className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Status
              </p>
              <Badge variant={patient.status === "active" ? "default" : "secondary"}>
                {patient.status}
              </Badge>
            </div>
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-500/10">
              <Calendar className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Total Appointments
              </p>
              <p className="text-lg font-semibold">
                {patientAppointments.length}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="appointments">
            Appointments ({patientAppointments.length})
          </TabsTrigger>
          <TabsTrigger value="insurance">Insurance</TabsTrigger>
          <TabsTrigger value="documents">Documents</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* Contact Information */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Phone className="h-5 w-5" />
                Contact Information
              </h3>
              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <Mail className="h-4 w-4 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Email</p>
                    <p className="text-sm text-muted-foreground">
                      {patient.email}
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Phone className="h-4 w-4 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Phone</p>
                    <p className="text-sm text-muted-foreground">
                      {patient.phone}
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <MapPin className="h-4 w-4 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Address</p>
                    <p className="text-sm text-muted-foreground">
                      {patient.address.street}
                      <br />
                      {patient.address.city}, {patient.address.state}{" "}
                      {patient.address.zipCode}
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <User className="h-4 w-4 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">
                      Communication Preference
                    </p>
                    <Badge variant="outline">
                      {patient.communicationPreference}
                    </Badge>
                  </div>
                </div>
              </div>
            </Card>

            {/* Emergency Contact */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <AlertCircle className="h-5 w-5" />
                Emergency Contact
              </h3>
              <div className="space-y-3">
                <div>
                  <p className="text-sm font-medium">Name</p>
                  <p className="text-sm text-muted-foreground">
                    {patient.emergencyContact.name}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium">Relationship</p>
                  <p className="text-sm text-muted-foreground">
                    {patient.emergencyContact.relationship}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium">Phone</p>
                  <p className="text-sm text-muted-foreground">
                    {patient.emergencyContact.phone}
                  </p>
                </div>
              </div>
            </Card>

            {/* Medical Tags */}
            {patient.tags.length > 0 && (
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Medical Tags
                </h3>
                <div className="flex flex-wrap gap-2">
                  {patient.tags.map((tag) => (
                    <Badge key={tag} variant="secondary">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </Card>
            )}

            {/* Patient Info */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Activity className="h-5 w-5" />
                Patient Information
              </h3>
              <div className="space-y-3">
                <div>
                  <p className="text-sm font-medium">Date of Birth</p>
                  <p className="text-sm text-muted-foreground">
                    {patient.dateOfBirth.toLocaleDateString()} (Age:{" "}
                    {calculateAge(patient.dateOfBirth)})
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium">Gender</p>
                  <p className="text-sm text-muted-foreground">
                    {patient.gender === "male" ? "Male" : "Female"}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium">Patient Since</p>
                  <p className="text-sm text-muted-foreground">
                    {patient.createdAt.toLocaleDateString()}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium">Last Updated</p>
                  <p className="text-sm text-muted-foreground">
                    {patient.updatedAt.toLocaleDateString()}
                  </p>
                </div>
              </div>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="appointments">
          <Card>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Time</TableHead>
                  <TableHead>Provider</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Reason</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {patientAppointments.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center h-24">
                      <p className="text-muted-foreground">
                        No appointments found
                      </p>
                    </TableCell>
                  </TableRow>
                ) : (
                  patientAppointments.map((apt) => (
                    <TableRow key={apt.id}>
                      <TableCell>
                        {apt.date.toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        {apt.startTime} - {apt.endTime}
                      </TableCell>
                      <TableCell>{apt.providerName}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{apt.appointmentType}</Badge>
                      </TableCell>
                      <TableCell>{apt.reason}</TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            apt.status === "completed"
                              ? "default"
                              : apt.status === "cancelled"
                              ? "destructive"
                              : "secondary"
                          }
                        >
                          {apt.status}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>

        <TabsContent value="insurance">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <CreditCard className="h-5 w-5" />
              Insurance Information
            </h3>
            {patient.insurance.length === 0 ? (
              <p className="text-muted-foreground">No insurance on file</p>
            ) : (
              <div className="space-y-4">
                {patient.insurance.map((ins) => (
                  <div
                    key={ins.id}
                    className="border rounded-lg p-4 space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <h4 className="font-semibold">{ins.provider}</h4>
                      <Badge variant={ins.isPrimary ? "default" : "secondary"}>
                        {ins.isPrimary ? "Primary" : "Secondary"}
                      </Badge>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Policy Number</p>
                        <p className="font-medium">{ins.policyNumber}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Group Number</p>
                        <p className="font-medium">{ins.groupNumber}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Subscriber</p>
                        <p className="font-medium">{ins.subscriberName}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Relationship</p>
                        <p className="font-medium">
                          {ins.subscriberRelationship}
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Effective Date</p>
                        <p className="font-medium">
                          {ins.effectiveDate.toLocaleDateString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Status</p>
                        <Badge
                          variant={
                            ins.status === "active" ? "default" : "secondary"
                          }
                        >
                          {ins.status}
                        </Badge>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </TabsContent>

        <TabsContent value="documents">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Documents
            </h3>
            <div className="text-center py-12">
              <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">
                Document management feature coming soon
              </p>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
