import { createContext, useContext, useState, ReactNode } from "react";
import type { OrchestratorResponse } from "@/lib/api";

interface ConversationContextValue {
  conversationId: string | null;
  lastResponse: OrchestratorResponse | null;
  setConversationId: (id: string | null) => void;
  setLastResponse: (resp: OrchestratorResponse | null) => void;
  resetConversation: () => void;
}

const ConversationContext = createContext<ConversationContextValue | undefined>(undefined);

export const ConversationProvider = ({ children }: { children: ReactNode }) => {
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [lastResponse, setLastResponse] = useState<OrchestratorResponse | null>(null);

  const resetConversation = () => {
    setConversationId(null);
    setLastResponse(null);
  };

  return (
    <ConversationContext.Provider
      value={{ conversationId, lastResponse, setConversationId, setLastResponse, resetConversation }}
    >
      {children}
    </ConversationContext.Provider>
  );
};

export const useConversation = (): ConversationContextValue => {
  const ctx = useContext(ConversationContext);
  if (!ctx) {
    throw new Error("useConversation must be used within a ConversationProvider");
  }
  return ctx;
};
