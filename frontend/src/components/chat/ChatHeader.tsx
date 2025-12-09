import { Bot, ChevronLeft, Info, Moon, Sun } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ChatHeaderProps {
  language: 'en' | 'ta';
  onToggleLanguage: () => void;
  onToggleXAI?: () => void;
  showXAIToggle?: boolean;
  darkMode: boolean;
  onToggleDarkMode: () => void;
}

const ChatHeader = ({
  language,
  onToggleLanguage,
  onToggleXAI,
  showXAIToggle,
  darkMode,
  onToggleDarkMode,
}: ChatHeaderProps) => {
  return (
    <header className="sticky top-0 z-20 border-b border-border bg-card/95 backdrop-blur-sm">
      <div className="flex items-center justify-between px-4 py-3 md:px-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-primary-glow flex items-center justify-center shadow-glow">
            <Bot className="w-5 h-5 text-primary-foreground" />
          </div>
          <div>
            <h1 className={cn('font-semibold text-foreground', language === 'ta' && 'font-tamil')}>
              {language === 'en' ? 'Loan Assistant' : 'கடன் உதவியாளர்'}
            </h1>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-success animate-pulse" />
              <span className={cn('text-xs text-muted-foreground', language === 'ta' && 'font-tamil')}>
                {language === 'en' ? 'Online' : 'ஆன்லைன்'}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Language Toggle */}
          <button
            onClick={onToggleLanguage}
            className={cn(
              'px-3 py-1.5 rounded-full text-xs font-medium transition-all',
              'bg-secondary text-secondary-foreground hover:bg-secondary/80',
              'border border-border'
            )}
          >
            {language === 'en' ? 'தமிழ்' : 'EN'}
          </button>

          {/* Dark Mode Toggle */}
          <button
            onClick={onToggleDarkMode}
            className="p-2 rounded-full hover:bg-muted transition-colors"
            aria-label="Toggle dark mode"
          >
            {darkMode ? (
              <Sun className="w-5 h-5 text-muted-foreground" />
            ) : (
              <Moon className="w-5 h-5 text-muted-foreground" />
            )}
          </button>

          {/* XAI Panel Toggle (Mobile/Tablet) */}
          {showXAIToggle && (
            <button
              onClick={onToggleXAI}
              className="p-2 rounded-full hover:bg-muted transition-colors lg:hidden"
              aria-label="Show explainability"
            >
              <Info className="w-5 h-5 text-muted-foreground" />
            </button>
          )}
        </div>
      </div>
    </header>
  );
};

export default ChatHeader;
