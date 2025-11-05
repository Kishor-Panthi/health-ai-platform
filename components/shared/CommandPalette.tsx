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

interface CommandPaletteProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CommandPalette({ open, onOpenChange }: CommandPaletteProps) {
  const router = useRouter();

  const handleSelect = (callback: () => void) => {
    onOpenChange(false);
    callback();
  };

  return (
    <CommandDialog open={open} onOpenChange={onOpenChange}>
      <CommandInput placeholder="Type a command or search..." />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>

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
      </CommandList>
    </CommandDialog>
  );
}
