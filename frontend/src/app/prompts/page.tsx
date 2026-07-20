"use client";

import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  getPrompt,
  getPromptVersions,
  getPrompts,
  rollbackPrompt,
  updatePrompt,
} from "@/lib/api";
import { AGENT_NAMES, AgentName } from "@/types";

export default function PromptsPage() {
  const queryClient = useQueryClient();
  const [agent, setAgent] = useState<AgentName>("writer");
  const [content, setContent] = useState("");

  const promptsQuery = useQuery({
    queryKey: ["prompts"],
    queryFn: getPrompts,
  });

  const promptQuery = useQuery({
    queryKey: ["prompts", agent],
    queryFn: () => getPrompt(agent),
  });

  const versionsQuery = useQuery({
    queryKey: ["prompts", agent, "versions"],
    queryFn: () => getPromptVersions(agent),
  });

  useEffect(() => {
    if (promptQuery.data) {
      setContent(promptQuery.data.content);
    }
  }, [promptQuery.data]);

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["prompts"] });
  };

  const saveMutation = useMutation({
    mutationFn: () => updatePrompt(agent, content),
    onSuccess: invalidate,
  });

  const rollbackMutation = useMutation({
    mutationFn: (version: number) => rollbackPrompt(agent, version),
    onSuccess: invalidate,
  });

  const dirty = promptQuery.data ? content !== promptQuery.data.content : false;
  const agents = promptsQuery.data?.map((p) => p.agent_name) ?? [
    ...AGENT_NAMES,
  ];

  return (
    <div className="flex gap-6 h-[calc(100vh-4rem)]">
      <div className="flex-1 flex flex-col space-y-4 min-w-0">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold">Prompt Editor</h1>
          <Button
            onClick={() => saveMutation.mutate()}
            disabled={!dirty || saveMutation.isPending}
          >
            {saveMutation.isPending && (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            )}
            Save Changes
          </Button>
        </div>

        <div className="flex items-center gap-2">
          <select
            className="bg-background border rounded-md p-2 text-sm w-48 capitalize"
            value={agent}
            onChange={(e) => setAgent(e.target.value as AgentName)}
          >
            {agents.map((name) => (
              <option key={name} value={name} className="capitalize">
                {name} agent
              </option>
            ))}
          </select>
          {promptQuery.data && (
            <Badge variant="secondary">v{promptQuery.data.version}</Badge>
          )}
          {saveMutation.isError && (
            <span className="text-sm text-destructive">
              Failed to save prompt.
            </span>
          )}
          {saveMutation.isSuccess && !dirty && (
            <span className="text-sm text-green-400">Saved.</span>
          )}
        </div>

        <Card className="flex-1 flex flex-col overflow-hidden">
          <CardHeader className="py-3 border-b bg-muted/30">
            <CardTitle className="text-sm font-medium">
              System Prompt Template
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0 flex-1">
            {promptQuery.isLoading ? (
              <div className="p-4 flex items-center gap-2 text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" /> Loading prompt...
              </div>
            ) : promptQuery.isError ? (
              <div className="p-4 text-sm text-destructive">
                Failed to load prompt for the {agent} agent.
              </div>
            ) : (
              <textarea
                className="w-full h-full p-4 bg-background resize-none focus:outline-none focus:ring-2 focus:ring-primary font-mono text-sm"
                value={content}
                onChange={(e) => setContent(e.target.value)}
              />
            )}
          </CardContent>
        </Card>
      </div>

      <div className="w-80 border-l pl-6 space-y-4 overflow-y-auto">
        <h2 className="text-lg font-semibold">Version History</h2>

        {versionsQuery.isLoading ? (
          <div className="flex items-center gap-2 text-muted-foreground text-sm">
            <Loader2 className="h-4 w-4 animate-spin" /> Loading versions...
          </div>
        ) : versionsQuery.isError ? (
          <p className="text-sm text-destructive">Failed to load versions.</p>
        ) : !versionsQuery.data || versionsQuery.data.length === 0 ? (
          <p className="text-sm text-muted-foreground">No versions yet.</p>
        ) : (
          <div className="space-y-3">
            {versionsQuery.data.map((version) => (
              <div
                key={version.version}
                className={`p-3 border rounded-lg ${
                  version.is_active ? "bg-secondary/50" : ""
                }`}
              >
                <div className="flex justify-between items-center mb-2">
                  <span className="font-medium text-sm">
                    v{version.version}
                    {version.is_active && (
                      <Badge variant="success" className="ml-2">
                        active
                      </Badge>
                    )}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {new Date(version.created_at).toLocaleDateString()}
                  </span>
                </div>
                {!version.is_active && (
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full text-xs h-7"
                    disabled={rollbackMutation.isPending}
                    onClick={() => rollbackMutation.mutate(version.version)}
                  >
                    Rollback to v{version.version}
                  </Button>
                )}
              </div>
            ))}
            {rollbackMutation.isError && (
              <p className="text-sm text-destructive">Rollback failed.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
