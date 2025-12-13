import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { Card } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

const loans = [
  { id: "LN001", amount: "₹2,00,000", date: "Jan 2024", status: "Closed", emi: "₹6,500" },
  { id: "LN002", amount: "₹5,00,000", date: "Dec 2024", status: "Active", emi: "₹16,250" },
];

const LoanHistory = () => (
  <DashboardLayout>
    <div className="mb-6">
      <h1 className="text-3xl font-bold">Loan History</h1>
      <p className="text-muted-foreground">View your past and current loans</p>
    </div>
    <Card variant="glass" className="overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Loan ID</TableHead>
            <TableHead>Amount</TableHead>
            <TableHead>Date</TableHead>
            <TableHead>EMI</TableHead>
            <TableHead>Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {loans.map((loan) => (
            <TableRow key={loan.id} className="hover:bg-primary/5 transition-colors">
              <TableCell className="font-medium">{loan.id}</TableCell>
              <TableCell>{loan.amount}</TableCell>
              <TableCell>{loan.date}</TableCell>
              <TableCell>{loan.emi}</TableCell>
              <TableCell>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${loan.status === "Active" ? "bg-primary/10 text-primary" : "bg-success/10 text-success"}`}>
                  {loan.status}
                </span>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Card>
  </DashboardLayout>
);

export default LoanHistory;
