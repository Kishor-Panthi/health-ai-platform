"use client";

import { LogOut, Settings, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Avatar } from "@/components/ui/avatar";

export function UserMenu() {
  // Mock user data
  const user = {
    name: "Dr. Sarah Johnson",
    email: "sarah.johnson@example.com",
    role: "Primary Care Physician",
    avatar: undefined,
  };

  return (
    <div className="flex items-center gap-2">
      <Button variant="ghost" className="flex items-center gap-2">
        <Avatar className="h-8 w-8">
          <div className="flex h-full w-full items-center justify-center bg-primary text-primary-foreground">
            {user.name
              .split(" ")
              .map((n) => n[0])
              .join("")}
          </div>
        </Avatar>
        <div className="hidden text-left lg:block">
          <p className="text-sm font-medium">{user.name}</p>
          <p className="text-xs text-muted-foreground">{user.role}</p>
        </div>
      </Button>
    </div>
  );
}
