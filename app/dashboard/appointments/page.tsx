"use client";

import React, { useState, useMemo } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import { Calendar, Filter, Plus, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { allMockAppointments, mockProviders } from "@/lib/utils/mockData";
import type { Appointment } from "@/lib/types";

export default function AppointmentsPage() {
  const [selectedProvider, setSelectedProvider] = useState<string>("all");
  const [showNewAppointmentDialog, setShowNewAppointmentDialog] =
    useState(false);
  const [selectedAppointment, setSelectedAppointment] =
    useState<Appointment | null>(null);

  // Filter appointments by provider
  const filteredAppointments = useMemo(() => {
    if (selectedProvider === "all") return allMockAppointments;
    return allMockAppointments.filter(
      (apt) => apt.providerId === selectedProvider
    );
  }, [selectedProvider]);

  // Convert appointments to FullCalendar events
  const events = useMemo(() => {
    return filteredAppointments.map((apt) => {
      // Color coding by appointment type
      const colorMap = {
        consultation: "#3b82f6", // blue
        "follow-up": "#10b981", // green
        procedure: "#f59e0b", // orange
        "physical-exam": "#8b5cf6", // purple
      };

      return {
        id: apt.id,
        title: `${apt.patientName} - ${apt.reason}`,
        start: `${apt.date.toISOString().split("T")[0]}T${apt.startTime}`,
        end: `${apt.date.toISOString().split("T")[0]}T${apt.endTime}`,
        backgroundColor: colorMap[apt.appointmentType],
        borderColor: colorMap[apt.appointmentType],
        extendedProps: {
          appointment: apt,
        },
      };
    });
  }, [filteredAppointments]);

  const handleEventClick = (clickInfo: any) => {
    const appointment = clickInfo.event.extendedProps.appointment;
    setSelectedAppointment(appointment);
  };

  const handleDateClick = (arg: any) => {
    console.log("Date clicked:", arg.dateStr);
    setShowNewAppointmentDialog(true);
  };

  // Stats
  const todayAppointments = filteredAppointments.filter(
    (apt) =>
      apt.date.toDateString() === new Date().toDateString() &&
      apt.status !== "cancelled"
  );
  const confirmedToday = todayAppointments.filter(
    (apt) => apt.status === "confirmed" || apt.status === "checked-in"
  );
  const completedToday = todayAppointments.filter(
    (apt) => apt.status === "completed"
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Appointments</h1>
          <p className="text-muted-foreground">
            Manage and schedule patient appointments
          </p>
        </div>
        <Button onClick={() => setShowNewAppointmentDialog(true)}>
          <Plus className="mr-2 h-4 w-4" />
          New Appointment
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Today's Appointments
              </p>
              <p className="text-2xl font-bold">{todayAppointments.length}</p>
            </div>
            <Calendar className="h-8 w-8 text-muted-foreground" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Confirmed
              </p>
              <p className="text-2xl font-bold">{confirmedToday.length}</p>
            </div>
            <Users className="h-8 w-8 text-muted-foreground" />
          </div>
        </Card>
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Completed
              </p>
              <p className="text-2xl font-bold">{completedToday.length}</p>
            </div>
            <Calendar className="h-8 w-8 text-muted-foreground" />
          </div>
        </Card>
      </div>

      {/* Filters */}
      <Card className="p-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-medium">Filter by Provider:</span>
          </div>
          <Select value={selectedProvider} onValueChange={setSelectedProvider}>
            <SelectTrigger className="w-[250px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Providers</SelectItem>
              {mockProviders.map((provider) => (
                <SelectItem key={provider.id} value={provider.id}>
                  Dr. {provider.firstName} {provider.lastName}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <div className="ml-auto flex items-center gap-2">
            <span className="text-sm font-medium">Legend:</span>
            <Badge
              className="bg-blue-500 hover:bg-blue-600"
              variant="default"
            >
              Consultation
            </Badge>
            <Badge
              className="bg-green-500 hover:bg-green-600"
              variant="default"
            >
              Follow-up
            </Badge>
            <Badge
              className="bg-orange-500 hover:bg-orange-600"
              variant="default"
            >
              Procedure
            </Badge>
            <Badge
              className="bg-purple-500 hover:bg-purple-600"
              variant="default"
            >
              Physical Exam
            </Badge>
          </div>
        </div>
      </Card>

      {/* Calendar */}
      <Card className="p-6">
        <FullCalendar
          plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
          initialView="timeGridWeek"
          headerToolbar={{
            left: "prev,next today",
            center: "title",
            right: "dayGridMonth,timeGridWeek,timeGridDay",
          }}
          events={events}
          eventClick={handleEventClick}
          dateClick={handleDateClick}
          editable={true}
          selectable={true}
          selectMirror={true}
          dayMaxEvents={true}
          weekends={true}
          slotMinTime="08:00:00"
          slotMaxTime="18:00:00"
          height="auto"
          eventContent={(eventInfo) => {
            const apt = eventInfo.event.extendedProps.appointment;
            return (
              <div className="p-1 text-xs overflow-hidden">
                <div className="font-semibold truncate">
                  {apt.patientName}
                </div>
                <div className="truncate">{apt.reason}</div>
                <div className="text-[10px] opacity-90">
                  {apt.startTime} - {apt.endTime}
                </div>
              </div>
            );
          }}
        />
      </Card>

      {/* Appointment Detail Dialog - Placeholder */}
      {selectedAppointment && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-2xl p-6 m-4">
            <h2 className="text-2xl font-bold mb-4">Appointment Details</h2>
            <div className="space-y-4">
              <div>
                <span className="font-medium">Patient:</span>{" "}
                {selectedAppointment.patientName}
              </div>
              <div>
                <span className="font-medium">Provider:</span>{" "}
                {selectedAppointment.providerName}
              </div>
              <div>
                <span className="font-medium">Date:</span>{" "}
                {selectedAppointment.date.toLocaleDateString()}
              </div>
              <div>
                <span className="font-medium">Time:</span>{" "}
                {selectedAppointment.startTime} - {selectedAppointment.endTime}
              </div>
              <div>
                <span className="font-medium">Type:</span>{" "}
                <Badge>{selectedAppointment.appointmentType}</Badge>
              </div>
              <div>
                <span className="font-medium">Status:</span>{" "}
                <Badge>{selectedAppointment.status}</Badge>
              </div>
              <div>
                <span className="font-medium">Reason:</span>{" "}
                {selectedAppointment.reason}
              </div>
              {selectedAppointment.room && (
                <div>
                  <span className="font-medium">Room:</span>{" "}
                  {selectedAppointment.room}
                </div>
              )}
            </div>
            <div className="mt-6 flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => setSelectedAppointment(null)}
              >
                Close
              </Button>
              <Button>Edit Appointment</Button>
            </div>
          </Card>
        </div>
      )}

      {/* New Appointment Dialog - Placeholder */}
      {showNewAppointmentDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-2xl p-6 m-4">
            <h2 className="text-2xl font-bold mb-4">Book New Appointment</h2>
            <p className="text-muted-foreground mb-6">
              Appointment booking form will be implemented here
            </p>
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => setShowNewAppointmentDialog(false)}
              >
                Cancel
              </Button>
              <Button onClick={() => setShowNewAppointmentDialog(false)}>
                Book Appointment
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
