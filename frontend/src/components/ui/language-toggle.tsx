import { Languages } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useTranslation } from "@/contexts/LanguageContext";

export const LanguageToggle = () => {
  const { language, setLanguage, t } = useTranslation();

  return (
    <div className="fixed bottom-4 left-4 z-50 flex items-center gap-2 bg-background/80 backdrop-blur-sm border border-border/50 rounded-full px-3 py-2 shadow-lg hover:shadow-xl transition-all duration-300">
      <Languages className="w-4 h-4 text-muted-foreground" />
      <Select value={language} onValueChange={setLanguage}>
        <SelectTrigger className="w-24 h-8 bg-transparent border-0 focus:ring-0 focus:ring-offset-0">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="en">English</SelectItem>
          <SelectItem value="hi">हिंदी</SelectItem>
          <SelectItem value="ta">தமிழ்</SelectItem>
          <SelectItem value="ml">മലയാളം</SelectItem>
          <SelectItem value="te">తెలుగు</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
};
