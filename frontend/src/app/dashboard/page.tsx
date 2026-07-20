"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  FileText,
  Heart,
  Eye,
  Search,
  Loader2,
  Lightbulb,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { getAnalyticsSummary, getDrafts, getIdeas } from "@/lib/api";
import { IdeaStatus } from "@/types";

const ideaStatusVariant: Record<
  IdeaStatus,
  "secondary" | "warning" | "success" | "destructive"
> = {
  pending: "secondary",
  researching: "warning",
  generating: "warning",
  completed: "success",
  failed: "destructive",
};

export default function DashboardPage() {
  const summaryQuery = useQuery({
    queryKey: ["analytics", "summary"],
    queryFn: getAnalyticsSummary,
  });
  const draftsQuery = useQuery({
    queryKey: ["drafts", "pending"],
    queryFn: () => getDrafts({ status: "pending" }),
  });
  const ideasQuery = useQuery({
    queryKey: ["ideas", "recent"],
    queryFn: () => getIdeas({ limit: 5 }),
  });

  const summary = summaryQuery.data;

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>

      {summaryQuery.isLoading ? (
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading summary...
        </div>
      ) : summaryQuery.isError ? (
        <p className="text-sm text-destructive">
          Failed to load analytics summary.
        </p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-sm font-medium">
                Total Posts Published
              </CardTitle>
              <FileText className="w-4 h-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary?.total_posts ?? 0}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-sm font-medium">
                Avg Engagement Rate
              </CardTitle>
              <Activity className="w-4 h-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {((summary?.avg_engagement_rate ?? 0) * 100).toFixed(1)}%
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-sm font-medium">Total Views</CardTitle>
              <Eye className="w-4 h-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {(summary?.total_views ?? 0).toLocaleString()}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-sm font-medium">Total Likes</CardTitle>
              <Heart className="w-4 h-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {(summary?.total_likes ?? 0).toLocaleString()}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-xl font-semibold">Pending Drafts</h2>
          <Card>
            <CardContent className="p-0">
              {draftsQuery.isLoading ? (
                <div className="p-4 flex items-center gap-2 text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" /> Loading drafts...
                </div>
              ) : draftsQuery.isError ? (
                <div className="p-4 text-sm text-destructive">
                  Failed to load drafts.
                </div>
              ) : !draftsQuery.data || draftsQuery.data.length === 0 ? (
                <div className="p-4 text-sm text-muted-foreground">
                  No pending drafts — generate some from Research.
                </div>
              ) : (
                draftsQuery.data.slice(0, 5).map((draft) => (
                  <div
                    key={draft.id}
                    className="p-4 border-b last:border-b-0 flex justify-between items-center gap-4"
                  >
                    <div className="min-w-0">
                      <div className="font-medium truncate">
                        {draft.hook || draft.content.slice(0, 80)}
                      </div>
                      <div className="text-sm text-muted-foreground capitalize">
                        {draft.platform}
                        {draft.quality_score
                          ? ` • Human score: ${draft.quality_score.human_score}`
                          : ""}
                      </div>
                    </div>
                    <Link href="/drafts">
                      <Button variant="outline" size="sm">
                        Review
                      </Button>
                    </Link>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>

        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Recent Ideas</h2>
          <Card>
            <CardContent className="p-4 space-y-2">
              {ideasQuery.isLoading ? (
                <div className="flex items-center gap-2 text-muted-foreground text-sm">
                  <Loader2 className="h-4 w-4 animate-spin" /> Loading ideas...
                </div>
              ) : ideasQuery.isError ? (
                <p className="text-sm text-destructive">Failed to load ideas.</p>
              ) : !ideasQuery.data || ideasQuery.data.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No ideas yet — create one from Research.
                </p>
              ) : (
                ideasQuery.data.map((idea) => (
                  <div
                    key={idea.id}
                    className="flex items-center justify-between gap-2 text-sm"
                  >
                    <span className="truncate flex items-center gap-2 min-w-0">
                      <Lightbulb className="h-4 w-4 shrink-0 text-muted-foreground" />
                      <span className="truncate">{idea.title}</span>
                    </span>
                    <Badge variant={ideaStatusVariant[idea.status]}>
                      {idea.status}
                    </Badge>
                  </div>
                ))
              )}
              <div className="pt-2">
                <Link href="/research">
                  <Button className="w-full justify-start" variant="outline">
                    <Search className="mr-2 h-4 w-4" /> New Research Idea
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
