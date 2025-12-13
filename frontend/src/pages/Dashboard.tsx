import { Navigate } from "react-router-dom";
import { DashboardLayout } from "@/components/dashboard/DashboardLayout";

const Dashboard = () => {
  // Redirect to chat by default
  return <Navigate to="/dashboard/chat" replace />;
};

export default Dashboard;
