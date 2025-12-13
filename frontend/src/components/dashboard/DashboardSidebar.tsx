import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  MessageSquare,
  BarChart3,
  CreditCard,
  Upload,
  FileText,
  History,
  PieChart,
  ChevronLeft,
  ChevronRight,
  LogOut,
  User,
} from "lucide-react";
import { Button } from "@/components/ui/button";

const menuItems = [
  { icon: MessageSquare, label: "Loan Chat", path: "/dashboard/chat" },
  { icon: BarChart3, label: "Progress Tracker", path: "/dashboard/progress" },
  { icon: CreditCard, label: "Current Loan Status", path: "/dashboard/status" },
  { icon: Upload, label: "Document Upload", path: "/dashboard/documents" },
  { icon: FileText, label: "Sanction Letter", path: "/dashboard/sanction" },
  { icon: History, label: "Loan History", path: "/dashboard/history" },
  { icon: PieChart, label: "Analytics", path: "/dashboard/analytics" },
];

interface DashboardSidebarProps {
  isCollapsed: boolean;
  setIsCollapsed: (value: boolean) => void;
}

export const DashboardSidebar = ({ isCollapsed, setIsCollapsed }: DashboardSidebarProps) => {
  const location = useLocation();
  const [activeIndex, setActiveIndex] = useState(0);

  const currentIndex = menuItems.findIndex((item) => location.pathname === item.path);
  const activeIdx = currentIndex !== -1 ? currentIndex : activeIndex;

  return (
    <motion.aside
      initial={false}
      animate={{ width: isCollapsed ? 80 : 280 }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
      className="fixed left-0 top-0 h-screen bg-sidebar border-r border-sidebar-border z-40 flex flex-col"
    >
      {/* Header */}
      <div className="h-20 flex items-center justify-between px-4 border-b border-sidebar-border">
        <AnimatePresence mode="wait">
          {!isCollapsed && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center gap-3"
            >
              <div className="w-10 h-10 rounded-lg gradient-bg flex items-center justify-center">
                <span className="text-primary-foreground font-bold text-lg font-poppins">IA</span>
              </div>
              <div>
                <span className="font-poppins font-bold text-foreground">Intelli</span>
                <span className="font-poppins font-bold text-primary">Approve</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <Button
          variant="ghost"
          size="icon"
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="flex-shrink-0"
        >
          {isCollapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
        </Button>
      </div>

      {/* Stepper Navigation */}
      <nav className="flex-1 py-6 px-3 overflow-y-auto">
        <div className="relative">
          {/* Progress Line */}
          <div className="absolute left-[19px] top-0 bottom-0 w-0.5 bg-border">
            <motion.div
              className="w-full bg-primary"
              initial={{ height: 0 }}
              animate={{ height: `${((activeIdx + 1) / menuItems.length) * 100}%` }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            />
          </div>

          {/* Menu Items */}
          <ul className="space-y-2 relative">
            {menuItems.map((item, index) => {
              const isActive = location.pathname === item.path;
              const isPast = index < activeIdx;
              const Icon = item.icon;

              return (
                <li key={item.path}>
                  <Link
                    to={item.path}
                    onClick={() => setActiveIndex(index)}
                    className={`stepper-item ${isActive ? "active" : ""}`}
                  >
                    <motion.div
                      className={`relative z-10 w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 transition-all duration-300 ${
                        isActive
                          ? "bg-primary text-primary-foreground shadow-lg shadow-primary/30"
                          : isPast
                          ? "bg-primary/20 text-primary"
                          : "bg-secondary text-muted-foreground"
                      }`}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <Icon className="w-5 h-5" />
                    </motion.div>

                    <AnimatePresence mode="wait">
                      {!isCollapsed && (
                        <motion.span
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          exit={{ opacity: 0, x: -10 }}
                          className={`font-medium whitespace-nowrap ${
                            isActive ? "text-foreground" : "text-muted-foreground"
                          }`}
                        >
                          {item.label}
                        </motion.span>
                      )}
                    </AnimatePresence>
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>
      </nav>

      {/* User Section */}
      <div className="p-4 border-t border-sidebar-border">
        <div className={`flex items-center ${isCollapsed ? "justify-center" : "gap-3"}`}>
          <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
            <User className="w-5 h-5 text-primary" />
          </div>
          <AnimatePresence mode="wait">
            {!isCollapsed && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex-1 min-w-0"
              >
                <div className="font-medium text-sm truncate">John Doe</div>
                <div className="text-xs text-muted-foreground truncate">john@example.com</div>
              </motion.div>
            )}
          </AnimatePresence>
          {!isCollapsed && (
            <Link to="/">
              <Button variant="ghost" size="icon" className="flex-shrink-0">
                <LogOut className="w-4 h-4" />
              </Button>
            </Link>
          )}
        </div>
      </div>
    </motion.aside>
  );
};
