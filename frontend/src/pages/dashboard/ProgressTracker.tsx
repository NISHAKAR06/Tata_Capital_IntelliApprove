import { motion } from "framer-motion";
import { Check, Circle, Clock } from "lucide-react";
import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { Card } from "@/components/ui/card";

const steps = [
  { id: 1, title: "Application Submitted", status: "completed", date: "Dec 10, 2024" },
  { id: 2, title: "Document Verification", status: "completed", date: "Dec 11, 2024" },
  { id: 3, title: "Credit Assessment", status: "current", date: "In Progress" },
  { id: 4, title: "Loan Approval", status: "pending", date: "Pending" },
  { id: 5, title: "Disbursement", status: "pending", date: "Pending" },
];

const ProgressTracker = () => {
  return (
    <DashboardLayout>
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Progress Tracker</h1>
        <p className="text-muted-foreground">Track your loan application progress</p>
      </div>

      <Card variant="glass" className="p-8">
        <div className="relative">
          {/* Progress Line */}
          <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-border">
            <motion.div
              className="w-full bg-primary"
              initial={{ height: 0 }}
              animate={{ height: "40%" }}
              transition={{ duration: 1, ease: "easeOut" }}
            />
          </div>

          {/* Steps */}
          <div className="space-y-8">
            {steps.map((step, index) => (
              <motion.div
                key={step.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.15 }}
                className="relative flex items-center gap-6 pl-14"
              >
                {/* Icon */}
                <div
                  className={`absolute left-0 w-12 h-12 rounded-full flex items-center justify-center z-10 transition-all duration-300 ${
                    step.status === "completed"
                      ? "bg-success text-success-foreground"
                      : step.status === "current"
                      ? "bg-primary text-primary-foreground animate-glow"
                      : "bg-secondary text-muted-foreground"
                  }`}
                >
                  {step.status === "completed" ? (
                    <Check className="w-6 h-6" />
                  ) : step.status === "current" ? (
                    <Clock className="w-6 h-6" />
                  ) : (
                    <Circle className="w-6 h-6" />
                  )}
                </div>

                {/* Content */}
                <Card
                  variant={step.status === "current" ? "elevated" : "default"}
                  className={`flex-1 p-4 ${
                    step.status === "current" ? "border-2 border-primary" : ""
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold text-lg">{step.title}</h3>
                      <p className="text-sm text-muted-foreground">{step.date}</p>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${
                        step.status === "completed"
                          ? "bg-success/10 text-success"
                          : step.status === "current"
                          ? "bg-primary/10 text-primary"
                          : "bg-secondary text-muted-foreground"
                      }`}
                    >
                      {step.status === "completed"
                        ? "Completed"
                        : step.status === "current"
                        ? "In Progress"
                        : "Pending"}
                    </span>
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </Card>
    </DashboardLayout>
  );
};

export default ProgressTracker;
