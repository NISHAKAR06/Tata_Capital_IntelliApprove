import { motion } from "framer-motion";
import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const Analytics = () => (
  <DashboardLayout>
    <div className="mb-6">
      <h1 className="text-3xl font-bold">Analytics</h1>
      <p className="text-muted-foreground">View your loan analytics and insights</p>
    </div>
    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
      {[
        { title: "Total Borrowed", value: "₹7,00,000", color: "primary" },
        { title: "Total Repaid", value: "₹2,50,000", color: "success" },
        { title: "Outstanding", value: "₹4,50,000", color: "warning" },
      ].map((stat, i) => (
        <motion.div key={stat.title} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
          <Card variant="glass">
            <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">{stat.title}</CardTitle></CardHeader>
            <CardContent><p className={`text-3xl font-bold text-${stat.color}`}>{stat.value}</p></CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
    <Card variant="glass" className="mt-6 p-8 text-center">
      <p className="text-muted-foreground">Detailed analytics charts coming soon...</p>
    </Card>
  </DashboardLayout>
);

export default Analytics;
