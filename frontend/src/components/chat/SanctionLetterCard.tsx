import { Download, FileText, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { downloadSanctionLetter } from '@/lib/api';

interface SanctionLetterCardProps {
  sanctionRef: string;
  language: 'en' | 'ta';
}

const SanctionLetterCard = ({ sanctionRef, language }: SanctionLetterCardProps) => {
  const handleDownload = () => {
    downloadSanctionLetter(sanctionRef);
  };

  return (
    <div className="bg-gradient-to-br from-success/10 to-success/5 rounded-xl border border-success/30 p-4 shadow-md animate-fade-in-up">
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-full bg-success/20 flex items-center justify-center flex-shrink-0">
          <CheckCircle2 className="w-6 h-6 text-success" />
        </div>
        
        <div className="flex-1 min-w-0">
          <h3 className={cn('font-semibold text-foreground mb-1', language === 'ta' && 'font-tamil')}>
            {language === 'en' ? 'Loan Approved!' : 'கடன் அனுமதிக்கப்பட்டது!'}
          </h3>
          <p className={cn('text-sm text-muted-foreground mb-3', language === 'ta' && 'font-tamil')}>
            {language === 'en' 
              ? 'Your sanction letter is ready for download.'
              : 'உங்கள் அனுமதி கடிதம் பதிவிறக்கத்திற்கு தயாராக உள்ளது.'}
          </p>
          
          <div className="flex items-center gap-2 text-xs text-muted-foreground mb-3">
            <FileText className="w-4 h-4" />
            <span>
              {language === 'en' ? 'Reference:' : 'குறிப்பு:'} {sanctionRef}
            </span>
          </div>
          
          <button
            onClick={handleDownload}
            className={cn(
              'inline-flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium text-sm',
              'bg-success text-success-foreground hover:bg-success/90 transition-all',
              'active:scale-[0.98]',
              language === 'ta' && 'font-tamil'
            )}
          >
            <Download className="w-4 h-4" />
            {language === 'en' ? 'Download Sanction Letter' : 'அனுமதி கடிதத்தை பதிவிறக்கவும்'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default SanctionLetterCard;
