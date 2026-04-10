import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Shield, Plus, Copy, Check, FolderOpen, Key, ArrowRight } from "lucide-react";

interface Project {
  id: string;
  name: string;
  createdAt: string;
  agents: number;
}

const Projects = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [projectName, setProjectName] = useState("");
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const createProject = () => {
    if (!projectName.trim()) return;
    const key = `sv_${crypto.randomUUID().replace(/-/g, "").slice(0, 32)}`;
    const newProject: Project = {
      id: crypto.randomUUID(),
      name: projectName,
      createdAt: new Date().toISOString(),
      agents: 0,
    };
    setProjects((prev) => [newProject, ...prev]);
    setApiKey(key);
    setProjectName("");
  };

  const copyKey = () => {
    if (apiKey) {
      navigator.clipboard.writeText(apiKey);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const closeCreate = () => {
    setShowCreate(false);
    setApiKey(null);
    setProjectName("");
  };

  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b border-border/50 bg-background/80 backdrop-blur-sm">
        <div className="container mx-auto flex items-center justify-between h-16 px-6">
          <div className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-primary" />
            <span className="text-lg font-bold text-foreground">Savier</span>
          </div>
          <Button variant="ghost" size="sm" onClick={() => navigate("/")}>
            Logout
          </Button>
        </div>
      </nav>

      <div className="container mx-auto px-6 py-12 max-w-3xl">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-foreground">Projects</h1>
            <p className="text-sm text-muted-foreground mt-1">Manage your agent governance workspaces</p>
          </div>
          <Button variant="hero" onClick={() => setShowCreate(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Create Project
          </Button>
        </div>

        {/* Create Project Modal */}
        {showCreate && (
          <div className="mb-8 p-6 rounded-xl border border-border bg-card animate-fade-in">
            {!apiKey ? (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-foreground">New Project</h3>
                <Input
                  placeholder="Project name (e.g., Production Agents)"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  className="bg-secondary border-border"
                  onKeyDown={(e) => e.key === "Enter" && createProject()}
                />
                <div className="flex gap-3">
                  <Button variant="hero" onClick={createProject}>Create</Button>
                  <Button variant="ghost" onClick={closeCreate}>Cancel</Button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-primary">
                  <Key className="h-5 w-5" />
                  <h3 className="text-lg font-semibold">Your API Key</h3>
                </div>
                <p className="text-sm text-muted-foreground">
                  Copy this key now. It won't be shown again.
                </p>
                <div className="flex items-center gap-2">
                  <code className="flex-1 px-4 py-3 rounded-lg bg-secondary font-mono text-sm text-foreground break-all border border-border">
                    {apiKey}
                  </code>
                  <Button variant="outline" size="icon" onClick={copyKey}>
                    {copied ? <Check className="h-4 w-4 text-primary" /> : <Copy className="h-4 w-4" />}
                  </Button>
                </div>
                <Button variant="ghost" onClick={closeCreate}>Done</Button>
              </div>
            )}
          </div>
        )}

        {/* Project List */}
        {projects.length === 0 ? (
          <div className="text-center py-20 border border-dashed border-border rounded-xl">
            <FolderOpen className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium text-foreground mb-1">No projects yet</h3>
            <p className="text-sm text-muted-foreground">Create your first project to start monitoring agents.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {projects.map((p) => (
              <button
                key={p.id}
                onClick={() => navigate(`/dashboard/${p.id}`)}
                className="w-full flex items-center justify-between p-5 rounded-xl border border-border bg-card card-hover text-left group"
              >
                <div>
                  <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors">{p.name}</h3>
                  <p className="text-sm text-muted-foreground mt-0.5">
                    Created {new Date(p.createdAt).toLocaleDateString()} · {p.agents} agents
                  </p>
                </div>
                <ArrowRight className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Projects;
