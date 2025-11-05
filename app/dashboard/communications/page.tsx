"use client";

import React, { useState, useMemo } from "react";
import {
  MessageSquare,
  Mail,
  Phone,
  Users,
  Send,
  Search,
  Filter,
  Plus,
  CheckCheck,
  Clock,
  AlertCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  allMockMessages,
  messageTemplates,
  allMockPatients,
} from "@/lib/utils/mockData";
import type { Message } from "@/lib/types";

export default function CommunicationsPage() {
  const [selectedTab, setSelectedTab] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedMessage, setSelectedMessage] = useState<Message | null>(null);
  const [showCompose, setShowCompose] = useState(false);

  // Filter messages
  const filteredMessages = useMemo(() => {
    let filtered = allMockMessages;

    // Type filter
    if (selectedTab !== "all") {
      filtered = filtered.filter((m) => m.type === selectedTab);
    }

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (m) =>
          m.recipientName.toLowerCase().includes(query) ||
          m.subject?.toLowerCase().includes(query) ||
          m.body.toLowerCase().includes(query)
      );
    }

    return filtered;
  }, [selectedTab, searchQuery]);

  // Stats
  const stats = {
    total: allMockMessages.length,
    sent: allMockMessages.filter((m) => m.status === "sent").length,
    delivered: allMockMessages.filter((m) => m.status === "delivered").length,
    read: allMockMessages.filter((m) => m.status === "read").length,
    failed: allMockMessages.filter((m) => m.status === "failed").length,
  };

  const getStatusIcon = (status: Message["status"]) => {
    switch (status) {
      case "sent":
        return <CheckCheck className="h-4 w-4 text-blue-500" />;
      case "delivered":
        return <CheckCheck className="h-4 w-4 text-green-500" />;
      case "read":
        return <CheckCheck className="h-4 w-4 text-green-600" />;
      case "failed":
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getTypeIcon = (type: Message["type"]) => {
    switch (type) {
      case "email":
        return <Mail className="h-4 w-4" />;
      case "sms":
        return <MessageSquare className="h-4 w-4" />;
      case "phone":
        return <Phone className="h-4 w-4" />;
      case "internal":
        return <Users className="h-4 w-4" />;
      default:
        return <MessageSquare className="h-4 w-4" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Communications</h1>
          <p className="text-muted-foreground">
            Manage patient communications and messages
          </p>
        </div>
        <Button onClick={() => setShowCompose(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Compose Message
        </Button>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-5">
        <Card className="p-6">
          <div className="text-2xl font-bold">{stats.total}</div>
          <p className="text-sm text-muted-foreground">Total Messages</p>
        </Card>
        <Card className="p-6">
          <div className="text-2xl font-bold">{stats.sent}</div>
          <p className="text-sm text-muted-foreground">Sent</p>
        </Card>
        <Card className="p-6">
          <div className="text-2xl font-bold">{stats.delivered}</div>
          <p className="text-sm text-muted-foreground">Delivered</p>
        </Card>
        <Card className="p-6">
          <div className="text-2xl font-bold">{stats.read}</div>
          <p className="text-sm text-muted-foreground">Read</p>
        </Card>
        <Card className="p-6">
          <div className="text-2xl font-bold text-red-600">{stats.failed}</div>
          <p className="text-sm text-muted-foreground">Failed</p>
        </Card>
      </div>

      {/* Search */}
      <Card className="p-4">
        <div className="flex items-center gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search messages..."
              className="pl-9"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
      </Card>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Message List */}
        <Card className="md:col-span-1 p-4">
          <Tabs value={selectedTab} onValueChange={setSelectedTab}>
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="all" className="text-xs">
                All
              </TabsTrigger>
              <TabsTrigger value="email" className="text-xs">
                Email
              </TabsTrigger>
              <TabsTrigger value="sms" className="text-xs">
                SMS
              </TabsTrigger>
              <TabsTrigger value="internal" className="text-xs">
                Internal
              </TabsTrigger>
              <TabsTrigger value="automated" className="text-xs">
                Auto
              </TabsTrigger>
            </TabsList>

            <div className="mt-4 space-y-2 max-h-[600px] overflow-y-auto">
              {filteredMessages.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No messages found
                </div>
              ) : (
                filteredMessages.slice(0, 50).map((message) => (
                  <div
                    key={message.id}
                    className={`p-3 rounded-lg border cursor-pointer hover:bg-accent transition-colors ${
                      selectedMessage?.id === message.id ? "bg-accent" : ""
                    }`}
                    onClick={() => setSelectedMessage(message)}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-start gap-2 flex-1 min-w-0">
                        {getTypeIcon(message.type)}
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-sm truncate">
                            {message.recipientName}
                          </p>
                          {message.subject && (
                            <p className="text-sm text-muted-foreground truncate">
                              {message.subject}
                            </p>
                          )}
                          <p className="text-xs text-muted-foreground mt-1">
                            {message.sentAt.toLocaleDateString()}{" "}
                            {message.sentAt.toLocaleTimeString([], {
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </p>
                        </div>
                      </div>
                      {getStatusIcon(message.status)}
                    </div>
                  </div>
                ))
              )}
            </div>
          </Tabs>
        </Card>

        {/* Message Detail */}
        <Card className="md:col-span-2 p-6">
          {selectedMessage ? (
            <div className="space-y-6">
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    {getTypeIcon(selectedMessage.type)}
                    <h2 className="text-2xl font-bold">
                      {selectedMessage.subject || "Message"}
                    </h2>
                  </div>
                  <p className="text-muted-foreground">
                    To: {selectedMessage.recipientName}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Badge>{selectedMessage.type}</Badge>
                  <Badge
                    variant={
                      selectedMessage.status === "read"
                        ? "default"
                        : selectedMessage.status === "failed"
                        ? "destructive"
                        : "secondary"
                    }
                  >
                    {selectedMessage.status}
                  </Badge>
                </div>
              </div>

              <div className="space-y-4 text-sm">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-muted-foreground">Sent</p>
                    <p className="font-medium">
                      {selectedMessage.sentAt.toLocaleString()}
                    </p>
                  </div>
                  {selectedMessage.deliveredAt && (
                    <div>
                      <p className="text-muted-foreground">Delivered</p>
                      <p className="font-medium">
                        {selectedMessage.deliveredAt.toLocaleString()}
                      </p>
                    </div>
                  )}
                  {selectedMessage.readAt && (
                    <div>
                      <p className="text-muted-foreground">Read</p>
                      <p className="font-medium">
                        {selectedMessage.readAt.toLocaleString()}
                      </p>
                    </div>
                  )}
                </div>
              </div>

              <div className="border-t pt-6">
                <h3 className="font-semibold mb-2">Message Content</h3>
                <div className="bg-muted/50 rounded-lg p-4 whitespace-pre-wrap">
                  {selectedMessage.body}
                </div>
              </div>

              <div className="flex justify-end gap-2">
                <Button variant="outline">Forward</Button>
                <Button variant="outline">Reply</Button>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-[400px] text-muted-foreground">
              <MessageSquare className="h-12 w-12 mb-4" />
              <p>Select a message to view details</p>
            </div>
          )}
        </Card>
      </div>

      {/* Compose Message Dialog */}
      {showCompose && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-2xl p-6">
            <h2 className="text-2xl font-bold mb-6">Compose New Message</h2>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                alert("Message sent! (mock)");
                setShowCompose(false);
              }}
              className="space-y-4"
            >
              <div className="space-y-2">
                <label className="text-sm font-medium">Message Type</label>
                <Select defaultValue="email">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="email">Email</SelectItem>
                    <SelectItem value="sms">SMS</SelectItem>
                    <SelectItem value="internal">Internal</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Recipient</label>
                <Select>
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
                <label className="text-sm font-medium">Template (Optional)</label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Select template..." />
                  </SelectTrigger>
                  <SelectContent>
                    {messageTemplates.map((template) => (
                      <SelectItem key={template.id} value={template.id}>
                        {template.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Subject</label>
                <Input placeholder="Enter subject..." />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Message</label>
                <Textarea
                  placeholder="Type your message..."
                  rows={8}
                  required
                />
              </div>

              <div className="flex justify-end gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowCompose(false)}
                >
                  Cancel
                </Button>
                <Button type="submit">
                  <Send className="mr-2 h-4 w-4" />
                  Send Message
                </Button>
              </div>
            </form>
          </Card>
        </div>
      )}
    </div>
  );
}
