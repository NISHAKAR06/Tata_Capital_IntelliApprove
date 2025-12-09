import { X, TrendingUp, CreditCard, Percent, CheckCircle2, Info } from 'lucide-react';
import { cn } from '@/lib/utils';

interface XAIData {
  emiPercentage?: number;
  creditScore?: number;
  interestRate?: number;
  reasoning?: string[];
}

interface XAIPanelProps {
  data: XAIData | null;
  language: 'en' | 'ta';
  onClose?: () => void;
  isDrawer?: boolean;
}

const XAIPanel = ({ data, language, onClose, isDrawer }: XAIPanelProps) => {
  if (!data) {
    return (
      <div className={cn(
        'flex flex-col items-center justify-center text-center p-8',
        isDrawer ? 'h-auto' : 'h-full'
      )}>
        <Info className="w-12 h-12 text-muted-foreground/40 mb-4" />
        <h3 className={cn('font-medium text-muted-foreground mb-2', language === 'ta' && 'font-tamil')}>
          {language === 'en' ? 'No Analysis Available' : 'பகுப்பாய்வு இல்லை'}
        </h3>
        <p className={cn('text-sm text-muted-foreground/70', language === 'ta' && 'font-tamil')}>
          {language === 'en' 
            ? 'Start a conversation to see loan analysis'
            : 'கடன் பகுப்பாய்வைக் காண உரையாடலைத் தொடங்கவும்'}
        </p>
      </div>
    );
  }

  return (
    <div className={cn('flex flex-col', isDrawer ? 'p-4' : 'h-full')}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className={cn('font-semibold text-lg text-foreground', language === 'ta' && 'font-tamil')}>
          {language === 'en' ? 'Decision Explanation' : 'முடிவு விளக்கம்'}
        </h2>
        {onClose && (
          <button onClick={onClose} className="p-1.5 hover:bg-muted rounded-full transition-colors lg:hidden">
            <X className="w-5 h-5 text-muted-foreground" />
          </button>
        )}
      </div>

      <div className="space-y-4 flex-1 overflow-y-auto">
        {/* EMI Percentage */}
        {data.emiPercentage !== undefined && (
          <div className="bg-secondary/50 rounded-xl p-4 border border-border">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                <Percent className="w-5 h-5 text-primary" />
              </div>
              <div>
                <p className={cn('text-xs text-muted-foreground', language === 'ta' && 'font-tamil')}>
                  {language === 'en' ? 'EMI to Salary Ratio' : 'EMI சம்பள விகிதம்'}
                </p>
                <p className="text-2xl font-bold text-foreground">{data.emiPercentage}%</p>
              </div>
            </div>
            <div className="w-full h-3 bg-muted rounded-full overflow-hidden">
              <div 
                className={cn(
                  'h-full rounded-full transition-all duration-1000',
                  data.emiPercentage <= 40 ? 'bg-success' : 
                  data.emiPercentage <= 50 ? 'bg-warning' : 'bg-destructive'
                )}
                style={{ width: `${Math.min(data.emiPercentage, 100)}%` }}
              />
            </div>
            <p className={cn('text-xs text-muted-foreground mt-2', language === 'ta' && 'font-tamil')}>
              {language === 'en' 
                ? data.emiPercentage <= 50 ? 'Within acceptable range' : 'Above recommended limit'
                : data.emiPercentage <= 50 ? 'ஏற்றுக்கொள்ளக்கூடிய வரம்பில்' : 'பரிந்துரைக்கப்பட்ட வரம்புக்கு மேல்'}
            </p>
          </div>
        )}

        {/* Credit Score */}
        {data.creditScore !== undefined && (
          <div className="bg-secondary/50 rounded-xl p-4 border border-border">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-full bg-success/10 flex items-center justify-center">
                <CreditCard className="w-5 h-5 text-success" />
              </div>
              <div>
                <p className={cn('text-xs text-muted-foreground', language === 'ta' && 'font-tamil')}>
                  {language === 'en' ? 'Credit Score' : 'கடன் மதிப்பெண்'}
                </p>
                <p className="text-2xl font-bold text-foreground">{data.creditScore}</p>
              </div>
            </div>
            <div className="flex gap-1">
              {[300, 500, 650, 750, 850].map((threshold, i) => (
                <div
                  key={threshold}
                  className={cn(
                    'flex-1 h-2 rounded-full',
                    data.creditScore >= threshold 
                      ? i < 2 ? 'bg-destructive' : i < 3 ? 'bg-warning' : 'bg-success'
                      : 'bg-muted'
                  )}
                />
              ))}
            </div>
            <p className={cn('text-xs text-muted-foreground mt-2', language === 'ta' && 'font-tamil')}>
              {language === 'en' 
                ? data.creditScore >= 750 ? 'Excellent' : data.creditScore >= 650 ? 'Good' : 'Fair'
                : data.creditScore >= 750 ? 'சிறப்பு' : data.creditScore >= 650 ? 'நல்ல' : 'நியாயமான'}
            </p>
          </div>
        )}

        {/* Interest Rate */}
        {data.interestRate !== undefined && (
          <div className="bg-secondary/50 rounded-xl p-4 border border-border">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-primary" />
              </div>
              <div>
                <p className={cn('text-xs text-muted-foreground', language === 'ta' && 'font-tamil')}>
                  {language === 'en' ? 'Interest Rate' : 'வட்டி விகிதம்'}
                </p>
                <p className="text-2xl font-bold text-foreground">{data.interestRate}% <span className="text-sm font-normal text-muted-foreground">p.a.</span></p>
              </div>
            </div>
          </div>
        )}

        {/* Reasoning */}
        {data.reasoning && data.reasoning.length > 0 && (
          <div className="bg-secondary/50 rounded-xl p-4 border border-border">
            <h4 className={cn('font-medium text-foreground mb-3', language === 'ta' && 'font-tamil')}>
              {language === 'en' ? 'Decision Factors' : 'முடிவு காரணிகள்'}
            </h4>
            <ul className="space-y-2">
              {data.reasoning.map((reason, index) => (
                <li key={index} className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-success mt-0.5 flex-shrink-0" />
                  <span className={cn('text-sm text-foreground', language === 'ta' && 'font-tamil')}>
                    {reason}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default XAIPanel;
