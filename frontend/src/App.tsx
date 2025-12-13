import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { LanguageProvider } from "@/contexts/LanguageContext";
import { ThemeProvider } from "@/contexts/ThemeContext";
import Index from "./pages/Index";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import LoanChat from "./pages/dashboard/LoanChat";
import ProgressTracker from "./pages/dashboard/ProgressTracker";
import CurrentLoanStatus from "./pages/dashboard/CurrentLoanStatus";
import DocumentUpload from "./pages/dashboard/DocumentUpload";
import SanctionLetter from "./pages/dashboard/SanctionLetter";
import LoanHistory from "./pages/dashboard/LoanHistory";
import Analytics from "./pages/dashboard/Analytics";
import NotFound from "./pages/NotFound";
import { GlobalHeader } from "@/components/ui/global-header";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <ThemeProvider>
        <LanguageProvider>
          <BrowserRouter>
            <GlobalHeader />
            <Routes>
              <Route path="/" element={<Index />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/dashboard/chat" element={<LoanChat />} />
              <Route path="/dashboard/progress" element={<ProgressTracker />} />
              <Route path="/dashboard/status" element={<CurrentLoanStatus />} />
              <Route path="/dashboard/documents" element={<DocumentUpload />} />
              <Route path="/dashboard/sanction" element={<SanctionLetter />} />
              <Route path="/dashboard/history" element={<LoanHistory />} />
              <Route path="/dashboard/analytics" element={<Analytics />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </BrowserRouter>
        </LanguageProvider>
      </ThemeProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
