"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, Loader2, X } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { approveDraft, getDrafts, rejectDraft } from "@/lib/api";
import { Draft, DraftStatus, QualityScore } from "@/types";

type Tab = DraftStatus | "all";

const tabs: { label: string; value: Tab }[] = [
  { label: "Pending", value: "pending" },
  { label: "Approved", value: "approved" },
  { label: "Rejected", value: "rejected" },
  { label: "Published", value: "published" },
  { label: "All", value: "all" },
];

function QualityBadges({ score }: { score: QualityScore | null }) {
  if (!score) {
    return (
      <Badge variant="secondary" className="font-normal">
        Not scored yet
      </Badge>
    );
  }
  return (
    <div className="flex flex-wrap gap-2 text-xs">
      <Badge variant={score.passed ? "success" : "destructive"}>
        {score.passed ? "Passed" : "Failed"}
      </Badge>
      <Badge variant="secondary">Originality: {score.originality}</Badge>
      <Badge variant="secondary">Hook: {score.hook_strength}</Badge>
      <Badge variant="secondary">
        Engagement: {score.engagement_predicted}
      </Badge>
      <Badge variant="secondary">Spam: {score.spam_probability}</Badge>
      <Badge variant="secondary">Readability: {score.readability_score}</Badge>
      <Badge variant="secondary">Brand: {score.brand_consistency}</Badge>
      <Badge variant="secondary">Human: {score.human_score}</Badge>
    </div>
  );
}

function DraftCard({ draft }: { draft: Draft }) {
  const queryClient = useQueryClient();
  const [scheduledFor, setScheduledFor] = useState("");
  const [rejecting, setRejecting] = useState(false);
  const [reason, setReason] = useState("");

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: ["drafts"] });

  const approveMutation = useMutation({
    mutationFn: () =>
      approveDraft(
        draft.id,
        scheduledFor ? new Date(scheduledFor).toISOString() : undefined
      ),
    onSuccess: invalidate,
  });

  const rejectMutation = useMutation({
    mutationFn: () => rejectDraft(draft.id, reason),
    onSuccess: () => {
      setRejecting(false);
      setReason("");
      invalidate();
    },
  });

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex justify-between items-start mb-4 gap-4 flex-wrap">
          <div className="flex items-center gap-2 text-muted-foreground">
            <span className="text-sm capitalize">{draft.platform} draft</span>
            <Badge variant="outline" className="capitalize">
              {draft.status}
            </Badge>
            {draft.scheduled_for && (
              <span className="text-xs">
                Scheduled: {new Date(draft.scheduled_for).toLocaleString()}
              </span>
            )}
          </div>
          <QualityBadges score={draft.quality_score} />
        </div>

        {draft.hook && (
          <div className="text-sm text-muted-foreground mb-2">
            Hook: {draft.hook}
          </div>
        )}

        <div className="text-lg mb-6 whitespace-pre-wrap">{draft.content}</div>

        {draft.status === "pending" && (
          <div className="space-y-3">
            {rejecting ? (
              <div className="space-y-2">
                <Textarea
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  placeholder="Reason for rejection (sent to the learning agent)"
                />
                <div className="flex justify-end gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setRejecting(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="destructive"
                    size="sm"
                    disabled={!reason || rejectMutation.isPending}
                    onClick={() => rejectMutation.mutate()}
                  >
                    {rejectMutation.isPending && (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    )}
                    Confirm Reject
                  </Button>
                </div>
              </div>
            ) : (
              <div className="flex flex-wrap items-center justify-end gap-3">
                <div className="flex items-center gap-2">
                  <label
                    className="text-sm text-muted-foreground"
                    htmlFor={`schedule-${draft.id}`}
                  >
                    Schedule (optional)
                  </label>
                  <Input
                    id={`schedule-${draft.id}`}
                    type="datetime-local"
                    className="w-auto"
                    value={scheduledFor}
                    onChange={(e) => setScheduledFor(e.target.value)}
                  />
                </div>
                <Button
                  variant="outline"
                  className="text-destructive border-destructive hover:bg-destructive/10"
                  onClick={() => setRejecting(true)}
                >
                  <X className="w-4 h-4 mr-2" /> Reject
                </Button>
                <Button
                  className="bg-green-600 hover:bg-green-700 text-white"
                  disabled={approveMutation.isPending}
                  onClick={() => approveMutation.mutate()}
                >
                  {approveMutation.isPending ? (
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <Check className="w-4 h-4 mr-2" />
                  )}
                  Approve
                </Button>
              </div>
            )}
            {(approveMutation.isError || rejectMutation.isError) && (
              <p className="text-sm text-destructive text-right">
                Action failed. Please try again.
              </p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default function DraftsPage() {
  const [tab, setTab] = useState<Tab>("pending");

  const draftsQuery = useQuery({
    queryKey: ["drafts", tab],
    queryFn: () => getDrafts(tab === "all" ? undefined : { status: tab }),
  });

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Drafts</h1>

      <div className="flex gap-4 border-b pb-2 mb-4">
        {tabs.map((t) => (
          <button
            key={t.value}
            onClick={() => setTab(t.value)}
            className={cn(
              "pb-2 -mb-[10px]",
              tab === t.value
                ? "text-primary font-medium border-b-2 border-primary"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            {t.label}
          </button>
        ))}
      </div>

      {draftsQuery.isLoading ? (
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading drafts...
        </div>
      ) : draftsQuery.isError ? (
        <p className="text-sm text-destructive">Failed to load drafts.</p>
      ) : !draftsQuery.data || draftsQuery.data.length === 0 ? (
        <Card>
          <CardContent className="p-6 text-sm text-muted-foreground">
            No drafts here yet — generate some from Research.
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {draftsQuery.data.map((draft) => (
            <DraftCard key={draft.id} draft={draft} />
          ))}
        </div>
      )}
    </div>
  );
}
