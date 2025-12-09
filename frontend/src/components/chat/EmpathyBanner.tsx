import { Heart } from 'lucide-react';
import { cn } from '@/lib/utils';

interface EmpathyBannerProps {
  sentiment: 'hesitation' | 'confusion' | 'negative';
  language: 'en' | 'ta';
}

const messages = {
  hesitation: {
    en: "I understand you might have some doubts. Let me address any concerns you have.",
    ta: "உங்களுக்கு சில சந்தேகங்கள் இருக்கலாம் என்று புரிகிறது. உங்கள் கவலைகளை தீர்க்க உதவுகிறேன்."
  },
  confusion: {
    en: "Don't worry, I'll help you find the best possible option. Let me simplify things.",
    ta: "கவலைப்படாதீர்கள், சிறந்த வாய்ப்பைக் கண்டுபிடிக்க உதவுவேன். விஷயங்களை எளிமையாக்குகிறேன்."
  },
  negative: {
    en: "I'm here to help you every step of the way. Let's find the right solution together.",
    ta: "ஒவ்வொரு அடியிலும் உங்களுக்கு உதவ நான் இங்கே இருக்கிறேன். சரியான தீர்வைக் கண்டுபிடிப்போம்."
  }
};

const EmpathyBanner = ({ sentiment, language }: EmpathyBannerProps) => {
  return (
    <div className="mx-4 my-2 animate-fade-in-up">
      <div className="bg-chat-empathy rounded-xl p-4 border border-purple-200 dark:border-purple-800/30">
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center flex-shrink-0">
            <Heart className="w-4 h-4 text-purple-600 dark:text-purple-400" />
          </div>
          <p className={cn(
            'text-sm text-purple-900 dark:text-purple-100 leading-relaxed',
            language === 'ta' && 'font-tamil'
          )}>
            {messages[sentiment][language]}
          </p>
        </div>
      </div>
    </div>
  );
};

export default EmpathyBanner;
