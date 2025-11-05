"use client";

import React, { useState } from "react";
import {
  User,
  Building2,
  Users,
  Shield,
  Bell,
  Palette,
  Zap,
  Lock,
  Mail,
  Calendar,
  DollarSign,
  Save,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { mockPractice, mockProviders, mockStaff, automationRules } from "@/lib/utils/mockData";

export default function SettingsPage() {
  const [darkMode, setDarkMode] = useState(false);

  const handleSave = (section: string) => {
    alert(`${section} settings saved! (mock)`);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">
          Manage your practice configuration and preferences
        </p>
      </div>

      <Tabs defaultValue="profile" className="space-y-4">
        <TabsList className="grid w-full grid-cols-7">
          <TabsTrigger value="profile">
            <User className="h-4 w-4 mr-2" />
            Profile
          </TabsTrigger>
          <TabsTrigger value="practice">
            <Building2 className="h-4 w-4 mr-2" />
            Practice
          </TabsTrigger>
          <TabsTrigger value="providers">
            <Users className="h-4 w-4 mr-2" />
            Providers
          </TabsTrigger>
          <TabsTrigger value="notifications">
            <Bell className="h-4 w-4 mr-2" />
            Notifications
          </TabsTrigger>
          <TabsTrigger value="appearance">
            <Palette className="h-4 w-4 mr-2" />
            Appearance
          </TabsTrigger>
          <TabsTrigger value="automation">
            <Zap className="h-4 w-4 mr-2" />
            Automation
          </TabsTrigger>
          <TabsTrigger value="security">
            <Shield className="h-4 w-4 mr-2" />
            Security
          </TabsTrigger>
        </TabsList>

        {/* Profile Settings */}
        <TabsContent value="profile">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-6">User Profile</h2>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSave("Profile");
              }}
              className="space-y-6"
            >
              <div className="flex items-center gap-6">
                <div className="h-20 w-20 rounded-full bg-primary/10 flex items-center justify-center">
                  <User className="h-10 w-10 text-primary" />
                </div>
                <div>
                  <Button type="button" variant="outline" size="sm">
                    Change Photo
                  </Button>
                  <p className="text-sm text-muted-foreground mt-1">
                    JPG, PNG or GIF. Max size 2MB
                  </p>
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="firstName">First Name</Label>
                  <Input id="firstName" defaultValue="John" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="lastName">Last Name</Label>
                  <Input id="lastName" defaultValue="Admin" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" type="email" defaultValue="admin@springfieldfm.com" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone</Label>
                  <Input id="phone" type="tel" defaultValue="(555) 100-2000" />
                </div>
                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="role">Role</Label>
                  <Select defaultValue="admin">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="admin">Administrator</SelectItem>
                      <SelectItem value="provider">Provider</SelectItem>
                      <SelectItem value="staff">Staff</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="flex justify-end">
                <Button type="submit">
                  <Save className="mr-2 h-4 w-4" />
                  Save Changes
                </Button>
              </div>
            </form>
          </Card>
        </TabsContent>

        {/* Practice Settings */}
        <TabsContent value="practice">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-6">Practice Information</h2>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSave("Practice");
              }}
              className="space-y-6"
            >
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="practiceName">Practice Name</Label>
                  <Input id="practiceName" defaultValue={mockPractice.name} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="npi">NPI Number</Label>
                  <Input id="npi" defaultValue={mockPractice.npi} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="taxId">Tax ID</Label>
                  <Input id="taxId" defaultValue={mockPractice.taxId} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="practicePhone">Phone</Label>
                  <Input id="practicePhone" defaultValue={mockPractice.phone} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="practiceFax">Fax</Label>
                  <Input id="practiceFax" defaultValue={mockPractice.fax} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="practiceEmail">Email</Label>
                  <Input id="practiceEmail" defaultValue={mockPractice.email} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="practiceWebsite">Website</Label>
                  <Input id="practiceWebsite" defaultValue={mockPractice.website} />
                </div>
                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="street">Street Address</Label>
                  <Input id="street" defaultValue={mockPractice.address.street} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="city">City</Label>
                  <Input id="city" defaultValue={mockPractice.address.city} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="state">State</Label>
                  <Input id="state" defaultValue={mockPractice.address.state} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="zipCode">ZIP Code</Label>
                  <Input id="zipCode" defaultValue={mockPractice.address.zipCode} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="timezone">Timezone</Label>
                  <Select defaultValue={mockPractice.settings.timezone}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="America/New_York">Eastern Time</SelectItem>
                      <SelectItem value="America/Chicago">Central Time</SelectItem>
                      <SelectItem value="America/Denver">Mountain Time</SelectItem>
                      <SelectItem value="America/Los_Angeles">Pacific Time</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="border-t pt-6">
                <h3 className="font-semibold mb-4">Practice Hours</h3>
                <div className="space-y-3">
                  {["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].map(
                    (day, index) => (
                      <div key={day} className="flex items-center gap-4">
                        <div className="w-24">
                          <Label>{day}</Label>
                        </div>
                        <Switch defaultChecked={index < 6} />
                        <Input type="time" defaultValue="08:00" className="w-32" />
                        <span className="text-muted-foreground">to</span>
                        <Input type="time" defaultValue="17:00" className="w-32" />
                      </div>
                    )
                  )}
                </div>
              </div>

              <div className="flex justify-end">
                <Button type="submit">
                  <Save className="mr-2 h-4 w-4" />
                  Save Changes
                </Button>
              </div>
            </form>
          </Card>
        </TabsContent>

        {/* Providers */}
        <TabsContent value="providers">
          <Card className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold">Providers & Staff</h2>
              <Button>
                <Users className="mr-2 h-4 w-4" />
                Add Provider
              </Button>
            </div>

            <div className="space-y-6">
              {/* Providers */}
              <div>
                <h3 className="font-semibold mb-3">Providers</h3>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Title</TableHead>
                      <TableHead>Specialty</TableHead>
                      <TableHead>NPI</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {mockProviders.map((provider) => (
                      <TableRow key={provider.id}>
                        <TableCell className="font-medium">
                          Dr. {provider.firstName} {provider.lastName}
                        </TableCell>
                        <TableCell>{provider.title}</TableCell>
                        <TableCell>{provider.specialty}</TableCell>
                        <TableCell className="font-mono text-sm">{provider.npi}</TableCell>
                        <TableCell>
                          <Badge variant={provider.status === "active" ? "default" : "secondary"}>
                            {provider.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Button variant="ghost" size="sm">
                            Edit
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              {/* Staff */}
              <div>
                <h3 className="font-semibold mb-3">Staff</h3>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {mockStaff.map((staff) => (
                      <TableRow key={staff.id}>
                        <TableCell className="font-medium">
                          {staff.firstName} {staff.lastName}
                        </TableCell>
                        <TableCell className="capitalize">{staff.role.replace("_", " ")}</TableCell>
                        <TableCell>{staff.email}</TableCell>
                        <TableCell>
                          <Badge variant={staff.status === "active" ? "default" : "secondary"}>
                            {staff.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Button variant="ghost" size="sm">
                            Edit
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>
          </Card>
        </TabsContent>

        {/* Notifications */}
        <TabsContent value="notifications">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-6">Notification Preferences</h2>
            <div className="space-y-6">
              <div className="space-y-4">
                <h3 className="font-semibold">Email Notifications</h3>
                <div className="space-y-3">
                  {[
                    { label: "New appointments", defaultChecked: true },
                    { label: "Appointment cancellations", defaultChecked: true },
                    { label: "New patient registrations", defaultChecked: true },
                    { label: "Claim status updates", defaultChecked: true },
                    { label: "Referral updates", defaultChecked: false },
                    { label: "Daily summary report", defaultChecked: false },
                  ].map((item) => (
                    <div key={item.label} className="flex items-center justify-between">
                      <Label>{item.label}</Label>
                      <Switch defaultChecked={item.defaultChecked} />
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-4 border-t pt-6">
                <h3 className="font-semibold">SMS Notifications</h3>
                <div className="space-y-3">
                  {[
                    { label: "Urgent alerts", defaultChecked: true },
                    { label: "Appointment reminders", defaultChecked: false },
                    { label: "System notifications", defaultChecked: false },
                  ].map((item) => (
                    <div key={item.label} className="flex items-center justify-between">
                      <Label>{item.label}</Label>
                      <Switch defaultChecked={item.defaultChecked} />
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-4 border-t pt-6">
                <h3 className="font-semibold">In-App Notifications</h3>
                <div className="space-y-3">
                  {[
                    { label: "Show desktop notifications", defaultChecked: true },
                    { label: "Play sound for alerts", defaultChecked: true },
                    { label: "Show notification badge", defaultChecked: true },
                  ].map((item) => (
                    <div key={item.label} className="flex items-center justify-between">
                      <Label>{item.label}</Label>
                      <Switch defaultChecked={item.defaultChecked} />
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex justify-end pt-4">
                <Button onClick={() => handleSave("Notifications")}>
                  <Save className="mr-2 h-4 w-4" />
                  Save Preferences
                </Button>
              </div>
            </div>
          </Card>
        </TabsContent>

        {/* Appearance */}
        <TabsContent value="appearance">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-6">Appearance</h2>
            <div className="space-y-6">
              <div className="space-y-3">
                <Label>Theme</Label>
                <div className="flex items-center gap-4">
                  <Button
                    variant={!darkMode ? "default" : "outline"}
                    onClick={() => setDarkMode(false)}
                    className="flex-1"
                  >
                    Light Mode
                  </Button>
                  <Button
                    variant={darkMode ? "default" : "outline"}
                    onClick={() => setDarkMode(true)}
                    className="flex-1"
                  >
                    Dark Mode
                  </Button>
                </div>
                <p className="text-sm text-muted-foreground">
                  Choose your preferred color scheme
                </p>
              </div>

              <div className="space-y-3 border-t pt-6">
                <Label>Primary Color</Label>
                <div className="flex gap-3">
                  {[
                    { color: "bg-blue-500", name: "Blue" },
                    { color: "bg-green-500", name: "Green" },
                    { color: "bg-purple-500", name: "Purple" },
                    { color: "bg-orange-500", name: "Orange" },
                    { color: "bg-red-500", name: "Red" },
                  ].map((item) => (
                    <button
                      key={item.name}
                      className={`${item.color} h-10 w-10 rounded-full border-2 border-transparent hover:border-foreground`}
                      title={item.name}
                    />
                  ))}
                </div>
              </div>

              <div className="space-y-3 border-t pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Compact Mode</Label>
                    <p className="text-sm text-muted-foreground">
                      Reduce spacing for more content
                    </p>
                  </div>
                  <Switch />
                </div>
              </div>

              <div className="space-y-3 border-t pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Show Sidebar by Default</Label>
                    <p className="text-sm text-muted-foreground">
                      Keep sidebar expanded on desktop
                    </p>
                  </div>
                  <Switch defaultChecked />
                </div>
              </div>

              <div className="flex justify-end pt-4">
                <Button onClick={() => handleSave("Appearance")}>
                  <Save className="mr-2 h-4 w-4" />
                  Save Preferences
                </Button>
              </div>
            </div>
          </Card>
        </TabsContent>

        {/* Automation */}
        <TabsContent value="automation">
          <Card className="p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-semibold">Automation Rules</h2>
                <p className="text-muted-foreground text-sm">
                  Configure automated workflows and reminders
                </p>
              </div>
              <Button>
                <Zap className="mr-2 h-4 w-4" />
                Create Rule
              </Button>
            </div>

            <div className="space-y-4">
              {automationRules.map((rule) => (
                <Card key={rule.id} className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-semibold">{rule.name}</h3>
                        <Badge variant={rule.isActive ? "default" : "secondary"}>
                          {rule.isActive ? "Active" : "Inactive"}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-3">
                        {rule.description}
                      </p>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <span>Trigger: {rule.trigger.event}</span>
                        <span>•</span>
                        <span>{rule.actions.length} action(s)</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Switch defaultChecked={rule.isActive} />
                      <Button variant="ghost" size="sm">
                        Edit
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </Card>
        </TabsContent>

        {/* Security */}
        <TabsContent value="security">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-6">Security Settings</h2>
            <div className="space-y-6">
              <div className="space-y-4">
                <h3 className="font-semibold flex items-center gap-2">
                  <Lock className="h-4 w-4" />
                  Password
                </h3>
                <Button variant="outline">Change Password</Button>
              </div>

              <div className="space-y-4 border-t pt-6">
                <h3 className="font-semibold">Two-Factor Authentication</h3>
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Enable 2FA</Label>
                    <p className="text-sm text-muted-foreground">
                      Add an extra layer of security to your account
                    </p>
                  </div>
                  <Switch />
                </div>
              </div>

              <div className="space-y-4 border-t pt-6">
                <h3 className="font-semibold">Session Management</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-muted/50 rounded">
                    <div>
                      <p className="font-medium">Current Session</p>
                      <p className="text-sm text-muted-foreground">
                        Windows • Chrome • Active now
                      </p>
                    </div>
                    <Badge variant="default">Active</Badge>
                  </div>
                </div>
                <Button variant="destructive" size="sm">
                  Sign Out All Sessions
                </Button>
              </div>

              <div className="space-y-4 border-t pt-6">
                <h3 className="font-semibold">HIPAA Compliance</h3>
                <div className="space-y-3">
                  {[
                    { label: "Enable audit logging", defaultChecked: true },
                    { label: "Require session timeout (15 min)", defaultChecked: true },
                    { label: "Encrypt all data at rest", defaultChecked: true },
                    { label: "Enable access controls", defaultChecked: true },
                  ].map((item) => (
                    <div key={item.label} className="flex items-center justify-between">
                      <Label>{item.label}</Label>
                      <Switch defaultChecked={item.defaultChecked} disabled />
                    </div>
                  ))}
                </div>
                <p className="text-sm text-muted-foreground">
                  These settings are enforced for HIPAA compliance
                </p>
              </div>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
