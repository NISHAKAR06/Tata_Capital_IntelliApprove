import { useState, useEffect, useRef } from 'react';
import { cn } from '@/lib/utils';
import { getSessionId, ChatResponse, callOrchestrator, OrchestratorState, OrchestratorResponse } from '@/lib/api';
import ChatHeader from './chat/ChatHeader';
import ChatInput from './chat/ChatInput';
import MessageBubble, { Message } from './chat/MessageBubble';
import TypingIndicator from './chat/TypingIndicator';
import StatusMessage from './chat/StatusMessage';
import SalarySlipUpload from './chat/SalarySlipUpload';
import SanctionLetterCard from './chat/SanctionLetterCard';
import EmpathyBanner from './chat/EmpathyBanner';
import XAIPanel from './xai/XAIPanel';

interface XAIData {
  emiPercentage?: number;
  creditScore?: number;
  interestRate?: number;
  reasoning?: string[];
}

const LoanChatbot = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [language, setLanguage] = useState<'en' | 'ta'>('en');
  const [darkMode, setDarkMode] = useState(false);
  const [showXAI, setShowXAI] = useState(false);
  const [xaiData, setXaiData] = useState<XAIData | null>(null);
  const [currentStatus, setCurrentStatus] = useState<'analyzing' | 'verifying' | 'underwriting' | 'complete' | null>(null);
  const [showUpload, setShowUpload] = useState(false);
  const [sanctionRef, setSanctionRef] = useState<string | null>(null);
  const [currentSentiment, setCurrentSentiment] = useState<'hesitation' | 'confusion' | 'negative' | null>(null);
  const [orchState, setOrchState] = useState<OrchestratorState>({});
  const [stage, setStage] = useState<string | undefined>(undefined);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const sessionId = useRef(getSessionId());

  // Load saved state
  useEffect(() => {
    const savedMessages = localStorage.getItem('loan_chat_messages');
    const savedLanguage = localStorage.getItem('loan_chat_language');
    const savedDarkMode = localStorage.getItem('loan_chat_dark_mode');
    
    if (savedMessages) {
      try {
        const parsed = JSON.parse(savedMessages);
        setMessages(parsed.map((m: Message) => ({ ...m, timestamp: new Date(m.timestamp) })));
      } catch (e) {
        console.error('Failed to parse saved messages');
      }
    }
    if (savedLanguage) setLanguage(savedLanguage as 'en' | 'ta');
    if (savedDarkMode === 'true') setDarkMode(true);
  }, []);

  // Save messages
  useEffect(() => {
    localStorage.setItem('loan_chat_messages', JSON.stringify(messages));
  }, [messages]);

  // Save preferences
  useEffect(() => {
    localStorage.setItem('loan_chat_language', language);
  }, [language]);

  useEffect(() => {
    localStorage.setItem('loan_chat_dark_mode', String(darkMode));
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping, currentStatus]);

  // Initial greeting
  useEffect(() => {
    if (messages.length === 0) {
      const greeting: Message = {
        id: 'initial',
        content: language === 'en'
          ? "👋 Hello! I'm your AI Loan Assistant. I can help you with personal loans, home loans, and business loans. How can I assist you today?"
          : "👋 வணக்கம்! நான் உங்கள் AI கடன் உதவியாளர். தனிப்பட்ட கடன்கள், வீட்டுக் கடன்கள் மற்றும் வணிகக் கடன்களில் உங்களுக்கு உதவ முடியும். இன்று நான் உங்களுக்கு எப்படி உதவ முடியும்?",
        sender: 'bot',
        timestamp: new Date(),
        agentStep: 'Master Agent - Welcome',
      };
      setMessages([greeting]);
    }
  }, []);

  const simulateProcessingSteps = async () => {
    const steps: Array<'analyzing' | 'verifying' | 'underwriting' | 'complete'> = [
      'analyzing', 'verifying', 'underwriting', 'complete'
    ];
    
    for (const step of steps) {
      setCurrentStatus(step);
      await new Promise(resolve => setTimeout(resolve, 800));
    }
    
    await new Promise(resolve => setTimeout(resolve, 300));
    setCurrentStatus(null);
  };

  const mapOrchestratorToChatResponse = (res: OrchestratorResponse): ChatResponse => {
    // Basic mapping from orchestrator response to existing ChatResponse shape
    const reply = res.message_to_user;

    let status: ChatResponse['status'] | undefined;
    if (res.stage === 'UNDERWRITING') status = 'processing';
    if (res.action === 'end') {
      const decision = res.state_updates?.explainability?.decision;
      if (decision === 'approved') status = 'approved';
      else if (decision === 'rejected') status = 'rejected';
    }

    const requiresSalarySlip = res.action === 'request_upload' || res.action === 'process_salary_slip';

    // Extract simple XAI view if available
    const explain = (res.state_updates?.explainability ?? {}) as any;
    const xaiData = explain
      ? {
          emiPercentage: undefined,
          creditScore: explain.credit_score ?? undefined,
          interestRate: undefined,
          reasoning: Array.isArray(explain.factors)
            ? explain.factors.map((f: any) => `${f.name}: ${f.status} (${f.reason})`)
            : explain.summary
            ? [explain.summary]
            : undefined,
        }
      : undefined;

    return {
      reply,
      status,
      requiresSalarySlip,
      sanctionRef: res.state_updates?.sanction_data?.sanction_number,
      xaiData,
      agentStep: res.worker_called,
    };
  };

  const handleSend = async (text: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      content: text,
      sender: 'user',
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);
    setCurrentSentiment(null);

    // Simulate processing for certain messages
    const shouldShowProcessing = text.toLowerCase().includes('loan') || 
                                  text.toLowerCase().includes('verify') ||
                                  /\d{10}/.test(text);
    
    if (shouldShowProcessing) {
      await simulateProcessingSteps();
    } else {
      await new Promise(resolve => setTimeout(resolve, 1000));
    }

    try {
      // Call backend orchestrator instead of legacy /chat
      const orchResponse = await callOrchestrator({
        user_message: text,
        stage,
        state: orchState,
        // For now, keep customer_profile / loan_request minimal;
        // can be wired to real forms later.
      });

      setIsTyping(false);

      // Merge state updates
      setOrchState(prev => ({ ...prev, ...(orchResponse.state_updates || {}) }));
      setStage(orchResponse.state_updates?.stage ?? orchResponse.stage);

      const response: ChatResponse = mapOrchestratorToChatResponse(orchResponse);

      // Handle sentiment (currently from legacy API only; placeholder)
      if (response.sentiment && response.sentiment !== 'neutral') {
        setCurrentSentiment(response.sentiment as 'hesitation' | 'confusion' | 'negative');
      }

      // Handle XAI data
      if (response.xaiData) {
        setXaiData(response.xaiData);
      }

      // Handle special responses
      if (response.requiresSalarySlip) {
        setShowUpload(true);
      }

      if (response.sanctionRef) {
        setSanctionRef(response.sanctionRef);
      }

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.reply,
        sender: 'bot',
        timestamp: new Date(),
        status: response.status,
        sentiment: response.sentiment,
        agentStep: response.agentStep,
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      setIsTyping(false);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: language === 'en' 
          ? "I apologize, but I'm experiencing technical difficulties. Please try again."
          : "மன்னிக்கவும், தொழில்நுட்ப சிக்கல்கள் உள்ளன. மீண்டும் முயற்சிக்கவும்.",
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleUploadComplete = (success: boolean) => {
    setShowUpload(false);
    if (success) {
      (async () => {
        setIsTyping(true);
        try {
          const orchResponse = await callOrchestrator({
            stage: 'UNDERWRITING',
            state: orchState,
            event: 'document_uploaded',
            uploaded_document_type: 'salary_slip',
          });

          setIsTyping(false);
          setOrchState(prev => ({ ...prev, ...(orchResponse.state_updates || {}) }));
          setStage(orchResponse.state_updates?.stage ?? orchResponse.stage);

          const response: ChatResponse = mapOrchestratorToChatResponse(orchResponse);
          if (response.xaiData) setXaiData(response.xaiData);
          if (response.sanctionRef) setSanctionRef(response.sanctionRef);

          const botMessage: Message = {
            id: (Date.now() + 1).toString(),
            content: response.reply,
            sender: 'bot',
            timestamp: new Date(),
            status: response.status,
            agentStep: response.agentStep,
          };

          setMessages(prev => [...prev, botMessage]);
        } catch (error) {
          setIsTyping(false);
          const errorMessage: Message = {
            id: (Date.now() + 1).toString(),
            content: language === 'en'
              ? "Upload received but processing failed. Please try again."
              : "பதிவேற்றம் பெறப்பட்டது ஆனால் செயலாக்கம் தோல்வியடைந்தது. மீண்டும் முயற்சிக்கவும்.",
            sender: 'bot',
            timestamp: new Date(),
          };
          setMessages(prev => [...prev, errorMessage]);
        }
      })();
    }
  };

  return (
    <div className={cn('h-screen flex flex-col lg:flex-row bg-background', darkMode && 'dark')}>
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0 h-full">
        <ChatHeader
          language={language}
          onToggleLanguage={() => setLanguage(l => l === 'en' ? 'ta' : 'en')}
          onToggleXAI={() => setShowXAI(!showXAI)}
          showXAIToggle={!!xaiData}
          darkMode={darkMode}
          onToggleDarkMode={() => setDarkMode(!darkMode)}
        />

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 scrollbar-hide">
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} language={language} />
          ))}
          
          {currentSentiment && (
            <EmpathyBanner sentiment={currentSentiment} language={language} />
          )}
          
          {currentStatus && (
            <StatusMessage step={currentStatus} language={language} />
          )}
          
          {isTyping && !currentStatus && <TypingIndicator />}
          
          {showUpload && (
            <div className="max-w-sm ml-11">
              <SalarySlipUpload
                language={language}
                onUploadComplete={handleUploadComplete}
                onClose={() => setShowUpload(false)}
              />
            </div>
          )}
          
          {sanctionRef && (
            <div className="max-w-md ml-11">
              <SanctionLetterCard sanctionRef={sanctionRef} language={language} />
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Mobile XAI Accordion */}
        {showXAI && xaiData && (
          <div className="lg:hidden border-t border-border bg-card animate-slide-in-bottom max-h-[40vh] overflow-y-auto">
            <XAIPanel
              data={xaiData}
              language={language}
              onClose={() => setShowXAI(false)}
              isDrawer
            />
          </div>
        )}

        <ChatInput onSend={handleSend} disabled={isTyping} language={language} />
      </div>

      {/* Desktop XAI Panel */}
      <aside className="hidden lg:flex flex-col w-80 xl:w-96 border-l border-border bg-card overflow-hidden">
        <XAIPanel data={xaiData} language={language} />
      </aside>
    </div>
  );
};

export default LoanChatbot;
