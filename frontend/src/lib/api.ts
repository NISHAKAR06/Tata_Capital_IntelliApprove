// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface OrchestratorState {
  stage?: string;
  loan_amount?: number;
  tenure?: number;
  personalized_rate?: number;
  emi?: number;
  pre_approved_limit?: number;
  crm_data?: Record<string, any>;
  kyc_verified?: boolean;
  credit_score?: number;
  explainability?: Record<string, any>;
  sanction_data?: Record<string, any>;
  gamification?: Record<string, any>;
}

export interface OrchestratorRequest {
  user_message?: string;
  stage?: string;
  state?: OrchestratorState;
  customer_profile?: Record<string, any>;
  loan_request?: {
    loan_amount?: number;
    tenure_months?: number;
  };
  event?: string; // e.g. "document_uploaded", "kyc_verified"
  uploaded_document_type?: string; // e.g. "salary_slip"
}

export interface OrchestratorResponse {
  stage: string;
  message_to_user: string;
  worker_called: string;
  worker_payload: Record<string, any>;
  state_updates: OrchestratorState;
  action: 'continue' | 'request_upload' | 'end' | 'process_salary_slip' | 'human_handoff';
  fallback_needed: boolean;
  model_version?: string;
}

// Legacy chat interfaces kept for now (can be refactored later)
export interface ChatMessage {
  message: string;
  session_id: string;
  language: 'en' | 'ta';
}

export interface ChatResponse {
  reply: string;
  status?: 'processing' | 'approved' | 'rejected' | 'pending_documents';
  sentiment?: 'neutral' | 'hesitation' | 'confusion' | 'negative';
  requiresSalarySlip?: boolean;
  sanctionRef?: string;
  xaiData?: {
    emiPercentage?: number;
    creditScore?: number;
    interestRate?: number;
    reasoning?: string[];
  };
  agentStep?: string;
}

export interface VerifyUserResponse {
  verified: boolean;
  name?: string;
  phone?: string;
}

export interface CreditScoreResponse {
  score: number;
  rating: 'excellent' | 'good' | 'fair' | 'poor';
}

export interface UploadResponse {
  success: boolean;
  message: string;
  documentId?: string;
  file_id?: string;
}

// Generate unique session ID
export const generateSessionId = (): string => {
  return 'sess_' + Math.random().toString(36).substring(2, 15) + Date.now().toString(36);
};

// Get or create session ID from localStorage
export const getSessionId = (): string => {
  let sessionId = localStorage.getItem('loan_chat_session_id');
  if (!sessionId) {
    sessionId = generateSessionId();
    localStorage.setItem('loan_chat_session_id', sessionId);
  }
  return sessionId;
};

/**
 * New unified orchestration call to FastAPI /orchestrate
 * This is the primary way the frontend talks to the backend loan brain.
 */
export const callOrchestrator = async (
  orchestratorPayload: OrchestratorRequest
): Promise<OrchestratorResponse> => {
  const response = await fetch(`${API_BASE_URL}/orchestrate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(orchestratorPayload),
  });

  if (!response.ok) {
    throw new Error(`Orchestrator HTTP error! status: ${response.status}`);
  }

  return response.json();
};

// Send chat message (can be refactored to use callOrchestrator later)
export const sendChatMessage = async (data: ChatMessage): Promise<ChatResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Chat API error:', error);
    // Return mock response for demo
    return getMockResponse(data.message, data.language);
  }
};

// Verify user by phone
export const verifyUser = async (phone: string): Promise<VerifyUserResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/verifyUser?phone=${encodeURIComponent(phone)}`);
    if (!response.ok) throw new Error('Verification failed');
    return await response.json();
  } catch (error) {
    console.error('Verify user error:', error);
    return { verified: true, name: 'Demo User', phone };
  }
};

// Get credit score
export const getCreditScore = async (customerId: string): Promise<CreditScoreResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/creditScore?id=${encodeURIComponent(customerId)}`);
    if (!response.ok) throw new Error('Credit score fetch failed');
    return await response.json();
  } catch (error) {
    console.error('Credit score error:', error);
    return { score: 750, rating: 'excellent' };
  }
};

// Upload salary slip (wire to orchestrator doc event)
export const uploadSalarySlip = async (file: File, sessionId: string): Promise<UploadResponse> => {
  try {
    const formData = new FormData();
    formData.append('salarySlip', file);
    formData.append('session_id', sessionId);
    
    const response = await fetch(`${API_BASE_URL}/uploadSalarySlip`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) throw new Error('Upload failed');
    return await response.json();
  } catch (error) {
    console.error('Upload error:', error);
    // Mock success for demo
    return { success: true, message: 'Document uploaded successfully', documentId: 'doc_' + Date.now() };
  }
};

// Download sanction letter
export const downloadSanctionLetter = async (ref: string): Promise<void> => {
  try {
    const response = await fetch(`${API_BASE_URL}/downloadSanctionLetter?ref=${encodeURIComponent(ref)}`);
    if (!response.ok) throw new Error('Download failed');
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sanction_letter_${ref}.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Download error:', error);
    alert('Demo mode: Sanction letter download simulated');
  }
};

// Mock response generator for demo
const getMockResponse = (message: string, language: 'en' | 'ta'): ChatResponse => {
  const lowerMessage = message.toLowerCase();
  
  const responses: Record<string, ChatResponse> = {
    greeting: {
      reply: language === 'en' 
        ? "Hello! I'm your AI Loan Assistant. I can help you with personal loans, home loans, and business loans. What type of loan are you interested in?"
        : "வணக்கம்! நான் உங்கள் AI கடன் உதவியாளர். தனிப்பட்ட கடன்கள், வீட்டுக் கடன்கள் மற்றும் வணிகக் கடன்களில் நான் உங்களுக்கு உதவ முடியும். எந்த வகையான கடனில் நீங்கள் ஆர்வமாக உள்ளீர்கள்?",
      agentStep: 'Sales Agent - Initial Contact',
    },
    loan_amount: {
      reply: language === 'en'
        ? "Great choice! For a personal loan of ₹5,00,000, I'll need to verify some details. Could you please share your registered mobile number for KYC verification?"
        : "சிறந்த தேர்வு! ₹5,00,000 தனிப்பட்ட கடனுக்கு, சில விவரங்களை சரிபார்க்க வேண்டும். KYC சரிபார்ப்புக்காக உங்கள் பதிவு செய்யப்பட்ட மொபைல் எண்ணை பகிர முடியுமா?",
      agentStep: 'Sales Agent - Requirement Analysis',
    },
    verification: {
      reply: language === 'en'
        ? "Thank you! I'm now verifying your KYC details... Your identity has been verified successfully! Let me check your credit score and eligibility."
        : "நன்றி! நான் இப்போது உங்கள் KYC விவரங்களை சரிபார்க்கிறேன்... உங்கள் அடையாளம் வெற்றிகரமாக சரிபார்க்கப்பட்டது! உங்கள் கடன் மதிப்பெண் மற்றும் தகுதியை சரிபார்க்கிறேன்.",
      agentStep: 'Verification Agent - KYC Check',
      xaiData: {
        creditScore: 750,
        reasoning: ['Identity verified via Aadhaar', 'No existing defaults found', 'Credit history: 5+ years']
      }
    },
    salary_required: {
      reply: language === 'en'
        ? "Based on our assessment, we need your latest salary slip to complete the underwriting process. Please upload a PDF of your salary slip."
        : "எங்கள் மதிப்பீட்டின் அடிப்படையில், அண்டர்ரைட்டிங் செயல்முறையை முடிக்க உங்கள் சமீபத்திய சம்பள சீட்டு தேவை. உங்கள் சம்பள சீட்டின் PDF ஐ பதிவேற்றவும்.",
      status: 'pending_documents',
      requiresSalarySlip: true,
      agentStep: 'Underwriting Agent - Document Collection',
    },
    approved: {
      reply: language === 'en'
        ? "🎉 Congratulations! Your loan has been APPROVED! Loan Amount: ₹5,00,000 | Interest Rate: 10.5% p.a. | EMI: ₹10,624 | Tenure: 60 months. Your sanction letter is ready for download."
        : "🎉 வாழ்த்துக்கள்! உங்கள் கடன் அனுமதிக்கப்பட்டது! கடன் தொகை: ₹5,00,000 | வட்டி விகிதம்: 10.5% p.a. | EMI: ₹10,624 | காலம்: 60 மாதங்கள். உங்கள் அனுமதி கடிதம் பதிவிறக்கத்திற்கு தயாராக உள்ளது.",
      status: 'approved',
      sanctionRef: 'SL' + Date.now().toString().slice(-8),
      agentStep: 'Underwriting Agent - Final Decision',
      xaiData: {
        emiPercentage: 42,
        creditScore: 750,
        interestRate: 10.5,
        reasoning: [
          'EMI is 42% of monthly salary - within acceptable range',
          'Excellent credit score of 750',
          'Rate reduced by 0.5% due to good credit history',
          'Stable employment for 3+ years'
        ]
      }
    },
    confusion: {
      reply: language === 'en'
        ? "I understand this can be overwhelming. Let me simplify: You're eligible for a loan, and I'm here to guide you step by step. Don't worry, I'll help you find the best possible option."
        : "இது குழப்பமாக இருக்கும் என்று புரிகிறது. எளிமையாக சொல்கிறேன்: நீங்கள் கடனுக்கு தகுதியானவர், படிப்படியாக உங்களுக்கு வழிகாட்ட நான் இங்கே இருக்கிறேன். கவலைப்படாதீர்கள், சிறந்த வாய்ப்பைக் கண்டுபிடிக்க உதவுவேன்.",
      sentiment: 'confusion',
      agentStep: 'Master Agent - Empathy Response',
    }
  };

  if (lowerMessage.includes('hello') || lowerMessage.includes('hi') || lowerMessage.includes('வணக்கம்')) {
    return responses.greeting;
  }
  if (lowerMessage.includes('loan') || lowerMessage.includes('கடன்') || lowerMessage.includes('500000') || lowerMessage.includes('5 lakh')) {
    return responses.loan_amount;
  }
  if (lowerMessage.includes('phone') || lowerMessage.includes('mobile') || lowerMessage.includes('verify') || /\d{10}/.test(message)) {
    return responses.verification;
  }
  if (lowerMessage.includes('salary') || lowerMessage.includes('slip') || lowerMessage.includes('upload')) {
    return responses.salary_required;
  }
  if (lowerMessage.includes('approved') || lowerMessage.includes('accept') || lowerMessage.includes('proceed')) {
    return responses.approved;
  }
  if (lowerMessage.includes('confused') || lowerMessage.includes('help') || lowerMessage.includes('understand')) {
    return responses.confusion;
  }

  return {
    reply: language === 'en'
      ? "I understand. Could you tell me more about what you're looking for? I can help with loan amounts, interest rates, EMI calculations, and eligibility."
      : "புரிகிறது. நீங்கள் என்ன தேடுகிறீர்கள் என்பதை மேலும் சொல்ல முடியுமா? கடன் தொகைகள், வட்டி விகிதங்கள், EMI கணக்கீடுகள் மற்றும் தகுதி ஆகியவற்றில் நான் உதவ முடியும்.",
    agentStep: 'Sales Agent - Information Gathering',
  };
};
