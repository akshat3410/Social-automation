"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Check, X, Twitter, Linkedin } from "lucide-react";

export default function DraftsPage() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Drafts</h1>
        <div className="flex gap-2">
          <select className="bg-background border rounded-md p-2 text-sm">
            <option>All Platforms</option>
            <option>Twitter</option>
            <option>LinkedIn</option>
          </select>
        </div>
      </div>
      
      <div className="flex gap-4 border-b pb-2 mb-4">
        <button className="text-primary font-medium border-b-2 border-primary pb-2 -mb-[10px]">Pending Approval (3)</button>
        <button className="text-muted-foreground hover:text-foreground">Approved</button>
        <button className="text-muted-foreground hover:text-foreground">Rejected</button>
        <button className="text-muted-foreground hover:text-foreground">All</button>
      </div>

      <div className="grid grid-cols-1 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex justify-between items-start mb-4">
              <div className="flex items-center gap-2 text-muted-foreground">
                <Twitter className="w-4 h-4 text-blue-400" />
                <span className="text-sm">Twitter Draft</span>
              </div>
              <div className="flex gap-2 text-xs">
                <span className="px-2 py-1 bg-green-500/20 text-green-500 rounded-full">Engagement: 95</span>
                <span className="px-2 py-1 bg-green-500/20 text-green-500 rounded-full">Spam: Low</span>
                <span className="px-2 py-1 bg-blue-500/20 text-blue-500 rounded-full">Readability: 88</span>
                <span className="px-2 py-1 bg-purple-500/20 text-purple-500 rounded-full">Originality: 92</span>
              </div>
            </div>
            
            <div className="text-lg mb-6 whitespace-pre-wrap">
              Next.js 14 is a massive leap forward. 🚀
              
              The new Server Actions mean we can finally say goodbye to messy API routes for simple mutations. It feels like the early days of PHP, but with all the safety and DX of modern React.
              
              Are you upgrading yet? #Nextjs #React #WebDev
            </div>
            
            <div className="flex justify-end gap-3">
              <Button variant="outline" className="text-destructive border-destructive hover:bg-destructive/10">
                <X className="w-4 h-4 mr-2" /> Reject
              </Button>
              <Button className="bg-green-600 hover:bg-green-700 text-white">
                <Check className="w-4 h-4 mr-2" /> Approve
              </Button>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex justify-between items-start mb-4">
              <div className="flex items-center gap-2 text-muted-foreground">
                <Linkedin className="w-4 h-4 text-blue-600" />
                <span className="text-sm">LinkedIn Draft</span>
              </div>
              <div className="flex gap-2 text-xs">
                <span className="px-2 py-1 bg-green-500/20 text-green-500 rounded-full">Engagement: 91</span>
                <span className="px-2 py-1 bg-green-500/20 text-green-500 rounded-full">Spam: Low</span>
                <span className="px-2 py-1 bg-blue-500/20 text-blue-500 rounded-full">Readability: 94</span>
                <span className="px-2 py-1 bg-purple-500/20 text-purple-500 rounded-full">Originality: 89</span>
              </div>
            </div>
            
            <div className="text-lg mb-6 whitespace-pre-wrap">
              Building AI agents is the new compiling.
              
              I spent the weekend working on a multi-agent system using LangGraph and the results were incredible. The ability to have specialized agents debate and refine outputs leads to dramatically better quality than single-prompt approaches.
              
              Here are 3 lessons I learned:
              1. Specialized prompts {">"} general prompts
              2. State management is the hardest part
              3. The future is multi-agent
              
              Have you tried building with autonomous agents yet?
            </div>
            
            <div className="flex justify-end gap-3">
              <Button variant="outline" className="text-destructive border-destructive hover:bg-destructive/10">
                <X className="w-4 h-4 mr-2" /> Reject
              </Button>
              <Button className="bg-green-600 hover:bg-green-700 text-white">
                <Check className="w-4 h-4 mr-2" /> Approve
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
