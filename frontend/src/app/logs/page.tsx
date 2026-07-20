"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Terminal } from "lucide-react";

const mockLogs = [
  { id: 1, time: '10:23:45', level: 'info', component: 'api', message: 'Received POST /api/ideas' },
  { id: 2, time: '10:23:45', level: 'info', component: 'worker', message: 'Queued task content_tasks.generate_drafts' },
  { id: 3, time: '10:23:47', level: 'info', component: 'agent:research', message: 'Started research for topic "AI Trends"' },
  { id: 4, time: '10:23:51', level: 'info', component: 'agent:research', message: 'Completed research. Found 3 key insights.' },
  { id: 5, time: '10:23:52', level: 'info', component: 'agent:writer', message: 'Generating draft 1 for Twitter...' },
  { id: 6, time: '10:23:58', level: 'warning', component: 'agent:writer', message: 'API rate limit nearing. Retrying with exponential backoff.' },
  { id: 7, time: '10:24:02', level: 'info', component: 'agent:writer', message: 'Draft 1 completed.' },
  { id: 8, time: '10:24:03', level: 'info', component: 'agent:quality', message: 'Evaluating draft 1 quality...' },
  { id: 9, time: '10:24:06', level: 'info', component: 'agent:quality', message: 'Draft 1 scored 92/100.' },
  { id: 10, time: '10:24:07', level: 'info', component: 'worker', message: 'Task content_tasks.generate_drafts completed successfully' },
];

export default function LogsPage() {
  return (
    <div className="space-y-6 flex flex-col h-[calc(100vh-4rem)]">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">System Logs</h1>
        <div className="flex gap-2">
          <select className="bg-background border rounded-md p-2 text-sm">
            <option>All Levels</option>
            <option>Info</option>
            <option>Warning</option>
            <option>Error</option>
          </select>
          <select className="bg-background border rounded-md p-2 text-sm">
            <option>All Components</option>
            <option>API</option>
            <option>Worker</option>
            <option>Agents</option>
          </select>
        </div>
      </div>

      <Card className="flex-1 overflow-hidden flex flex-col bg-black text-gray-300 font-mono text-sm border-gray-800">
        <div className="p-3 border-b border-gray-800 flex items-center gap-2 bg-gray-900">
          <Terminal className="w-4 h-4" />
          <span>Real-time Logs</span>
          <div className="ml-auto flex items-center gap-2">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
            </span>
            <span className="text-xs text-gray-400">Live</span>
          </div>
        </div>
        <CardContent className="p-4 flex-1 overflow-y-auto space-y-1">
          {mockLogs.map((log) => (
            <div key={log.id} className="flex gap-4 hover:bg-gray-900 p-1 rounded">
              <span className="text-gray-500 w-20 flex-shrink-0">{log.time}</span>
              <span className={`w-16 flex-shrink-0 ${
                log.level === 'info' ? 'text-blue-400' : 
                log.level === 'warning' ? 'text-yellow-400' : 'text-red-400'
              }`}>
                [{log.level.toUpperCase()}]
              </span>
              <span className="text-purple-400 w-32 flex-shrink-0">[{log.component}]</span>
              <span className="text-gray-300">{log.message}</span>
            </div>
          ))}
          <div className="text-gray-500 animate-pulse pt-2">Waiting for new logs...</div>
        </CardContent>
      </Card>
    </div>
  );
}
