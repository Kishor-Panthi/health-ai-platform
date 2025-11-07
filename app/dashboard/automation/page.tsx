"use client";

import { useState } from "react";
import { Plus, Play, Pause, Edit, Trash2, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";

interface AutomationRule {
  id: string;
  name: string;
  description: string;
  trigger: string;
  action: string;
  enabled: boolean;
  lastRun?: Date;
  runCount: number;
}

const mockRules: AutomationRule[] = [
  {
    id: "1",
    name: "Appointment Reminder - 24 Hours",
    description: "Send SMS reminder to patients 24 hours before appointment",
    trigger: "24 hours before appointment",
    action: "Send SMS",
    enabled: true,
    lastRun: new Date(Date.now() - 2 * 60 * 60 * 1000),
    runCount: 156,
  },
  {
    id: "2",
    name: "New Patient Welcome Email",
    description: "Send welcome email when a new patient is registered",
    trigger: "Patient registered",
    action: "Send Email",
    enabled: true,
    lastRun: new Date(Date.now() - 24 * 60 * 60 * 1000),
    runCount: 42,
  },
  {
    id: "3",
    name: "Insurance Verification",
    description: "Verify insurance eligibility 3 days before appointment",
    trigger: "3 days before appointment",
    action: "Check insurance eligibility",
    enabled: false,
    runCount: 0,
  },
  {
    id: "4",
    name: "Claim Status Update",
    description: "Check claim status weekly and notify if rejected",
    trigger: "Every Monday 9:00 AM",
    action: "Update claim status & notify",
    enabled: true,
    lastRun: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
    runCount: 28,
  },
];

export default function AutomationPage() {
  const [rules, setRules] = useState<AutomationRule[]>(mockRules);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const toggleRule = (id: string) => {
    setRules((prev) =>
      prev.map((rule) =>
        rule.id === id ? { ...rule, enabled: !rule.enabled } : rule
      )
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Automation Center</h1>
          <p className="text-muted-foreground">
            Create and manage automated workflows for your practice
          </p>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              New Rule
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create Automation Rule</DialogTitle>
              <DialogDescription>
                Define triggers and actions to automate your practice workflows
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="rule-name">Rule Name</Label>
                <Input id="rule-name" placeholder="e.g., Appointment Reminder" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="rule-description">Description</Label>
                <Textarea
                  id="rule-description"
                  placeholder="Describe what this rule does..."
                  rows={3}
                />
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="trigger">Trigger</Label>
                  <Select>
                    <SelectTrigger id="trigger">
                      <SelectValue placeholder="Select trigger" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="appointment-created">
                        Appointment Created
                      </SelectItem>
                      <SelectItem value="patient-registered">
                        Patient Registered
                      </SelectItem>
                      <SelectItem value="claim-submitted">
                        Claim Submitted
                      </SelectItem>
                      <SelectItem value="before-appointment">
                        Before Appointment
                      </SelectItem>
                      <SelectItem value="schedule">On Schedule</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="action">Action</Label>
                  <Select>
                    <SelectTrigger id="action">
                      <SelectValue placeholder="Select action" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="send-email">Send Email</SelectItem>
                      <SelectItem value="send-sms">Send SMS</SelectItem>
                      <SelectItem value="create-task">Create Task</SelectItem>
                      <SelectItem value="update-record">Update Record</SelectItem>
                      <SelectItem value="notify-staff">Notify Staff</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={() => setIsDialogOpen(false)}>Create Rule</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Rules</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{rules.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Active Rules</CardTitle>
            <Play className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {rules.filter((r) => r.enabled).length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Executions</CardTitle>
            <Zap className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {rules.reduce((sum, r) => sum + r.runCount, 0)}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Inactive Rules</CardTitle>
            <Pause className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {rules.filter((r) => !r.enabled).length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Rules List */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Automation Rules</h2>
        {rules.map((rule) => (
          <Card key={rule.id}>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <CardTitle>{rule.name}</CardTitle>
                    <Badge variant={rule.enabled ? "default" : "secondary"}>
                      {rule.enabled ? "Active" : "Inactive"}
                    </Badge>
                  </div>
                  <CardDescription>{rule.description}</CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <Switch
                    checked={rule.enabled}
                    onCheckedChange={() => toggleRule(rule.id)}
                  />
                  <Button variant="ghost" size="icon">
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon">
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Trigger</p>
                  <p className="font-medium">{rule.trigger}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Action</p>
                  <p className="font-medium">{rule.action}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Last Run</p>
                  <p className="font-medium">
                    {rule.lastRun
                      ? rule.lastRun.toLocaleString()
                      : "Never"}
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground">Run Count</p>
                  <p className="font-medium">{rule.runCount}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
