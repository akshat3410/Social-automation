"use client";

import { useQuery } from "@tanstack/react-query";
import { Activity, FileEdit, Lightbulb, Loader2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getDrafts, getIdeas } from "@/lib/api";

interface ActivityItem {
  id: string;
  kind: "idea" | "draft";
  label: string;
  status: string;
  timestamp: string;
}

const statusVariant = (
  status: string
): "secondary" | "warning" | "success" | "destructive" => {
  switch (status) {
    case "researching":
    case "generating":
    case "pending":
      return "warning";
    case "completed":
    case "approved":
    case "published":
      return "success";
    case "failed":
    case "rejected":
      return "destructive";
    default:
      return "secondary";
  }
};

export default function LogsPage() {
  const ideasQuery = useQuery({
    queryKey: ["ideas", "activity"],
    queryFn: () => getIdeas({ limit: 25 }),
    refetchInterval: 10000,
  });
  const draftsQuery = useQuery({
    queryKey: ["drafts", "activity"],
    queryFn: () => getDrafts(),
    refetchInterval: 10000,
  });

  const isLoading = ideasQuery.isLoading || draftsQuery.isLoading;
  const isError = ideasQuery.isError && draftsQuery.isError;

  const items: ActivityItem[] = [
    ...(ideasQuery.data ?? []).map((idea) => ({
      id: `idea-${idea.id}`,
      kind: "idea" as const,
      label: idea.title,
      status: idea.status,
      timestamp: idea.created_at,
    })),
    ...(draftsQuery.data ?? []).map((draft) => ({
      id: `draft-${draft.id}`,
      kind: "draft" as const,
      label: draft.hook || draft.content.slice(0, 80),
      status: draft.status,
      timestamp: draft.created_at,
    })),
  ].sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Recent Activity</h1>
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Activity className="h-4 w-4" />
          Refreshes every 10s
        </div>
      </div>
      <p className="text-sm text-muted-foreground">
        Activity derived from your ideas and drafts. This is not a live log
        stream.
      </p>

      {isLoading ? (
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading activity...
        </div>
      ) : isError ? (
        <p className="text-sm text-destructive">Failed to load activity.</p>
      ) : items.length === 0 ? (
        <Card>
          <CardContent className="p-6 text-sm text-muted-foreground">
            No activity yet — create an idea from Research to get started.
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-0">
            {items.map((item) => (
              <div
                key={item.id}
                className="p-4 border-b last:border-b-0 flex items-center justify-between gap-4"
              >
                <div className="flex items-center gap-3 min-w-0">
                  {item.kind === "idea" ? (
                    <Lightbulb className="h-4 w-4 shrink-0 text-muted-foreground" />
                  ) : (
                    <FileEdit className="h-4 w-4 shrink-0 text-muted-foreground" />
                  )}
                  <div className="min-w-0">
                    <div className="truncate text-sm font-medium">
                      {item.label}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {item.kind === "idea" ? "Idea" : "Draft"} •{" "}
                      {new Date(item.timestamp).toLocaleString()}
                    </div>
                  </div>
                </div>
                <Badge variant={statusVariant(item.status)}>{item.status}</Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
