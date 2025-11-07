"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import {
  Calendar,
  Users,
  MessageSquare,
  DollarSign,
  FileText,
  BarChart3,
  Settings,
  HelpCircle,
  Plus,
  Search,
  Home,
  UserPlus,
  CalendarPlus,
  FileBox,
  Send,
  User,
  Mail,
  CreditCard,
} from "lucide-react";
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from "@/components/ui/command";
import {
  allMockPatients,
  allMockAppointments,
  allMockClaims,
  allMockReferrals,
  allMockMessages,
} from "@/lib/utils/mockData";

interface CommandPaletteProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CommandPalette({ open, onOpenChange }: CommandPaletteProps) {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = React.useState("");

  const handleSelect = (callback: () => void) => {
    onOpenChange(false);
    setSearchQuery("");
    callback();
  };

  // Search functionality
  const searchResults = React.useMemo(() => {
    if (!searchQuery || searchQuery.length < 2) {
      return { patients: [], appointments: [], claims: [], referrals: [], messages: [] };
    }

    const query = searchQuery.toLowerCase();

    const patients = allMockPatients
      .filter((p) => {
        const fullName = `${p.firstName} ${p.lastName}`.toLowerCase();
        return (
          fullName.includes(query) ||
          p.mrn.toLowerCase().includes(query) ||
          p.email.toLowerCase().includes(query) ||
          p.phone.includes(query)
        );
      })
      .slice(0, 5);

    const appointments = allMockAppointments
      .filter((a) => {
        return (
          a.patientName.toLowerCase().includes(query) ||
          a.providerName.toLowerCase().includes(query) ||
          a.reason.toLowerCase().includes(query)
        );
      })
      .slice(0, 5);

    const claims = allMockClaims
      .filter((c) => {
        return (
          c.claimNumber.toLowerCase().includes(query) ||
          c.patientName.toLowerCase().includes(query) ||
          c.providerName.toLowerCase().includes(query)
        );
      })
      .slice(0, 5);

    const referrals = allMockReferrals
      .filter((r) => {
        return (
          r.patientName.toLowerCase().includes(query) ||
          r.referringProvider.toLowerCase().includes(query) ||
          r.specialist.toLowerCase().includes(query) ||
          r.specialty.toLowerCase().includes(query)
        );
      })
      .slice(0, 5);

    const messages = allMockMessages
      .filter((m) => {
        return (
          m.patientName.toLowerCase().includes(query) ||
          m.subject.toLowerCase().includes(query) ||
          m.preview.toLowerCase().includes(query)
        );
      })
      .slice(0, 5);

    return { patients, appointments, claims, referrals, messages };
  }, [searchQuery]);

  const hasSearchResults =
    searchResults.patients.length > 0 ||
    searchResults.appointments.length > 0 ||
    searchResults.claims.length > 0 ||
    searchResults.referrals.length > 0 ||
    searchResults.messages.length > 0;

  return (
    <CommandDialog open={open} onOpenChange={onOpenChange}>
      <CommandInput
        placeholder="Type a command or search..."
        value={searchQuery}
        onValueChange={setSearchQuery}
      />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>

        {/* Search Results */}
        {searchResults.patients.length > 0 && (
          <>
            <CommandGroup heading="Patients">
              {searchResults.patients.map((patient) => (
                <CommandItem
                  key={patient.id}
                  onSelect={() =>
                    handleSelect(() => router.push(`/dashboard/patients/${patient.id}`))
                  }
                >
                  <User className="mr-2 h-4 w-4" />
                  <div className="flex flex-col">
                    <span>
                      {patient.firstName} {patient.lastName}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      MRN: {patient.mrn} • {patient.email}
                    </span>
                  </div>
                </CommandItem>
              ))}
            </CommandGroup>
            <CommandSeparator />
          </>
        )}

        {searchResults.appointments.length > 0 && (
          <>
            <CommandGroup heading="Appointments">
              {searchResults.appointments.map((apt) => (
                <CommandItem
                  key={apt.id}
                  onSelect={() =>
                    handleSelect(() => router.push("/dashboard/appointments"))
                  }
                >
                  <Calendar className="mr-2 h-4 w-4" />
                  <div className="flex flex-col">
                    <span>{apt.patientName}</span>
                    <span className="text-xs text-muted-foreground">
                      {apt.date.toLocaleDateString()} at {apt.startTime} • {apt.reason}
                    </span>
                  </div>
                </CommandItem>
              ))}
            </CommandGroup>
            <CommandSeparator />
          </>
        )}

        {searchResults.claims.length > 0 && (
          <>
            <CommandGroup heading="Claims">
              {searchResults.claims.map((claim) => (
                <CommandItem
                  key={claim.id}
                  onSelect={() =>
                    handleSelect(() => router.push("/dashboard/billing"))
                  }
                >
                  <CreditCard className="mr-2 h-4 w-4" />
                  <div className="flex flex-col">
                    <span>{claim.claimNumber}</span>
                    <span className="text-xs text-muted-foreground">
                      {claim.patientName} • ${claim.billedAmount.toFixed(2)}
                    </span>
                  </div>
                </CommandItem>
              ))}
            </CommandGroup>
            <CommandSeparator />
          </>
        )}

        {searchResults.referrals.length > 0 && (
          <>
            <CommandGroup heading="Referrals">
              {searchResults.referrals.map((referral) => (
                <CommandItem
                  key={referral.id}
                  onSelect={() =>
                    handleSelect(() => router.push("/dashboard/referrals"))
                  }
                >
                  <FileText className="mr-2 h-4 w-4" />
                  <div className="flex flex-col">
                    <span>{referral.patientName}</span>
                    <span className="text-xs text-muted-foreground">
                      {referral.specialty} • {referral.specialist}
                    </span>
                  </div>
                </CommandItem>
              ))}
            </CommandGroup>
            <CommandSeparator />
          </>
        )}

        {searchResults.messages.length > 0 && (
          <>
            <CommandGroup heading="Messages">
              {searchResults.messages.map((message) => (
                <CommandItem
                  key={message.id}
                  onSelect={() =>
                    handleSelect(() => router.push("/dashboard/communications"))
                  }
                >
                  <Mail className="mr-2 h-4 w-4" />
                  <div className="flex flex-col">
                    <span>{message.subject}</span>
                    <span className="text-xs text-muted-foreground">
                      {message.patientName} • {message.preview.slice(0, 50)}...
                    </span>
                  </div>
                </CommandItem>
              ))}
            </CommandGroup>
            <CommandSeparator />
          </>
        )}

        {/* Only show navigation when not searching or no search results */}
        {!hasSearchResults && (
          <>
            <CommandGroup heading="Navigation">
              <CommandItem
                onSelect={() => handleSelect(() => router.push("/dashboard"))}
              >
                <Home className="mr-2 h-4 w-4" />
                <span>Dashboard</span>
              </CommandItem>
              <CommandItem
                onSelect={() => handleSelect(() => router.push("/dashboard/appointments"))}
              >
                <Calendar className="mr-2 h-4 w-4" />
                <span>Appointments</span>
              </CommandItem>
              <CommandItem
                onSelect={() => handleSelect(() => router.push("/dashboard/patients"))}
              >
                <Users className="mr-2 h-4 w-4" />
                <span>Patients</span>
              </CommandItem>
              <CommandItem
                onSelect={() => handleSelect(() => router.push("/dashboard/communications"))}
              >
                <MessageSquare className="mr-2 h-4 w-4" />
                <span>Communications</span>
              </CommandItem>
              <CommandItem
                onSelect={() => handleSelect(() => router.push("/dashboard/billing"))}
              >
                <DollarSign className="mr-2 h-4 w-4" />
                <span>Billing</span>
              </CommandItem>
              <CommandItem
                onSelect={() => handleSelect(() => router.push("/dashboard/referrals"))}
              >
                <FileText className="mr-2 h-4 w-4" />
                <span>Referrals</span>
              </CommandItem>
              <CommandItem
                onSelect={() => handleSelect(() => router.push("/dashboard/reports"))}
              >
                <BarChart3 className="mr-2 h-4 w-4" />
                <span>Reports & Analytics</span>
              </CommandItem>
              <CommandItem
                onSelect={() => handleSelect(() => router.push("/dashboard/settings"))}
              >
                <Settings className="mr-2 h-4 w-4" />
                <span>Settings</span>
              </CommandItem>
            </CommandGroup>

            <CommandSeparator />

            <CommandGroup heading="Quick Actions">
              <CommandItem
                onSelect={() =>
                  handleSelect(() => router.push("/dashboard/appointments?action=new"))
                }
              >
                <CalendarPlus className="mr-2 h-4 w-4" />
                <span>Book New Appointment</span>
              </CommandItem>
              <CommandItem
                onSelect={() =>
                  handleSelect(() => router.push("/dashboard/patients?action=new"))
                }
              >
                <UserPlus className="mr-2 h-4 w-4" />
                <span>Add New Patient</span>
              </CommandItem>
              <CommandItem
                onSelect={() =>
                  handleSelect(() => router.push("/dashboard/billing?action=new-claim"))
                }
              >
                <FileBox className="mr-2 h-4 w-4" />
                <span>Create New Claim</span>
              </CommandItem>
              <CommandItem
                onSelect={() =>
                  handleSelect(() => router.push("/dashboard/referrals?action=new"))
                }
              >
                <Send className="mr-2 h-4 w-4" />
                <span>Send Referral</span>
              </CommandItem>
              <CommandItem
                onSelect={() =>
                  handleSelect(() => router.push("/dashboard/communications?action=compose"))
                }
              >
                <MessageSquare className="mr-2 h-4 w-4" />
                <span>Compose Message</span>
              </CommandItem>
            </CommandGroup>

            <CommandSeparator />

            <CommandGroup heading="Help & Support">
              <CommandItem
                onSelect={() => handleSelect(() => router.push("/dashboard/help"))}
              >
                <HelpCircle className="mr-2 h-4 w-4" />
                <span>Help Center</span>
              </CommandItem>
              <CommandItem
                onSelect={() =>
                  handleSelect(() => router.push("/dashboard/help/shortcuts"))
                }
              >
                <Search className="mr-2 h-4 w-4" />
                <span>Keyboard Shortcuts</span>
              </CommandItem>
            </CommandGroup>
          </>
        )}
      </CommandList>
    </CommandDialog>
  );
}
