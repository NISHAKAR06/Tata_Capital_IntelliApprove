import { Helmet } from 'react-helmet-async';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  User,
  MessageSquare,
  CheckCircle2,
  XCircle,
  FileText,
  Download,
  History,
  LogOut,
  Languages,
  Clock,
  Upload,
  AlertCircle,
  FileCheck,
  Calendar,
  CreditCard,
  HelpCircle,
  ChevronRight,
  ChevronDown,
  TrendingUp,
  Shield,
  BarChart3,
  Settings,
  Sun,
  Moon,
  Key
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

// Mock data for the dashboard
const currentLoan = {
  amount: '₹5,00,000',
  interestRate: 11.5,
  discount: 1.5,
  tenure: 60,
  emi: '₹12,450',
  status: 'approved',
  referenceId: 'LN20241207001'
};

const loanHistory = [
  { date: '2024-12-06', amount: '₹5,00,000', status: 'approved', reason: '-' },
  { date: '2024-11-15', amount: '₹3,00,000', status: 'approved', reason: '-' },
  { date: '2024-09-20', amount: '₹8,00,000', status: 'rejected', reason: 'Credit score below required threshold' },
];

const progressSteps = [
  { id: 1, name: 'Requirement Captured', completed: true, status: 'completed' },
  { id: 2, name: 'KYC Verified', completed: true, status: 'completed' },
  { id: 3, name: 'Credit Evaluated', completed: true, status: 'completed' },
  { id: 4, name: 'Salary Slip Checked', completed: false, status: 'in-progress' },
  { id: 5, name: 'Final Decision', completed: false, status: 'pending' },
];

const recentChatMessages = [
  { id: 1, content: "Hello! I'd like to apply for a personal loan.", sender: 'user', time: '2 mins ago' },
  { id: 2, content: "Hi! I'd be happy to help you with a personal loan application. What's your monthly income?", sender: 'bot', time: '2 mins ago' },
  { id: 3, content: "My salary is ₹85,000 per month", sender: 'user', time: '1 min ago' },
  { id: 4, content: "Great! Based on your income, you may be eligible for up to ₹5,00,000. Let me verify your employment details.", sender: 'bot', time: '1 min ago' },
];

const Dashboard = () => {
  const [language, setLanguage] = useState<'en' | 'ta'>('en');
  const [darkMode, setDarkMode] = useState(false);
  const [showSalaryUpload, setShowSalaryUpload] = useState(true);
  const [expandedCard, setExpandedCard] = useState<string | null>(null);

  // Apply dark mode to document
  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    if (!darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  const toggleCard = (cardId: string) => {
    setExpandedCard(expandedCard === cardId ? null : cardId);
  };

  return (
    <>
      <Helmet>
        <title>Dashboard | AI Loan Assistant</title>
        <meta name="description" content="Personal loan dashboard and application tracking." />
      </Helmet>

      <div className="min-h-screen bg-background">
        {/* 1. Header / Top Bar */}
        <header className="sticky top-0 z-10 border-b border-border bg-card/95 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                <User className="w-4 h-4 text-primary" />
              </div>
              <div>
                <p className="font-medium text-foreground">Rajesh Kumar</p>
                <p className="text-xs text-muted-foreground">
                  {language === 'en' ? 'Active Borrower' : 'செயலில் உள்ள கடன் வாங்குநர்'}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {/* Chat Button */}
              <Link to="/chat" title={language === 'en' ? 'Start Chat' : 'அரட்டையை தொடங்கு'}>
                <Button variant="outline" size="sm">
                  <MessageSquare className="w-4 h-4" />
                </Button>
              </Link>

              {/* Dark Mode Toggle */}
              <Button
                variant="outline"
                size="sm"
                onClick={toggleDarkMode}
                title={darkMode ? (language === 'en' ? 'Switch to Light Mode' : 'ஒளி முறைக்கு மாற்று') : (language === 'en' ? 'Switch to Dark Mode' : 'இருள் முறைக்கு மாற்று')}
              >
                {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
              </Button>

              {/* Language Switch */}
              <Button
                variant="outline"
                size="sm"
                onClick={() => setLanguage(language === 'en' ? 'ta' : 'en')}
                title={language === 'en' ? 'Switch to Tamil' : 'English-க்கு மாற்று'}
              >
                <Languages className="w-4 h-4" />
              </Button>

              {/* Settings */}
              <Link to="/settings" title={language === 'en' ? 'Settings' : 'அமைப்புகள்'}>
                <Button variant="outline" size="sm">
                  <Settings className="w-4 h-4" />
                </Button>
              </Link>

              {/* Logout */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  // In a real app, this would clear session/tokens
                  // For now, redirect to home page
                  window.location.href = '/';
                }}
                title={language === 'en' ? 'Logout' : 'வெளியேறு'}
              >
                <LogOut className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 py-6">
          {/* Dashboard Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Loan Chat Card */}
            <div
              className="bg-card rounded-xl border border-border p-6 cursor-pointer hover:shadow-lg transition-all duration-200 group"
              onClick={() => toggleCard('chat')}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                    <MessageSquare className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors">
                      {language === 'en' ? 'Loan Chat' : 'கடன் அரட்டை'}
                    </h3>
                    <p className="text-xs text-muted-foreground">
                      {language === 'en' ? 'AI Assistant' : 'AI உதவியாளர்'}
                    </p>
                  </div>
                </div>
                {expandedCard === 'chat' ? (
                  <ChevronDown className="w-5 h-5 text-muted-foreground" />
                ) : (
                  <ChevronRight className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
                )}
              </div>

              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">4 active conversations</p>
                <p className="text-xs text-muted-foreground">Last message: 2 mins ago</p>
              </div>

              {expandedCard === 'chat' && (
                <div className="mt-4 pt-4 border-t border-border animate-in slide-in-from-top-2 duration-200">
                  <div className="space-y-3 max-h-64 overflow-y-auto">
                    {recentChatMessages.slice(0, 2).map((msg) => (
                      <div key={msg.id} className="flex gap-2">
                        <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                          {msg.sender === 'bot' ? '🤖' : '👤'}
                        </div>
                        <div className="flex-1">
                          <p className="text-xs text-muted-foreground mb-1">
                            {msg.sender === 'bot' ? 'AI Assistant' : 'You'} · {msg.time}
                          </p>
                          <p className="text-sm">{msg.content}</p>
                        </div>
                      </div>
                    ))}
                    <div className="pt-2">
                      <Link to="/chat">
                        <Button size="sm" className="w-full gap-2">
                          <MessageSquare className="w-3 h-3" />
                          {language === 'en' ? 'Continue Chat' : 'அரட்டையை தொடரவும்'}
                        </Button>
                      </Link>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Progress Tracker Card */}
            <div
              className="bg-card rounded-xl border border-border p-6 cursor-pointer hover:shadow-lg transition-all duration-200 group"
              onClick={() => toggleCard('progress')}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                    <Clock className="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors">
                      {language === 'en' ? 'Progress Tracker' : 'முன்னேற்ற கண்காணி'}
                    </h3>
                    <p className="text-xs text-muted-foreground">
                      {language === 'en' ? 'Application Status' : 'விண்ணப்ப நிலை'}
                    </p>
                  </div>
                </div>
                {expandedCard === 'progress' ? (
                  <ChevronDown className="w-5 h-5 text-muted-foreground" />
                ) : (
                  <ChevronRight className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
                )}
              </div>

              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">
                  {progressSteps.filter(s => s.completed).length} of {progressSteps.length} steps completed
                </p>
                <div className="w-full bg-muted rounded-full h-2">
                  <div
                    className="bg-green-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${(progressSteps.filter(s => s.completed).length / progressSteps.length) * 100}%` }}
                  />
                </div>
              </div>

              {expandedCard === 'progress' && (
                <div className="mt-4 pt-4 border-t border-border animate-in slide-in-from-top-2 duration-200">
                  <div className="space-y-3">
                    {progressSteps.map((step) => (
                      <div key={step.id} className="flex items-center gap-3">
                        <div className={cn(
                          "w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium",
                          step.status === 'completed' && "bg-green-500 text-white",
                          step.status === 'in-progress' && "bg-blue-500 text-white",
                          step.status === 'pending' && "bg-gray-300 text-gray-600"
                        )}>
                          {step.status === 'completed' ? '✓' : step.id}
                        </div>
                        <span className={cn(
                          "text-sm",
                          step.status === 'completed' && "text-green-700",
                          step.status === 'in-progress' && "text-blue-700",
                          step.status === 'pending' && "text-muted-foreground"
                        )}>
                          {step.name}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Current Loan Card */}
            <div
              className="bg-card rounded-xl border border-border p-6 cursor-pointer hover:shadow-lg transition-all duration-200 group"
              onClick={() => toggleCard('loan')}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center">
                    <CreditCard className="w-5 h-5 text-purple-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors">
                      {language === 'en' ? 'Current Loan' : 'தற்போதைய கடன்'}
                    </h3>
                    <p className="text-xs text-muted-foreground">
                      {language === 'en' ? 'Loan Details' : 'கடன் விவரங்கள்'}
                    </p>
                  </div>
                </div>
                {expandedCard === 'loan' ? (
                  <ChevronDown className="w-5 h-5 text-muted-foreground" />
                ) : (
                  <ChevronRight className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
                )}
              </div>

              <div className="space-y-2">
                <p className="text-2xl font-bold text-primary">{currentLoan.amount}</p>
                <p className="text-xs text-muted-foreground">
                  EMI: {currentLoan.emi} | Tenure: {currentLoan.tenure}M
                </p>
              </div>

              {expandedCard === 'loan' && (
                <div className="mt-4 pt-4 border-t border-border animate-in slide-in-from-top-2 duration-200">
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="text-center p-3 bg-primary/5 rounded-lg">
                      <p className="text-xs text-muted-foreground">Amount</p>
                      <p className="font-semibold text-primary">{currentLoan.amount}</p>
                    </div>
                    <div className="text-center p-3 bg-green-50 rounded-lg">
                      <p className="text-xs text-muted-foreground">Rate</p>
                      <p className="font-semibold text-green-700">{currentLoan.interestRate}%</p>
                    </div>
                    <div className="text-center p-3 bg-blue-50 rounded-lg">
                      <p className="text-xs text-muted-foreground">EMI</p>
                      <p className="font-semibold text-blue-700">{currentLoan.emi}</p>
                    </div>
                    <div className="text-center p-3 bg-purple-50 rounded-lg">
                      <p className="text-xs text-muted-foreground">Status</p>
                      <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        <CheckCircle2 className="w-3 h-3" />
                        Approved
                      </span>
                    </div>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Ref: {currentLoan.referenceId}
                  </div>
                </div>
              )}
            </div>

            {/* Salary Upload Card */}
            {showSalaryUpload && (
              <div
                className="bg-card rounded-xl border border-border p-6 cursor-pointer hover:shadow-lg transition-all duration-200 group"
                onClick={() => toggleCard('upload')}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center">
                      <Upload className="w-5 h-5 text-orange-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors">
                        {language === 'en' ? 'Document Upload' : 'ஆவண பதிவேற்றம்'}
                      </h3>
                      <p className="text-xs text-muted-foreground">
                        {language === 'en' ? 'Verification Required' : 'சரிபார்ப்பு தேவை'}
                      </p>
                    </div>
                  </div>
                  {expandedCard === 'upload' ? (
                    <ChevronDown className="w-5 h-5 text-muted-foreground" />
                  ) : (
                    <ChevronRight className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
                  )}
                </div>

                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">Salary slip verification</p>
                  <p className="text-xs text-orange-600">Pending review</p>
                </div>

                {expandedCard === 'upload' && (
                  <div className="mt-4 pt-4 border-t border-border animate-in slide-in-from-top-2 duration-200">
                    <div className="text-center">
                      <Upload className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                      <h4 className="font-medium mb-1">
                        {language === 'en' ? 'Upload Salary Slip' : 'சம்பள சீட்டை பதிவேற்றவும்'}
                      </h4>
                      <p className="text-sm text-muted-foreground mb-3">
                        {language === 'en'
                          ? 'PDF format required for verification'
                          : 'சரிபார்ப்புக்கு PDF வடிவம் தேவை'
                        }
                      </p>
                      <Button variant="outline" size="sm" className="gap-2">
                        <Upload className="w-3 h-3" />
                        {language === 'en' ? 'Choose File' : 'கோப்பை தேர்ந்தெடு'}
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Sanction Letter Card */}
            <div
              className="bg-card rounded-xl border border-border p-6 cursor-pointer hover:shadow-lg transition-all duration-200 group"
              onClick={() => toggleCard('sanction')}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                    <FileCheck className="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors">
                      {language === 'en' ? 'Sanction Letter' : 'அங்கீகார கடிதம்'}
                    </h3>
                    <p className="text-xs text-muted-foreground">
                      {language === 'en' ? 'Official Document' : 'அதிகாரப்பூர்வ ஆவணம்'}
                    </p>
                  </div>
                </div>
                {expandedCard === 'sanction' ? (
                  <ChevronDown className="w-5 h-5 text-muted-foreground" />
                ) : (
                  <ChevronRight className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
                )}
              </div>

              <div className="space-y-2">
                <p className="text-sm text-green-700">Loan approved</p>
                <p className="text-xs text-muted-foreground">Download available</p>
              </div>

              {expandedCard === 'sanction' && (
                <div className="mt-4 pt-4 border-t border-border animate-in slide-in-from-top-2 duration-200">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <p className="font-medium text-green-800">Approval confirmed</p>
                      <p className="text-sm text-green-600">December 6, 2024</p>
                    </div>
                    <Button size="sm" className="gap-2 bg-green-600 hover:bg-green-700">
                      <Download className="w-3 h-3" />
                      Download PDF
                    </Button>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Reference: LN20241207001
                  </div>
                </div>
              )}
            </div>

            {/* Loan History Card */}
            <div
              className="bg-card rounded-xl border border-border p-6 cursor-pointer hover:shadow-lg transition-all duration-200 group"
              onClick={() => toggleCard('history')}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                    <History className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors">
                      {language === 'en' ? 'Loan History' : 'கடன் வரலாறு'}
                    </h3>
                    <p className="text-xs text-muted-foreground">
                      {language === 'en' ? 'Past Applications' : 'கடந்த விண்ணப்பங்கள்'}
                    </p>
                  </div>
                </div>
                {expandedCard === 'history' ? (
                  <ChevronDown className="w-5 h-5 text-muted-foreground" />
                ) : (
                  <ChevronRight className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
                )}
              </div>

              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">
                  {loanHistory.filter(l => l.status === 'approved').length} approved loans
                </p>
                <p className="text-xs text-muted-foreground">
                  Last application: 2 days ago
                </p>
              </div>

              {expandedCard === 'history' && (
                <div className="mt-4 pt-4 border-t border-border animate-in slide-in-from-top-2 duration-200">
                  <div className="space-y-3 max-h-48 overflow-y-auto">
                    {loanHistory.map((loan, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <Calendar className="w-4 h-4 text-muted-foreground" />
                          <div>
                            <p className="text-sm font-medium">{loan.date}</p>
                            <p className="text-xs text-muted-foreground">{loan.amount}</p>
                          </div>
                        </div>
                        <span className={cn(
                          "inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs",
                          loan.status === 'approved' ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                        )}>
                          {loan.status === 'approved' ? 'Approved' : 'Rejected'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Analytics Card */}
            <div
              className="bg-card rounded-xl border border-border p-6 cursor-pointer hover:shadow-lg transition-all duration-200 group"
              onClick={() => toggleCard('analytics')}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center">
                    <BarChart3 className="w-5 h-5 text-indigo-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors">
                      {language === 'en' ? 'Analytics' : 'பகுப்பாய்வு'}
                    </h3>
                    <p className="text-xs text-muted-foreground">
                      {language === 'en' ? 'Performance Metrics' : 'செயல்திறன் அளவீடுகள்'}
                    </p>
                  </div>
                </div>
                {expandedCard === 'analytics' ? (
                  <ChevronDown className="w-5 h-5 text-muted-foreground" />
                ) : (
                  <ChevronRight className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
                )}
              </div>

              <div className="space-y-2">
                <p className="text-sm text-muted-foreground">Approval rate: 78%</p>
                <p className="text-xs text-green-600">+5% from last month</p>
              </div>

              {expandedCard === 'analytics' && (
                <div className="mt-4 pt-4 border-t border-border animate-in slide-in-from-top-2 duration-200">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center p-3 bg-green-50 rounded-lg">
                      <p className="text-2xl font-bold text-green-700">78%</p>
                      <p className="text-xs text-green-600">Approval Rate</p>
                    </div>
                    <div className="text-center p-3 bg-blue-50 rounded-lg">
                      <p className="text-2xl font-bold text-blue-700">1.2min</p>
                      <p className="text-xs text-blue-600">Avg Response</p>
                    </div>
                    <div className="text-center p-3 bg-purple-50 rounded-lg">
                      <p className="text-2xl font-bold text-purple-700">₹25L</p>
                      <p className="text-xs text-purple-600">Avg Amount</p>
                    </div>
                    <div className="text-center p-3 bg-orange-50 rounded-lg">
                      <p className="text-2xl font-bold text-orange-700">45</p>
                      <p className="text-xs text-orange-600">Daily Apps</p>
                    </div>
                  </div>
                </div>
              )}
            </div>


          </div>
        </main>
      </div>
    </>
  );
};

export default Dashboard;
