import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle, DollarSign, Shield, TrendingUp, Activity, AlertTriangle } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";

const tokenData = [
  { day: "Mon", tokens: 42000, cost: 84 },
  { day: "Tue", tokens: 53000, cost: 106 },
  { day: "Wed", tokens: 48000, cost: 96 },
  { day: "Thu", tokens: 61000, cost: 122 },
  { day: "Fri", tokens: 55000, cost: 110 },
  { day: "Sat", tokens: 38000, cost: 76 },
  { day: "Sun", tokens: 45000, cost: 90 },
];

const actionData = [
  { name: "Safe", value: 847, color: "hsl(155, 100%, 50%)" },
  { name: "Anomalous", value: 23, color: "hsl(0, 72%, 51%)" },
];

const metrics = [
  { icon: CheckCircle, label: "Tasks Completed", value: "12,847", change: "+14.2%", positive: true },
  { icon: Activity, label: "Resource Consumption", value: "342K tokens", change: "-8.1%", positive: true },
  { icon: Shield, label: "Risk Events Mitigated", value: "156", change: "+23", positive: true },
  { icon: TrendingUp, label: "Agent Reliability", value: "97.3%", change: "+0.8%", positive: true },
];

const ExecutiveTab = () => {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Metrics Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((m) => (
          <Card key={m.label} className="bg-card border-border card-hover">
            <CardContent className="p-5">
              <div className="flex items-center justify-between mb-3">
                <div className="h-9 w-9 rounded-lg bg-primary/10 flex items-center justify-center">
                  <m.icon className="h-5 w-5 text-primary" />
                </div>
                <span className="text-xs font-medium text-primary">{m.change}</span>
              </div>
              <div className="text-2xl font-bold text-foreground">{m.value}</div>
              <div className="text-xs text-muted-foreground mt-1">{m.label}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* ROI Banner */}
      <Card className="bg-gradient-to-r from-primary/10 via-card to-card border-primary/20 glow-primary">
        <CardContent className="p-6 flex items-center justify-between">
          <div>
            <div className="text-sm text-muted-foreground mb-1">Estimated ROI This Quarter</div>
            <div className="text-5xl font-extrabold text-primary glow-text">$2.4M</div>
            <div className="text-sm text-muted-foreground mt-2">Based on cost savings, risk mitigation, and efficiency gains</div>
          </div>
          <DollarSign className="h-16 w-16 text-primary/20" />
        </CardContent>
      </Card>

      {/* Charts */}
      <div className="grid lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2 bg-card border-border">
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-semibold text-foreground">Token Usage Over Time</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={tokenData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(222, 25%, 18%)" />
                <XAxis dataKey="day" stroke="hsl(215, 20%, 55%)" fontSize={12} />
                <YAxis stroke="hsl(215, 20%, 55%)" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(222, 40%, 10%)",
                    border: "1px solid hsl(222, 25%, 18%)",
                    borderRadius: "8px",
                    color: "hsl(210, 40%, 92%)",
                    fontSize: "12px",
                  }}
                />
                <Line type="monotone" dataKey="tokens" stroke="hsl(155, 100%, 50%)" strokeWidth={2} dot={{ fill: "hsl(155, 100%, 50%)", r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="bg-card border-border">
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-semibold text-foreground">Safe vs Anomalous</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center">
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={actionData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
                  dataKey="value"
                  strokeWidth={0}
                >
                  {actionData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(222, 40%, 10%)",
                    border: "1px solid hsl(222, 25%, 18%)",
                    borderRadius: "8px",
                    color: "hsl(210, 40%, 92%)",
                    fontSize: "12px",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex gap-6 mt-2">
              {actionData.map((d) => (
                <div key={d.name} className="flex items-center gap-2 text-xs">
                  <div className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: d.color }} />
                  <span className="text-muted-foreground">{d.name}</span>
                  <span className="font-semibold text-foreground">{d.value}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ExecutiveTab;
