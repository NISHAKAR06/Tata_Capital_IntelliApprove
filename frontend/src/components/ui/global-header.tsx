import { useLocation } from "react-router-dom";
import { Languages, Moon, Sun } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { useTranslation } from "@/contexts/LanguageContext";
import { useTheme } from "@/contexts/ThemeContext";

export const GlobalHeader = () => {
  const location = useLocation();
  const { language, setLanguage } = useTranslation();
  const { theme, toggleTheme } = useTheme();

  // Don't show on home page (hero page) as it has the navbar controls
  if (location.pathname === '/') {
    return null;
  }

  return (
    <header className="fixed top-4 right-4 z-[100]">
      <div className="flex items-center gap-2 p-3 bg-card/95 backdrop-blur-xl border border-border/50 rounded-full shadow-xl hover:shadow-2xl transition-all duration-300">
        <Select value={language} onValueChange={setLanguage}>
          <SelectTrigger className="w-20 h-8 bg-transparent border-0 focus:ring-0 focus:ring-offset-0 text-sm">
            <div className="flex items-center gap-1">
              <Languages className="w-4 h-4" />
              <SelectValue />
            </div>
          </SelectTrigger>
          <SelectContent className="z-[60]">
            <SelectItem value="en">EN</SelectItem>
            <SelectItem value="hi">हिंदी</SelectItem>
            <SelectItem value="ta">தமிழ்</SelectItem>
            <SelectItem value="ml">മലയാളം</SelectItem>
            <SelectItem value="te">తెలుగు</SelectItem>
          </SelectContent>
        </Select>

        <div className="w-px h-4 bg-border" />

        <Button
          variant="ghost"
          size="icon"
          onClick={toggleTheme}
          className="w-8 h-8 hover:bg-accent rounded-full"
          title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
        >
          {theme === 'light' ? (
            <Moon className="w-4 h-4" />
          ) : (
            <Sun className="w-4 h-4" />
          )}
        </Button>
      </div>
    </header>
  );
};
