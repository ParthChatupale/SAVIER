import { useState, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  FileText, ChevronDown, ChevronUp, Filter, Search,
  ShieldCheck, AlertTriangle, Zap, DollarSign, Activity
} from "lucide-react";
import {
  PieChart, Pie, Cell, LineChart, Line, BarChart, Bar,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend
} from "recharts";

// --- Mock Data ---
const mockData = [
  { id: "run-001", timestamp: "2026-04-10 14:23:01", agent: "DataProcessor-A1", task: "ETL Pipeline Execution", action: "Processed 50k records", status: "Safe", thought: "Identified 50k records matching schema. Applied standard transformation pipeline.", toolInput: '{"source": "s3://data-lake/raw", "transform": "normalize"}', output: "Successfully processed and stored 50,000 records.", tokens: 1240, confidence: 0.97, flagReason: "" },
  { id: "run-002", timestamp: "2026-04-10 14:22:45", agent: "SecurityBot-B3", task: "Vulnerability Scan", action: "Escalated CVE-2026-1234", status: "Warning", thought: "Detected medium-severity vulnerability in dependency tree. Recommending immediate patch.", toolInput: '{"scan_target": "production-api", "depth": "full"}', output: "Found 3 vulnerabilities: 1 medium, 2 low.", tokens: 890, confidence: 0.82, flagReason: "High deviation from expected output pattern" },
  { id: "run-003", timestamp: "2026-04-10 14:22:12", agent: "ComplianceAgent-C2", task: "GDPR Data Audit", action: "Flagged PII exposure", status: "Critical", thought: "Found unencrypted PII in staging environment log files. Immediate action required.", toolInput: '{"audit_scope": "staging-logs", "regulation": "GDPR"}', output: "ALERT: PII data found in 12 log files.", tokens: 2100, confidence: 0.65, flagReason: "Unencrypted PII detected in non-production environment" },
  { id: "run-004", timestamp: "2026-04-10 14:21:33", agent: "DeployBot-D1", task: "CI/CD Pipeline", action: "Deployed v2.3.1", status: "Safe", thought: "All tests passing. No breaking changes detected. Proceeding with canary deployment.", toolInput: '{"version": "2.3.1", "strategy": "canary"}', output: "Deployment successful. Canary at 10%.", tokens: 560, confidence: 0.99, flagReason: "" },
  { id: "run-005", timestamp: "2026-04-10 14:20:58", agent: "CostOptimizer-E1", task: "Resource Scaling", action: "Reduced instances by 30%", status: "Safe", thought: "Current load at 25% capacity. Safe to scale down without performance impact.", toolInput: '{"action": "scale_down", "target": "web-cluster"}', output: "Scaled from 10 to 7 instances. Est. savings: $2,400/mo.", tokens: 780, confidence: 0.94, flagReason: "" },
  { id: "run-006", timestamp: "2026-04-10 14:19:44", agent: "SecurityBot-B3", task: "Access Review", action: "Revoked stale tokens", status: "Warning", thought: "Found 23 API tokens unused for 90+ days. Policy requires revocation.", toolInput: '{"review_type": "token_audit", "threshold_days": 90}', output: "Revoked 23 stale tokens. Notified 8 users.", tokens: 1050, confidence: 0.78, flagReason: "Automated revocation of 23 tokens may impact active integrations" },
  { id: "run-007", timestamp: "2026-04-10 14:18:20", agent: "DataProcessor-A1", task: "Data Migration", action: "Migrated 120k rows", status: "Safe", thought: "Schema validated. All foreign keys intact. Running in batch mode.", toolInput: '{"source": "legacy-db", "target": "cloud-db", "batch_size": 5000}', output: "Migration complete. 120,000 rows transferred.", tokens: 1800, confidence: 0.96, flagReason: "" },
  { id: "run-008", timestamp: "2026-04-10 14:17:05", agent: "ComplianceAgent-C2", task: "SOC2 Audit Check", action: "Verified access controls", status: "Safe", thought: "All access controls meet SOC2 requirements. No deviations found.", toolInput: '{"audit_type": "SOC2", "scope": "access-controls"}', output: "SOC2 access control audit passed.", tokens: 670, confidence: 0.98, flagReason: "" },
];

const statusColors: Record<string, string> = {
  Safe: "bg-primary/10 text-primary border-primary/20",
  Warning: "bg-warning/10 text-warning border-warning/20",
  Critical: "bg-destructive/10 text-destructive border-destructive/20",
};

const statusRowBorder: Record<string, string> = {
  Safe: "border-l-2 border-l-primary/40",
  Warning: "border-l-2 border-l-warning/40",
  Critical: "border-l-2 border-l-destructive/40",
};

// --- Chart Data ---
const riskDistribution = [
  { name: "Safe", value: 5, color: "hsl(155, 100%, 50%)" },
  { name: "Warning", value: 2, color: "hsl(38, 92%, 50%)" },
  { name: "Critical", value: 1, color: "hsl(0, 72%, 51%)" },
];

const executionTrend = [
  { time: "14:00", executions: 2 },
  { time: "14:05", executions: 5 },
  { time: "14:10", executions: 3 },
  { time: "14:15", executions: 7 },
  { time: "14:20", executions: 4 },
  { time: "14:25", executions: 8 },
];

const agentActivity = [
  { agent: "DataProcessor", executions: 3 },
  { agent: "SecurityBot", executions: 2 },
  { agent: "ComplianceAgent", executions: 2 },
  { agent: "DeployBot", executions: 1 },
  { agent: "CostOptimizer", executions: 1 },
];

const anomalyRate = 25; // percent

const ComplianceTab = () => {
  const [expandedRow, setExpandedRow] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterStatus, setFilterStatus] = useState("All");

  const filtered = useMemo(() => {
    return mockData.filter((row) => {
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        if (!row.agent.toLowerCase().includes(q) && !row.task.toLowerCase().includes(q)) return false;
      }
      if (filterStatus !== "All" && row.status !== filterStatus) return false;
      return true;
    });
  }, [searchQuery, filterStatus]);

  const totalExecutions = mockData.length;
  const criticalAlerts = mockData.filter((r) => r.status === "Critical").length;
  const avgConfidence = (mockData.reduce((s, r) => s + r.confidence, 0) / mockData.length * 100).toFixed(1);

  const CustomTooltipChart = ({ active, payload, label }: any) => {
    if (!active || !payload?.length) return null;
    return (
      <div className="rounded-lg border border-border bg-card px-3 py-2 text-xs shadow-lg">
        <p className="text-muted-foreground mb-1">{label}</p>
        {payload.map((p: any, i: number) => (
          <p key={i} className="text-foreground font-medium">{p.name}: {p.value}</p>
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">Compliance & Audit Hub</h1>
        <p className="text-muted-foreground mt-1">Monitor and review all AI agent executions with full traceability and risk analysis.</p>
        <p className="text-xs text-muted-foreground/70 mt-1">Each entry represents a single agent execution with its outcome and risk classification.</p>
      </div>

      {/* Section 1: Visual Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {/* Risk Distribution Donut */}
        <Card className="bg-card border-border hover:border-primary/20 transition-colors">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Risk Distribution</CardTitle>
          </CardHeader>
          <CardContent className="flex justify-center">
            <ResponsiveContainer width={160} height={160}>
              <PieChart>
                <Pie
                  data={riskDistribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={45}
                  outerRadius={70}
                  dataKey="value"
                  stroke="none"
                  onClick={(entry) => {
                    setFilterStatus(filterStatus === entry.name ? "All" : entry.name);
                  }}
                  className="cursor-pointer"
                >
                  {riskDistribution.map((entry, i) => (
                    <Cell key={i} fill={entry.color} opacity={filterStatus === "All" || filterStatus === entry.name ? 1 : 0.3} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltipChart />} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
          <div className="flex justify-center gap-3 pb-4 text-xs">
            {riskDistribution.map((r) => (
              <div key={r.name} className="flex items-center gap-1">
                <div className="h-2 w-2 rounded-full" style={{ backgroundColor: r.color }} />
                <span className="text-muted-foreground">{r.name}</span>
              </div>
            ))}
          </div>
        </Card>

        {/* Execution Trend */}
        <Card className="bg-card border-border hover:border-primary/20 transition-colors">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Execution Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={150}>
              <LineChart data={executionTrend}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(222, 25%, 18%)" />
                <XAxis dataKey="time" tick={{ fontSize: 10, fill: "hsl(215, 20%, 55%)" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 10, fill: "hsl(215, 20%, 55%)" }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltipChart />} />
                <Line type="monotone" dataKey="executions" stroke="hsl(155, 100%, 50%)" strokeWidth={2} dot={{ fill: "hsl(155, 100%, 50%)", r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Anomaly Rate */}
        <Card className="bg-card border-border hover:border-primary/20 transition-colors">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Anomaly Rate</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center gap-3 pt-4">
            <div className="relative w-28 h-28">
              <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
                <circle cx="50" cy="50" r="40" fill="none" stroke="hsl(222, 25%, 18%)" strokeWidth="8" />
                <circle
                  cx="50" cy="50" r="40" fill="none"
                  stroke="hsl(38, 92%, 50%)"
                  strokeWidth="8"
                  strokeDasharray={`${anomalyRate * 2.51} ${251 - anomalyRate * 2.51}`}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-xl font-bold text-foreground">{anomalyRate}%</span>
              </div>
            </div>
            <p className="text-xs text-muted-foreground">of executions flagged</p>
          </CardContent>
        </Card>

        {/* Agent Activity */}
        <Card className="bg-card border-border hover:border-primary/20 transition-colors">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Agent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={150}>
              <BarChart data={agentActivity} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(222, 25%, 18%)" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 10, fill: "hsl(215, 20%, 55%)" }} axisLine={false} tickLine={false} />
                <YAxis dataKey="agent" type="category" tick={{ fontSize: 9, fill: "hsl(215, 20%, 55%)" }} axisLine={false} tickLine={false} width={85} />
                <Tooltip content={<CustomTooltipChart />} />
                <Bar dataKey="executions" fill="hsl(155, 100%, 50%)" radius={[0, 4, 4, 0]} barSize={14} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Section 2: Metrics Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard icon={Activity} label="Total Executions" value={totalExecutions.toString()} accent="primary" />
        <MetricCard icon={AlertTriangle} label="Critical Alerts" value={criticalAlerts.toString()} accent="destructive" />
        <MetricCard icon={ShieldCheck} label="Avg Confidence" value={`${avgConfidence}%`} accent="primary" />
        <MetricCard icon={DollarSign} label="Estimated ROI" value="$18.4K" accent="primary" />
      </div>

      {/* Section 3: Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-2 text-muted-foreground">
          <Filter className="h-4 w-4" />
        </div>
        <div className="relative flex-1 max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by Agent Name or Task..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 h-9 bg-secondary border-border text-sm"
          />
        </div>
        <div className="flex gap-1">
          {["All", "Safe", "Warning", "Critical"].map((s) => (
            <Button
              key={s}
              variant={filterStatus === s ? "default" : "ghost"}
              size="sm"
              onClick={() => setFilterStatus(s)}
              className="h-8 text-xs"
            >
              {s}
            </Button>
          ))}
        </div>
        <div className="ml-auto">
          <Button variant="outline" size="sm">
            <FileText className="h-4 w-4 mr-2" />
            Generate CIO Governance Brief
          </Button>
        </div>
      </div>

      {/* Section 4: Table */}
      {filtered.length === 0 ? (
        <Card className="bg-card border-border">
          <CardContent className="flex flex-col items-center justify-center py-16 text-muted-foreground">
            <ShieldCheck className="h-10 w-10 mb-3 text-primary/40" />
            <p className="text-sm font-medium">No agent executions recorded yet</p>
            <p className="text-xs mt-1">Executions will appear here once agents start running.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="rounded-xl border border-border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-secondary/50">
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">Execution Time</th>
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">Execution ID</th>
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">Agent Name</th>
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">Assigned Task</th>
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">Outcome</th>
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">Risk Status</th>
                  <th className="w-10" />
                </tr>
              </thead>
              <tbody>
                {filtered.map((row) => (
                  <TableRow key={row.id} row={row} expanded={expandedRow === row.id} onToggle={() => setExpandedRow(expandedRow === row.id ? null : row.id)} />
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

// --- Sub-components ---

function MetricCard({ icon: Icon, label, value, accent }: { icon: any; label: string; value: string; accent: string }) {
  const accentClass = accent === "destructive" ? "text-destructive" : "text-primary";
  return (
    <Card className="bg-card border-border hover:border-primary/20 transition-colors group">
      <CardContent className="flex items-center gap-4 py-4 px-5">
        <div className={`p-2 rounded-lg bg-${accent}/10`}>
          <Icon className={`h-5 w-5 ${accentClass}`} />
        </div>
        <div>
          <p className="text-xs text-muted-foreground">{label}</p>
          <p className={`text-xl font-bold ${accentClass}`}>{value}</p>
        </div>
      </CardContent>
    </Card>
  );
}

function TableRow({ row, expanded, onToggle }: { row: typeof mockData[0]; expanded: boolean; onToggle: () => void }) {
  return (
    <>
      <tr
        className={`border-b border-border/50 hover:bg-secondary/30 cursor-pointer transition-colors ${statusRowBorder[row.status]}`}
        onClick={onToggle}
      >
        <td className="py-3 px-4 font-mono text-xs text-muted-foreground">{row.timestamp}</td>
        <td className="py-3 px-4 font-mono text-xs text-primary">{row.id}</td>
        <td className="py-3 px-4 font-medium text-foreground">{row.agent}</td>
        <td className="py-3 px-4 text-foreground">{row.task}</td>
        <td className="py-3 px-4 text-muted-foreground">{row.action}</td>
        <td className="py-3 px-4">
          <Badge variant="outline" className={statusColors[row.status]}>{row.status}</Badge>
        </td>
        <td className="py-3 px-4">
          {expanded ? <ChevronUp className="h-4 w-4 text-muted-foreground" /> : <ChevronDown className="h-4 w-4 text-muted-foreground" />}
        </td>
      </tr>
      {expanded && (
        <tr className="bg-secondary/20">
          <td colSpan={7} className="px-4 py-4">
            <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-4 text-xs">
              <div>
                <span className="text-muted-foreground font-medium block mb-1">Thought Process</span>
                <p className="text-foreground bg-card rounded-lg p-3 border border-border">{row.thought}</p>
              </div>
              <div>
                <span className="text-muted-foreground font-medium block mb-1">Tool Input / Output</span>
                <pre className="text-primary font-mono bg-card rounded-lg p-3 border border-border overflow-x-auto mb-2">{row.toolInput}</pre>
                <p className="text-foreground bg-card rounded-lg p-3 border border-border">{row.output}</p>
              </div>
              <div>
                <span className="text-muted-foreground font-medium block mb-1">Token Usage / Metadata</span>
                <div className="bg-card rounded-lg p-3 border border-border space-y-1">
                  <p className="text-foreground">Tokens: <span className="text-primary font-mono">{row.tokens}</span></p>
                  <p className="text-foreground">Confidence: <span className="text-primary font-mono">{(row.confidence * 100).toFixed(0)}%</span></p>
                </div>
              </div>
              <div>
                <span className="text-muted-foreground font-medium block mb-1">Flag Reason</span>
                <p className={`bg-card rounded-lg p-3 border border-border ${row.flagReason ? "text-warning" : "text-muted-foreground/60 italic"}`}>
                  {row.flagReason || "No anomalies detected"}
                </p>
              </div>
            </div>
          </td>
        </tr>
      )}
    </>
  );
}

export default ComplianceTab;
