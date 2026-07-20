"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Loader2, Search, Sparkles } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  createIdea,
  getIdeas,
  triggerGenerate,
  triggerResearch,
} from "@/lib/api";
import { Idea, IdeaStatus, Platform } from "@/types";

const statusVariant: Record<
  IdeaStatus,
  "secondary" | "warning" | "success" | "destructive"
> = {
  pending: "secondary",
  researching: "warning",
  generating: "warning",
  completed: "success",
  failed: "destructive",
};

export default function ResearchPage() {
  const queryClient = useQueryClient();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [platform, setPlatform] = useState<Platform>("twitter");

  const ideasQuery = useQuery({
    queryKey: ["ideas"],
    queryFn: () => getIdeas({ limit: 50 }),
    refetchInterval: (query) => {
      const ideas = query.state.data;
      const inProgress = ideas?.some(
        (i) => i.status === "researching" || i.status === "generating"
      );
      return inProgress ? 5000 : false;
    },
  });

  const invalidateIdeas = () =>
    queryClient.invalidateQueries({ queryKey: ["ideas"] });

  const createMutation = useMutation({
    mutationFn: () =>
      createIdea({
        title,
        description: description || undefined,
        platform,
      }),
    onSuccess: () => {
      setTitle("");
      setDescription("");
      invalidateIdeas();
    },
  });

  const researchMutation = useMutation({
    mutationFn: (id: string) => triggerResearch(id),
    onSuccess: invalidateIdeas,
  });

  const generateMutation = useMutation({
    mutationFn: (id: string) => triggerGenerate(id),
    onSuccess: () => {
      invalidateIdeas();
      queryClient.invalidateQueries({ queryKey: ["drafts"] });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate();
  };

  const inProgress = (idea: Idea) =>
    idea.status === "researching" || idea.status === "generating";

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold">Research</h1>

      <Card>
        <CardHeader>
          <CardTitle>New Content Idea</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1" htmlFor="title">
                Title
              </label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. AI trends in 2026"
                required
              />
            </div>
            <div>
              <label
                className="block text-sm font-medium mb-1"
                htmlFor="description"
              >
                Description (optional)
              </label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Extra context or angle for the agents"
              />
            </div>
            <div>
              <label
                className="block text-sm font-medium mb-1"
                htmlFor="platform"
              >
                Platform
              </label>
              <select
                id="platform"
                className="w-full bg-background border rounded-md p-2 text-sm"
                value={platform}
                onChange={(e) => setPlatform(e.target.value as Platform)}
              >
                <option value="twitter">Twitter</option>
                <option value="reddit">Reddit</option>
              </select>
            </div>
            {createMutation.isError && (
              <p className="text-sm text-destructive">
                Failed to create idea. Please try again.
              </p>
            )}
            <Button type="submit" disabled={createMutation.isPending || !title}>
              {createMutation.isPending && (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              )}
              Create Idea
            </Button>
          </form>
        </CardContent>
      </Card>

      <div className="space-y-4">
        <h2 className="text-2xl font-bold">Ideas</h2>
        {ideasQuery.isLoading ? (
          <div className="flex items-center gap-2 text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" /> Loading ideas...
          </div>
        ) : ideasQuery.isError ? (
          <p className="text-sm text-destructive">Failed to load ideas.</p>
        ) : !ideasQuery.data || ideasQuery.data.length === 0 ? (
          <Card>
            <CardContent className="p-6 text-sm text-muted-foreground">
              No ideas yet — create your first one above.
            </CardContent>
          </Card>
        ) : (
          ideasQuery.data.map((idea) => (
            <Card key={idea.id}>
              <CardContent className="p-4 flex items-center justify-between gap-4">
                <div className="min-w-0">
                  <div className="font-medium truncate">{idea.title}</div>
                  {idea.description && (
                    <div className="text-sm text-muted-foreground truncate">
                      {idea.description}
                    </div>
                  )}
                  <div className="text-xs text-muted-foreground capitalize mt-1">
                    {idea.platform} •{" "}
                    {new Date(idea.created_at).toLocaleString()}
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <Badge variant={statusVariant[idea.status]}>
                    {inProgress(idea) && (
                      <Loader2 className="mr-1 h-3 w-3 animate-spin" />
                    )}
                    {idea.status}
                  </Badge>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={inProgress(idea) || researchMutation.isPending}
                    onClick={() => researchMutation.mutate(idea.id)}
                  >
                    <Search className="mr-2 h-4 w-4" /> Research
                  </Button>
                  <Button
                    size="sm"
                    disabled={inProgress(idea) || generateMutation.isPending}
                    onClick={() => generateMutation.mutate(idea.id)}
                  >
                    <Sparkles className="mr-2 h-4 w-4" /> Generate
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))
        )}
        {(researchMutation.isError || generateMutation.isError) && (
          <p className="text-sm text-destructive">
            Failed to start the task. Please try again.
          </p>
        )}
      </div>
    </div>
  );
}
