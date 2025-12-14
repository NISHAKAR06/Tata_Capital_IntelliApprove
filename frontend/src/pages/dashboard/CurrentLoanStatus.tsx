import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { CreditCard, IndianRupee, Calendar, TrendingUp } from "lucide-react";
import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useConversation } from "@/contexts/ConversationContext";
import { acceptSanction, getConversationState } from "@/lib/api";
import { toast } from "@/components/ui/sonner";

interface LoanOfferSnapshot {
  amount?: number;
  tenure?: number;
  personalized_rate?: number;
  emi?: number;
}

const CurrentLoanStatus = () => {
  const { conversationId } = useConversation();
  const [stage, setStage] = useState<string | null>(null);
  const [offer, setOffer] = useState<LoanOfferSnapshot | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isAccepting, setIsAccepting] = useState(false);

  useEffect(() => {
    const loadState = async () => {
      if (!conversationId) return;
      try {
        setIsLoading(true);
        const resp = await getConversationState(conversationId);
        setStage(resp.stage);
        const stateOffer = (resp.state_updates?.offer ||
          {}) as LoanOfferSnapshot;
        setOffer(stateOffer);
      } catch (error) {
        console.error(error);
        toast.error("Unable to load current loan status.");
      } finally {
        setIsLoading(false);
      }
    };

    loadState();
  }, [conversationId]);

  const amount = offer?.amount ?? 500000;
  const rate = offer?.personalized_rate ?? 10.5;
  const tenure = offer?.tenure ?? 36;
  const emi = offer?.emi ?? 16250;
  const stageLabel =
    stage ?? (conversationId ? "Processing" : "No Active Application");

  const canAccept = stage === "COMPLETED" && !!conversationId;

  const handleAcceptSanction = async () => {
    if (!conversationId || !canAccept || isAccepting) return;
    try {
      setIsAccepting(true);
      const resp = await acceptSanction(conversationId);
      toast.success(resp.message || "Sanction accepted and funds disbursed.");
    } catch (err) {
      console.error(err);
      toast.error("Unable to accept sanction. Please try again.");
    } finally {
      setIsAccepting(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Current Loan Status</h1>
        <p className="text-muted-foreground">View your active loan details</p>
      </div>

      <div className="grid gap-6">
        {/* Status Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Card variant="glass" className="status-card status-processing">
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <CardTitle>Personal Loan Application</CardTitle>
                <span className="px-4 py-2 rounded-full bg-primary/10 text-primary font-medium text-sm">
                  {isLoading ? "Loading..." : stageLabel}
                </span>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                    <IndianRupee className="w-6 h-6 text-primary" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Loan Amount</p>
                    <p className="text-xl font-bold">
                      ₹{amount.toLocaleString("en-IN")}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-success/10 flex items-center justify-center">
                    <TrendingUp className="w-6 h-6 text-success" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">
                      Interest Rate
                    </p>
                    <p className="text-xl font-bold">{rate}% p.a.</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-warning/10 flex items-center justify-center">
                    <Calendar className="w-6 h-6 text-warning" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Tenure</p>
                    <p className="text-xl font-bold">{tenure} Months</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center">
                    <CreditCard className="w-6 h-6 text-accent" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">EMI</p>
                    <p className="text-xl font-bold">
                      ₹{emi.toLocaleString("en-IN")}
                    </p>
                  </div>
                </div>
              </div>
              {canAccept && (
                <div className="mt-6 flex justify-end">
                  <Button
                    variant="hero"
                    onClick={handleAcceptSanction}
                    disabled={isAccepting}
                  >
                    {isAccepting
                      ? "Processing..."
                      : "Accept Sanction & Disburse"}
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Additional Status Cards */}
        <div className="grid md:grid-cols-2 gap-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card variant="glass" className="status-card status-approved">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">Previous Loan</CardTitle>
                  <span className="px-3 py-1 rounded-full bg-success/10 text-success font-medium text-sm">
                    Completed
                  </span>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Amount</span>
                    <span className="font-medium">₹2,00,000</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Closed On</span>
                    <span className="font-medium">Oct 15, 2024</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card variant="glass" className="p-6">
              <h3 className="font-semibold text-lg mb-4">Credit Score</h3>
              <div className="flex items-center gap-4">
                <div className="relative w-24 h-24">
                  <svg className="w-full h-full -rotate-90">
                    <circle
                      cx="48"
                      cy="48"
                      r="40"
                      fill="none"
                      stroke="hsl(var(--secondary))"
                      strokeWidth="8"
                    />
                    <motion.circle
                      cx="48"
                      cy="48"
                      r="40"
                      fill="none"
                      stroke="hsl(var(--success))"
                      strokeWidth="8"
                      strokeLinecap="round"
                      strokeDasharray={251.2}
                      initial={{ strokeDashoffset: 251.2 }}
                      animate={{ strokeDashoffset: 251.2 * 0.25 }}
                      transition={{ duration: 1, delay: 0.5 }}
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-2xl font-bold text-success">750</span>
                  </div>
                </div>
                <div>
                  <p className="font-medium text-success">Excellent</p>
                  <p className="text-sm text-muted-foreground">
                    Last updated: Dec 1, 2024
                  </p>
                </div>
              </div>
            </Card>
          </motion.div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default CurrentLoanStatus;
