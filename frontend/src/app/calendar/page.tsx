"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CalendarDays, Loader2, Trash2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { deleteSchedule, getScheduled } from "@/lib/api";
import { Schedule } from "@/types";

export default function CalendarPage() {
  const queryClient = useQueryClient();

  const scheduledQuery = useQuery({
    queryKey: ["scheduled"],
    queryFn: getScheduled,
  });

  const cancelMutation = useMutation({
    mutationFn: (id: string) => deleteSchedule(id),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["scheduled"] }),
  });

  const grouped = (scheduledQuery.data ?? [])
    .slice()
    .sort(
      (a, b) =>
        new Date(a.scheduled_for).getTime() -
        new Date(b.scheduled_for).getTime()
    )
    .reduce<Record<string, Schedule[]>>((acc, item) => {
      const day = new Date(item.scheduled_for).toLocaleDateString(undefined, {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
      });
      (acc[day] = acc[day] || []).push(item);
      return acc;
    }, {});

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold">Calendar</h1>

      {scheduledQuery.isLoading ? (
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading scheduled
          posts...
        </div>
      ) : scheduledQuery.isError ? (
        <p className="text-sm text-destructive">
          Failed to load scheduled posts.
        </p>
      ) : Object.keys(grouped).length === 0 ? (
        <Card>
          <CardContent className="p-6 text-sm text-muted-foreground">
            Nothing scheduled — approve a draft with a schedule time to see it
            here.
          </CardContent>
        </Card>
      ) : (
        Object.entries(grouped).map(([day, items]) => (
          <div key={day} className="space-y-2">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <CalendarDays className="h-5 w-5 text-muted-foreground" />
              {day}
            </h2>
            <Card>
              <CardContent className="p-0">
                {items.map((item) => (
                  <div
                    key={item.id}
                    className="p-4 border-b last:border-b-0 flex items-center justify-between gap-4"
                  >
                    <div>
                      <div className="font-medium">
                        {new Date(item.scheduled_for).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Draft {item.draft_id}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary">{item.status}</Badge>
                      <Button
                        variant="ghost"
                        size="icon"
                        title="Cancel schedule"
                        disabled={cancelMutation.isPending}
                        onClick={() => cancelMutation.mutate(item.id)}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        ))
      )}
      {cancelMutation.isError && (
        <p className="text-sm text-destructive">
          Failed to cancel the schedule.
        </p>
      )}
    </div>
  );
}
