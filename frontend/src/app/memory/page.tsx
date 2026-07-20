"use client";

import { Brain } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function MemoryPage() {
  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold">Memory</h1>
      <Card>
        <CardHeader>
          <div className="mx-auto mb-2 w-12 h-12 bg-secondary rounded-lg flex items-center justify-center">
            <Brain className="h-6 w-6 text-muted-foreground" />
          </div>
          <CardTitle className="text-center text-xl">
            Memory browsing is coming soon
          </CardTitle>
          <CardDescription className="text-center">
            The learning agent stores what it learns from your approvals and
            rejections, but there is no API to browse that memory yet. This
            page will light up once the backend exposes it.
          </CardDescription>
        </CardHeader>
        <CardContent />
      </Card>
    </div>
  );
}
