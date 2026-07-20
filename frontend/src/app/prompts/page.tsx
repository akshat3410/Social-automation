"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const defaultPrompt = `You are an expert social media writer.
Your task is to write a highly engaging tweet based on the following research.

Guidelines:
- Keep it under 280 characters
- Use a hook in the first sentence
- Include 1-2 relevant hashtags
- Maintain a professional yet approachable tone

Research Context:
{research_context}
`;

export default function PromptsPage() {
  const [prompt, setPrompt] = useState(defaultPrompt);

  return (
    <div className="space-y-6 flex h-[calc(100vh-4rem)]">
      <div className="flex-1 pr-6 flex flex-col space-y-4">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold">Prompt Editor</h1>
          <Button>Save Changes</Button>
        </div>
        
        <div className="flex gap-2">
          <select className="bg-background border rounded-md p-2 text-sm w-48">
            <option>Writer Agent</option>
            <option>Research Agent</option>
            <option>Editor Agent</option>
            <option>Quality Agent</option>
            <option>Learning Agent</option>
          </select>
        </div>

        <Card className="flex-1 flex flex-col overflow-hidden">
          <CardHeader className="py-3 border-b bg-muted/30">
            <CardTitle className="text-sm font-medium">System Prompt Template</CardTitle>
          </CardHeader>
          <CardContent className="p-0 flex-1">
            <textarea
              className="w-full h-full p-4 bg-background resize-none focus:outline-none focus:ring-2 focus:ring-primary font-mono text-sm"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            />
          </CardContent>
        </Card>
      </div>

      <div className="w-80 border-l pl-6 space-y-4">
        <h2 className="text-lg font-semibold">Version History</h2>
        
        <div className="space-y-3">
          <div className="p-3 border rounded-lg bg-secondary/50">
            <div className="flex justify-between items-center mb-2">
              <span className="font-medium text-sm">Current Version</span>
              <span className="text-xs text-muted-foreground">Just now</span>
            </div>
            <p className="text-xs text-muted-foreground line-clamp-2">Added guideline for 1-2 hashtags.</p>
          </div>
          
          <div className="p-3 border rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <span className="font-medium text-sm">v1.4</span>
              <span className="text-xs text-muted-foreground">2 days ago</span>
            </div>
            <p className="text-xs text-muted-foreground mb-3 line-clamp-2">Updated tone to professional.</p>
            <Button variant="outline" size="sm" className="w-full text-xs h-7">Rollback to v1.4</Button>
          </div>
          
          <div className="p-3 border rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <span className="font-medium text-sm">v1.3</span>
              <span className="text-xs text-muted-foreground">1 week ago</span>
            </div>
            <p className="text-xs text-muted-foreground mb-3 line-clamp-2">Initial prompt.</p>
            <Button variant="outline" size="sm" className="w-full text-xs h-7">Rollback to v1.3</Button>
          </div>
        </div>
      </div>
    </div>
  );
}
