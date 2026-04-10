import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Shield, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import ComplianceTab from "@/components/dashboard/ComplianceTab";
import CommandCenterTab from "@/components/dashboard/CommandCenterTab";
import ExecutiveTab from "@/components/dashboard/ExecutiveTab";

const Dashboard = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("compliance");

  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b border-border/50 bg-background/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto flex items-center justify-between h-14 px-6">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => navigate("/projects")}>
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <div className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-primary" />
              <span className="font-bold text-foreground">Savier</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-primary animate-pulse-slow" />
            <span className="text-xs text-muted-foreground font-mono">LIVE</span>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-6 py-6">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="bg-secondary/50 border border-border mb-6">
            <TabsTrigger value="compliance" className="data-[state=active]:bg-primary/10 data-[state=active]:text-primary">
              Compliance & Audit
            </TabsTrigger>
            <TabsTrigger value="command" className="data-[state=active]:bg-primary/10 data-[state=active]:text-primary">
              Command Center
            </TabsTrigger>
            <TabsTrigger value="executive" className="data-[state=active]:bg-primary/10 data-[state=active]:text-primary">
              Executive Overview
            </TabsTrigger>
          </TabsList>

          <TabsContent value="compliance"><ComplianceTab /></TabsContent>
          <TabsContent value="command"><CommandCenterTab /></TabsContent>
          <TabsContent value="executive"><ExecutiveTab /></TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Dashboard;
