"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function ResearchPage() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(false);

  const handleResearch = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setResults(true);
    }, 1500);
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold">Research</h1>
      
      <Card>
        <CardHeader>
          <CardTitle>New Research Topic</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleResearch} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Topic</label>
              <input 
                type="text" 
                className="w-full bg-background border rounded-md p-2" 
                placeholder="e.g. AI trends in 2025" 
                required 
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Platform Focus</label>
                <select className="w-full bg-background border rounded-md p-2">
                  <option>Twitter</option>
                  <option>LinkedIn</option>
                  <option>General</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Research Depth</label>
                <select className="w-full bg-background border rounded-md p-2">
                  <option>Quick (1-2 mins)</option>
                  <option>Deep Dive (5-10 mins)</option>
                </select>
              </div>
            </div>
            <Button type="submit" disabled={loading}>
              {loading ? "Researching..." : "Start Research"}
            </Button>
          </form>
        </CardContent>
      </Card>

      {results && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4">
          <h2 className="text-2xl font-bold">Research Results</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Trending Angles</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="p-3 bg-secondary rounded-lg">1. The rise of agentic workflows vs copilot models</div>
                <div className="p-3 bg-secondary rounded-lg">2. Open source models catching up to proprietary</div>
                <div className="p-3 bg-secondary rounded-lg">3. Hardware optimization and smaller models</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Key Insights</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <p>• 78% of developers expect to use AI agents daily by 2025.</p>
                <p>• Llama 3 and Mistral are driving open-source adoption.</p>
                <p>• Inference costs dropped by 80% over the last year.</p>
              </CardContent>
            </Card>
          </div>
          
          <Card>
            <CardHeader>
              <CardTitle>Sources</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <a href="#" className="block p-3 border rounded-lg hover:bg-secondary">
                <div className="font-medium text-primary">State of AI Report 2024</div>
                <div className="text-sm text-muted-foreground">Comprehensive analysis of AI trends and future predictions.</div>
              </a>
              <a href="#" className="block p-3 border rounded-lg hover:bg-secondary">
                <div className="font-medium text-primary">Hugging Face Community Insights</div>
                <div className="text-sm text-muted-foreground">Discussions on open source model adoption rates.</div>
              </a>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
