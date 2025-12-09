import { Check, CheckCheck } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface Message {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  status?: 'approved' | 'rejected' | 'pending_documents' | 'processing';
  sentiment?: 'neutral' | 'hesitation' | 'confusion' | 'negative';
  agentStep?: string;
}

interface MessageBubbleProps {
  message: Message;
  language: 'en' | 'ta';
}

const MessageBubble = ({ message, language }: MessageBubbleProps) => {
  const isUser = message.sender === 'user';
  const isEmpathy = message.sentiment && message.sentiment !== 'neutral';
  
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString(language === 'ta' ? 'ta-IN' : 'en-IN', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div
      className={cn(
        'flex gap-3 animate-fade-in-up',
        isUser ? 'flex-row-reverse' : 'flex-row'
      )}
    >
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
          <span className="text-primary-foreground text-xs font-semibold">AI</span>
        </div>
      )}
      
      <div className={cn('flex flex-col gap-1 max-w-[80%] md:max-w-[70%]', isUser && 'items-end')}>
        {message.agentStep && !isUser && (
          <span className="text-xs text-muted-foreground px-1">
            {message.agentStep}
          </span>
        )}
        
        <div
          className={cn(
            language === 'ta' && 'font-tamil',
            isUser ? 'chat-bubble-user' : isEmpathy ? 'chat-bubble-empathy' : 'chat-bubble-bot'
          )}
        >
          <p className="text-sm md:text-base leading-relaxed whitespace-pre-wrap">
            {message.content}
          </p>
        </div>
        
        <div className={cn('flex items-center gap-1.5 px-1', isUser && 'flex-row-reverse')}>
          <span className="text-xs text-muted-foreground">
            {formatTime(message.timestamp)}
          </span>
          {isUser && (
            <CheckCheck className="w-3.5 h-3.5 text-primary" />
          )}
        </div>
        
        {message.status && (
          <div className="mt-1">
            {message.status === 'approved' && (
              <span className="status-badge status-approved">
                <Check className="w-3.5 h-3.5" />
                {language === 'en' ? 'Approved' : 'அனுமதிக்கப்பட்டது'}
              </span>
            )}
            {message.status === 'pending_documents' && (
              <span className="status-badge status-pending">
                ⚠ {language === 'en' ? 'Salary Slip Required' : 'சம்பள சீட்டு தேவை'}
              </span>
            )}
            {message.status === 'rejected' && (
              <span className="status-badge status-rejected">
                ❌ {language === 'en' ? 'Rejected' : 'நிராகரிக்கப்பட்டது'}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
