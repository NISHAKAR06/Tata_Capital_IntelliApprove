import { Loader2, CheckCircle2, AlertCircle, FileText, Shield, Calculator } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StatusMessageProps {
  step: 'analyzing' | 'verifying' | 'underwriting' | 'complete';
  language: 'en' | 'ta';
}

const steps = {
  analyzing: {
    en: 'Analyzing your requirement...',
    ta: 'உங்கள் தேவையை பகுப்பாய்வு செய்கிறது...',
    icon: Calculator,
  },
  verifying: {
    en: 'Verifying KYC details...',
    ta: 'KYC விவரங்களை சரிபார்க்கிறது...',
    icon: Shield,
  },
  underwriting: {
    en: 'Running underwriting checks...',
    ta: 'அண்டர்ரைட்டிங் சோதனைகளை நடத்துகிறது...',
    icon: FileText,
  },
  complete: {
    en: 'Analysis complete',
    ta: 'பகுப்பாய்வு முடிந்தது',
    icon: CheckCircle2,
  },
};

const StatusMessage = ({ step, language }: StatusMessageProps) => {
  const currentStep = steps[step];
  const Icon = currentStep.icon;
  const isComplete = step === 'complete';

  return (
    <div className="flex items-center justify-center py-3 animate-fade-in-up">
      <div
        className={cn(
          'inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium',
          isComplete
            ? 'bg-success/10 text-success'
            : 'bg-primary/10 text-primary'
        )}
      >
        {isComplete ? (
          <CheckCircle2 className="w-4 h-4" />
        ) : (
          <Loader2 className="w-4 h-4 animate-spin" />
        )}
        <span className={language === 'ta' ? 'font-tamil' : ''}>
          {currentStep[language]}
        </span>
      </div>
    </div>
  );
};

export default StatusMessage;
