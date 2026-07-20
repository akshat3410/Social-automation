"use client";

import { useQuery } from "@tanstack/react-query";
import { Loader2 } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getAnalyticsPosts, getAnalyticsSummary } from "@/lib/api";

export default function AnalyticsPage() {
  const summaryQuery = useQuery({
    queryKey: ["analytics", "summary"],
    queryFn: getAnalyticsSummary,
  });
  const postsQuery = useQuery({
    queryKey: ["analytics", "posts"],
    queryFn: getAnalyticsPosts,
  });

  const summary = summaryQuery.data;
  const posts = postsQuery.data ?? [];

  const chartData = [...posts]
    .sort(
      (a, b) =>
        new Date(a.published_at).getTime() - new Date(b.published_at).getTime()
    )
    .map((p) => ({
      name:
        p.content_preview.length > 24
          ? `${p.content_preview.slice(0, 24)}…`
          : p.content_preview,
      views: p.views,
      likes: p.likes,
      replies: p.replies,
      reposts: p.reposts,
      engagement: Number((p.engagement_rate * 100).toFixed(2)),
      date: new Date(p.published_at).toLocaleDateString(),
    }));

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Analytics</h1>

      {summaryQuery.isLoading ? (
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading summary...
        </div>
      ) : summaryQuery.isError ? (
        <p className="text-sm text-destructive">Failed to load summary.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {[
            { label: "Posts", value: summary?.total_posts ?? 0 },
            {
              label: "Views",
              value: (summary?.total_views ?? 0).toLocaleString(),
            },
            {
              label: "Likes",
              value: (summary?.total_likes ?? 0).toLocaleString(),
            },
            {
              label: "Replies",
              value: (summary?.total_replies ?? 0).toLocaleString(),
            },
            {
              label: "Reposts",
              value: (summary?.total_reposts ?? 0).toLocaleString(),
            },
            {
              label: "Avg Engagement",
              value: `${((summary?.avg_engagement_rate ?? 0) * 100).toFixed(1)}%`,
            },
          ].map((stat) => (
            <Card key={stat.label}>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.label}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {postsQuery.isLoading ? (
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading post analytics...
        </div>
      ) : postsQuery.isError ? (
        <p className="text-sm text-destructive">
          Failed to load post analytics.
        </p>
      ) : posts.length === 0 ? (
        <Card>
          <CardContent className="p-6 text-sm text-muted-foreground">
            No published posts yet — analytics will appear once posts go live.
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Engagement Rate Over Time</CardTitle>
            </CardHeader>
            <CardContent className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                  <XAxis dataKey="date" />
                  <YAxis unit="%" />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="engagement"
                    name="Engagement %"
                    stroke="#8884d8"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Views per Post</CardTitle>
            </CardHeader>
            <CardContent className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                  <XAxis dataKey="name" hide />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="views" fill="#82ca9d" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Posts</CardTitle>
            </CardHeader>
            <CardContent className="p-0 overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="p-4 font-medium">Content</th>
                    <th className="p-4 font-medium">Platform</th>
                    <th className="p-4 font-medium text-right">Views</th>
                    <th className="p-4 font-medium text-right">Likes</th>
                    <th className="p-4 font-medium text-right">Replies</th>
                    <th className="p-4 font-medium text-right">Reposts</th>
                    <th className="p-4 font-medium text-right">Engagement</th>
                    <th className="p-4 font-medium">Published</th>
                  </tr>
                </thead>
                <tbody>
                  {posts.map((post) => (
                    <tr key={post.post_id} className="border-b last:border-b-0">
                      <td className="p-4 max-w-xs truncate">
                        {post.content_preview}
                      </td>
                      <td className="p-4 capitalize">{post.platform}</td>
                      <td className="p-4 text-right">
                        {post.views.toLocaleString()}
                      </td>
                      <td className="p-4 text-right">
                        {post.likes.toLocaleString()}
                      </td>
                      <td className="p-4 text-right">
                        {post.replies.toLocaleString()}
                      </td>
                      <td className="p-4 text-right">
                        {post.reposts.toLocaleString()}
                      </td>
                      <td className="p-4 text-right">
                        {(post.engagement_rate * 100).toFixed(1)}%
                      </td>
                      <td className="p-4 whitespace-nowrap">
                        {new Date(post.published_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
