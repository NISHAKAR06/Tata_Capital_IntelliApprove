import { motion } from "framer-motion";
import { FileText, Download } from "lucide-react";
import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const SanctionLetter = () => (
  <DashboardLayout>
    <div className="mb-6">
      <h1 className="text-3xl font-bold">Sanction Letter</h1>
      <p className="text-muted-foreground">View and download your sanction letter</p>
    </div>
    <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}>
      <Card variant="glass" className="p-8 text-center">
        <div className="w-20 h-20 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-6">
          <FileText className="w-10 h-10 text-primary" />
        </div>
        <h3 className="text-xl font-semibold mb-2">Sanction Letter Ready</h3>
        <p className="text-muted-foreground mb-6">Your loan has been sanctioned. Download the letter below.</p>
        <Button variant="hero" size="lg" className="animate-pulse-soft">
          <Download className="w-5 h-5 mr-2" /> Download Sanction Letter
        </Button>
      </Card>
    </motion.div>
  </DashboardLayout>
);

export default SanctionLetter;
