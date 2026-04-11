import { useEffect, useRef, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Activity, AlertTriangle, ShieldAlert, Clock, Cpu, Zap } from "lucide-react";

const logEntries = [
  { time: "14:23:01.234", agent: "DataProcessor-A1", msg: "ETL pipeline completed. 50,000 records processed.", level: "info" },
  { time: "14:22:58.112", agent: "SecurityBot-B3", msg: "Vulnerability scan initiated on production-api", level: "info" },
  { time: "14:22:45.890", agent: "SecurityBot-B3", msg: "⚠ CVE-2026-1234 detected — medium severity", level: "warn" },
  { time: "14:22:33.445", agent: "ComplianceAgent-C2", msg: "GDPR audit started for staging-logs", level: "info" },
  { time: "14:22:12.001", agent: "ComplianceAgent-C2", msg: "🚨 CRITICAL: PII exposure in 12 log files", level: "error" },
  { time: "14:21:55.667", agent: "DeployBot-D1", msg: "Build v2.3.1 compiled successfully", level: "info" },
  { time: "14:21:33.221", agent: "DeployBot-D1", msg: "Canary deployment started at 10%", level: "info" },
  { time: "14:21:10.998", agent: "CostOptimizer-E1", msg: "Analyzing web-cluster resource utilization", level: "info" },
  { time: "14:20:58.432", agent: "CostOptimizer-E1", msg: "Scaled down: 10 → 7 instances. Saving $2,400/mo", level: "info" },
  { time: "14:20:44.100", agent: "SecurityBot-B3", msg: "⚠ 23 stale API tokens found (90+ days unused)", level: "warn" },
  { time: "14:20:22.876", agent: "DataProcessor-A1", msg: "Schema validation passed for incoming batch", level: "info" },
  { time: "14:19:58.543", agent: "ComplianceAgent-C2", msg: "SOC2 control check: all 14 controls passing", level: "info" },
];

const alerts = [
  { id: 1, severity: "critical", agent: "ComplianceAgent-C2", reason: "Unencrypted PII detected in staging log files. GDPR Article 32 violation.", time: "14:22:12" },
  { id: 2, severity: "warning", agent: "SecurityBot-B3", reason: "Behavioral anomaly: Agent accessed 3x more resources than baseline in scan cycle.", time: "14:22:45" },
  { id: 3, severity: "warning", agent: "SecurityBot-B3", reason: "Stale API tokens present security risk. Auto-revocation policy triggered.", time: "14:20:44" },
  { id: 4, severity: "critical", agent: "DeployBot-D1", reason: "Deployment attempted without required approval chain. Policy violation.", time: "14:18:30" },
  { id: 5, severity: "warning", agent: "CostOptimizer-E1", reason: "Resource scaling decision made without consulting capacity forecast model.", time: "14:17:55" },
];

const levelColors: Record<string, string> = {
  info: "text-muted-foreground",
  warn: "text-warning",
  error: "text-destructive",
};

const CommandCenterTab = () => {
  const logRef = useRef<HTMLDivElement>(null);
  const [activeAgents] = useState(5);
  const [latency] = useState("12ms");
  const [lastEvent] = useState("14:23:01");

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = 0;
    }
  }, []);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* System Bar */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { icon: Cpu, label: "Active Agents", value: activeAgents, color: "text-primary" },
          { icon: Zap, label: "Latency", value: latency, color: "text-primary" },
          { icon: Clock, label: "Last Event", value: lastEvent, color: "text-primary" },
        ].map((s) => (
          <div key={s.label} className="flex items-center gap-3 p-4 rounded-xl border border-border bg-card">
            <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <s.icon className={`h-5 w-5 ${s.color}`} />
            </div>
            <div>
              <div className="text-xs text-muted-foreground">{s.label}</div>
              <div className="text-lg font-bold text-foreground font-mono">{s.value}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Split Layout */}
      <div className="grid lg:grid-cols-5 gap-6">
        {/* Terminal Feed */}
        <div className="lg:col-span-3 rounded-xl border border-border bg-card overflow-hidden">
          <div className="flex items-center gap-2 px-4 py-3 border-b border-border bg-secondary/30">
            <Activity className="h-4 w-4 text-primary" />
            <span className="text-sm font-semibold text-foreground">Live Agent Feed</span>
            <div className="ml-auto flex items-center gap-1.5">
              <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
              <span className="text-xs text-muted-foreground font-mono">STREAMING</span>
            </div>
          </div>
          <div ref={logRef} className="h-[420px] overflow-y-auto p-4 font-mono text-xs space-y-1">
            {logEntries.map((entry, i) => (
              <div key={i} className="flex gap-2 py-1 hover:bg-secondary/20 rounded px-2 -mx-2 transition-colors">
                <span className="text-muted-foreground shrink-0">{entry.time}</span>
                <span className="text-primary shrink-0">[{entry.agent}]</span>
                <span className={levelColors[entry.level]}>{entry.msg}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Alert Center */}
        <div className="lg:col-span-2 rounded-xl border border-border bg-card overflow-hidden">
          <div className="flex items-center gap-2 px-4 py-3 border-b border-border bg-secondary/30">
            <AlertTriangle className="h-4 w-4 text-warning" />
            <span className="text-sm font-semibold text-foreground">Alert Center</span>
            <Badge variant="outline" className="ml-auto bg-destructive/10 text-destructive border-destructive/20 text-xs">
              {alerts.filter((a) => a.severity === "critical").length} Critical
            </Badge>
          </div>
          <div className="h-[420px] overflow-y-auto p-3 space-y-3">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className={`p-3 rounded-lg border ${
                  alert.severity === "critical"
                    ? "border-destructive/30 bg-destructive/5"
                    : "border-warning/30 bg-warning/5"
                }`}
              >
                <div className="flex items-center gap-2 mb-1.5">
                  {alert.severity === "critical" ? (
                    <ShieldAlert className="h-4 w-4 text-destructive" />
                  ) : (
                    <AlertTriangle className="h-4 w-4 text-warning" />
                  )}
                  <span className={`text-xs font-semibold uppercase ${
                    alert.severity === "critical" ? "text-destructive" : "text-warning"
                  }`}>
                    {alert.severity}
                  </span>
                  <span className="text-xs text-muted-foreground ml-auto font-mono">{alert.time}</span>
                </div>
                <p className="text-xs text-foreground leading-relaxed">{alert.reason}</p>
                <p className="text-xs text-muted-foreground mt-1">Agent: {alert.agent}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CommandCenterTab;
