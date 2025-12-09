import { useState, useRef, useEffect } from 'react';
import { Send, Mic } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  language: 'en' | 'ta';
}

const ChatInput = ({ onSend, disabled, language }: ChatInputProps) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleInput = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + 'px';
    }
  };

  useEffect(() => {
    handleInput();
  }, [message]);

  return (
    <div className="border-t border-border bg-card/95 backdrop-blur-sm p-3 md:p-4 safe-bottom">
      <div className="flex items-end gap-2 max-w-4xl mx-auto">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            placeholder={language === 'en' ? 'Type your message...' : 'உங்கள் செய்தியை தட்டச்சு செய்யவும்...'}
            rows={1}
            className={cn(
              'w-full resize-none rounded-2xl border border-border bg-background px-4 py-3 pr-12',
              'focus:outline-none focus:ring-2 focus:ring-ring/50 focus:border-primary',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              'text-sm md:text-base transition-all',
              language === 'ta' && 'font-tamil'
            )}
          />
        </div>
        
        <button
          onClick={handleSubmit}
          disabled={!message.trim() || disabled}
          className={cn(
            'flex-shrink-0 w-11 h-11 md:w-12 md:h-12 rounded-full',
            'flex items-center justify-center transition-all',
            'bg-primary text-primary-foreground',
            'hover:bg-primary/90 active:scale-95',
            'disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100',
            'shadow-md hover:shadow-lg'
          )}
          aria-label="Send message"
        >
          <Send className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

export default ChatInput;
