import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Shield, Activity, TrendingUp, FileText, Zap, Eye, BarChart3, Lock } from "lucide-react";

const features = [
  { icon: Activity, title: "Real-Time Monitoring", desc: "Track every agent action as it happens with sub-second latency" },
  { icon: Shield, title: "Anomaly Detection", desc: "AI-powered behavioral analysis catches threats before they escalate" },
  { icon: TrendingUp, title: "ROI Tracking", desc: "Quantify the business value of your autonomous agent deployments" },
  { icon: FileText, title: "Audit Logs", desc: "Complete immutable audit trails for compliance and governance" },
];

const stats = [
  { value: "99.97%", label: "Uptime SLA" },
  { value: "<50ms", label: "Detection Latency" },
  { value: "10M+", label: "Events/Day" },
  { value: "SOC2", label: "Certified" },
];

const Landing = () => {
  return (
    <div className="min-h-screen bg-background">
      {/* Nav */}
      <nav className="border-b border-border/50 backdrop-blur-sm sticky top-0 z-50 bg-background/80">
        <div className="container mx-auto flex items-center justify-between h-16 px-6">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-primary/20 flex items-center justify-center">
              <Shield className="h-5 w-5 text-primary" />
            </div>
            <span className="text-xl font-bold tracking-tight text-foreground">Savier</span>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="ghost" asChild>
              <Link to="/auth">Login</Link>
            </Button>
            <Button variant="hero" asChild>
              <Link to="/auth?tab=signup">Get Started</Link>
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-grid opacity-30" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full bg-primary/5 blur-[120px]" />
        <div className="container mx-auto px-6 pt-24 pb-20 relative">
          <div className="max-w-3xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-primary/30 bg-primary/5 text-primary text-sm font-medium mb-8 animate-fade-in">
              <Zap className="h-3.5 w-3.5" />
              Autonomous Agent Governance Platform
            </div>
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-extrabold tracking-tight mb-6 animate-slide-up text-foreground">
              Monitor, Analyze, and{" "}
              <span className="text-gradient glow-text">Govern AI Agents</span>{" "}
              in Real-Time
            </h1>
            <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 animate-slide-up" style={{ animationDelay: "0.1s" }}>
              Enterprise-grade observability and compliance for autonomous AI agents. 
              Detect anomalies, enforce policies, and prove ROI — all from one dashboard.
            </p>
            <div className="flex items-center justify-center gap-4 animate-slide-up" style={{ animationDelay: "0.2s" }}>
              <Button variant="hero" size="lg" asChild>
                <Link to="/auth?tab=signup">Get Started Free</Link>
              </Button>
              <Button variant="hero-outline" size="lg" asChild>
                <Link to="/auth">Login</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="border-y border-border/50 bg-card/30">
        <div className="container mx-auto px-6 py-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((s) => (
              <div key={s.label} className="text-center">
                <div className="text-3xl font-bold text-primary glow-text">{s.value}</div>
                <div className="text-sm text-muted-foreground mt-1">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-6 py-24">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            Everything you need to govern AI agents
          </h2>
          <p className="text-muted-foreground max-w-xl mx-auto">
            Built for enterprise compliance officers and CIOs who need complete visibility into autonomous agent operations.
          </p>
        </div>
        <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
          {features.map((f, i) => (
            <div
              key={f.title}
              className="group p-6 rounded-xl border border-border bg-card card-hover animate-slide-up"
              style={{ animationDelay: `${i * 0.1}s` }}
            >
              <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                <f.icon className="h-5 w-5 text-primary" />
              </div>
              <h3 className="text-lg font-semibold text-foreground mb-2">{f.title}</h3>
              <p className="text-muted-foreground text-sm leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="container mx-auto px-6 pb-24">
        <div className="rounded-2xl border border-primary/20 bg-gradient-to-br from-primary/5 to-transparent p-12 text-center animate-glow-pulse">
          <h2 className="text-3xl font-bold text-foreground mb-4">Ready to govern your AI agents?</h2>
          <p className="text-muted-foreground mb-8 max-w-lg mx-auto">Start monitoring in minutes. No infrastructure to manage.</p>
          <Button variant="hero" size="lg" asChild>
            <Link to="/auth?tab=signup">Start Free Trial</Link>
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/50 py-8">
        <div className="container mx-auto px-6 flex items-center justify-between text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <Shield className="h-4 w-4 text-primary" />
            <span>Savier</span>
          </div>
          <span>© 2026 Savier. All rights reserved.</span>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
