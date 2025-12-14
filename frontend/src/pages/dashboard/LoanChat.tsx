import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Send, Bot, User, Mic, Paperclip } from "lucide-react";
import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { toast } from "@/components/ui/sonner";
import { postChatMessage, postVoiceMessage } from "@/lib/api";
import { useConversation } from "@/contexts/ConversationContext";

type ChatRole = "user" | "assistant";

interface ChatMessage {
  id: number;
  role: ChatRole;
  content: string;
}

const initialMessages: ChatMessage[] = [];

const LoanChat = () => {
  const { conversationId, setConversationId, setLastResponse } =
    useConversation();
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [voiceFile, setVoiceFile] = useState<File | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const hasBootstrapped = useRef(false);

  // Call backend once on first load to get a real welcome message
  useEffect(() => {
    if (hasBootstrapped.current) return;
    if (messages.length > 0 || conversationId) return;

    hasBootstrapped.current = true;

    const bootstrap = async () => {
      try {
        setIsSending(true);
        const resp = await postChatMessage("", {});

        if (resp.conversation_id) {
          setConversationId(resp.conversation_id);
        }

        setLastResponse(resp);

        const assistantMessage: ChatMessage = {
          id: 1,
          role: "assistant",
          content:
            resp.message_to_user ||
            "Hello! I'm your AI Loan Assistant. How can I help you today?",
        };

        setMessages([assistantMessage]);
      } catch (err) {
        console.error("Failed to load welcome message", err);
      } finally {
        setIsSending(false);
      }
    };

    void bootstrap();
  }, [conversationId, messages.length, setConversationId, setLastResponse]);

  const handleSend = async () => {
    if (!input.trim() || isSending) return;

    const userContent = input.trim();
    const nextId = messages.length + 1;
    const userMessage: ChatMessage = {
      id: nextId,
      role: "user",
      content: userContent,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    try {
      setIsSending(true);
      const resp = await postChatMessage(userContent, {
        conversationId: conversationId ?? undefined,
      });

      if (resp.conversation_id && resp.conversation_id !== conversationId) {
        setConversationId(resp.conversation_id);
      }

      setLastResponse(resp);

      const assistantMessage: ChatMessage = {
        id: nextId + 1,
        role: "assistant",
        content: resp.message_to_user || "",
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error(err);
      toast.error("Failed to contact loan assistant. Please try again.");
    } finally {
      setIsSending(false);
    }
  };

  const handleVoiceSend = async (file: File) => {
    if (isSending) return;

    const nextId = messages.length + 1;
    const userMessage: ChatMessage = {
      id: nextId,
      role: "user",
      content: "[Voice message sent]",
    };

    // Show the user's voice message immediately in the chat
    setMessages((prev) => [...prev, userMessage]);

    try {
      setIsSending(true);
      const resp = await postVoiceMessage(file, {
        conversationId: conversationId ?? undefined,
      });

      if (resp.conversation_id && resp.conversation_id !== conversationId) {
        setConversationId(resp.conversation_id);
      }

      setLastResponse(resp);

      const transcript =
        ((resp.invoke_worker as any)?.user_transcript as string | undefined) ||
        "Transcribed audio";

      // Always update the user's bubble so it never stays as
      // "[Voice message sent]".
      setMessages((prev) =>
        prev.map((m) => (m.id === nextId ? { ...m, content: transcript } : m))
      );

      const assistantMessage: ChatMessage = {
        id: nextId + 1,
        role: "assistant",
        content:
          resp.message_to_user ||
          "I received your voice message and processed it.",
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setVoiceFile(null);
    } catch (err) {
      console.error(err);
      toast.error("Failed to send voice message. Please try again.");
    } finally {
      setIsSending(false);
    }
  };

  const startRecording = async () => {
    if (isRecording || isSending) return;

    if (!navigator.mediaDevices?.getUserMedia) {
      toast.error("Voice input is not supported in this browser.");
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const blob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        const file = new File([blob], "voice-message.webm", {
          type: "audio/webm",
        });
        setVoiceFile(file);
        await handleVoiceSend(file);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Failed to start recording", err);
      toast.error("Unable to access microphone.");
    }
  };

  const stopRecording = () => {
    const recorder = mediaRecorderRef.current;
    if (recorder && recorder.state !== "inactive") {
      recorder.stop();
    }
    setIsRecording(false);
    toast.message("Stopped recording", {
      description: "Sending your voice message to IntelliApprove...",
    });
  };

  return (
    <DashboardLayout>
      <div className="h-[calc(100vh-4rem)] flex flex-col">
        <div className="mb-6">
          <h1 className="text-3xl font-bold">Loan Chat</h1>
          <p className="text-muted-foreground">
            Chat with our AI assistant to apply for loans
          </p>
        </div>

        <Card variant="glass" className="flex-1 flex flex-col overflow-hidden">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((message, index) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, x: message.role === "user" ? 20 : -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`flex items-end gap-3 ${
                  message.role === "user" ? "flex-row-reverse" : ""
                }`}
              >
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                    message.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-secondary text-secondary-foreground"
                  }`}
                >
                  {message.role === "user" ? (
                    <User className="w-5 h-5" />
                  ) : (
                    <Bot className="w-5 h-5" />
                  )}
                </div>
                <div
                  className={`chat-bubble ${
                    message.role === "user"
                      ? "chat-bubble-user"
                      : "chat-bubble-ai"
                  }`}
                >
                  {message.content}
                </div>
              </motion.div>
            ))}

            {/* Typing indicator while waiting for AI response */}
            {isSending && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-end gap-3"
              >
                <div className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 bg-secondary text-secondary-foreground">
                  <Bot className="w-5 h-5" />
                </div>
                <div className="chat-bubble chat-bubble-ai flex items-center gap-1">
                  <motion.span
                    className="inline-block w-2 h-2 rounded-full bg-muted-foreground"
                    animate={{ opacity: [0.2, 1, 0.2], y: [0, -2, 0] }}
                    transition={{
                      repeat: Infinity,
                      duration: 0.8,
                      ease: "easeInOut",
                    }}
                  />
                  <motion.span
                    className="inline-block w-2 h-2 rounded-full bg-muted-foreground"
                    animate={{ opacity: [0.2, 1, 0.2], y: [0, -2, 0] }}
                    transition={{
                      repeat: Infinity,
                      duration: 0.8,
                      ease: "easeInOut",
                      delay: 0.15,
                    }}
                  />
                  <motion.span
                    className="inline-block w-2 h-2 rounded-full bg-muted-foreground"
                    animate={{ opacity: [0.2, 1, 0.2], y: [0, -2, 0] }}
                    transition={{
                      repeat: Infinity,
                      duration: 0.8,
                      ease: "easeInOut",
                      delay: 0.3,
                    }}
                  />
                </div>
              </motion.div>
            )}
          </div>

          {/* Input */}
          <div className="p-4 border-t border-border">
            <div className="flex gap-3">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                placeholder="Type your message..."
                className="flex-1"
                disabled={isSending}
              />
              <div className="flex items-center gap-2">
                {/* File upload (generic documents/images) */}
                <input
                  type="file"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) {
                      toast.success(`Attached file: ${file.name}`);
                    }
                  }}
                  className="hidden"
                  id="file-upload"
                />
                <Button type="button" variant="outline" size="icon" asChild>
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <Paperclip className="w-5 h-5" />
                  </label>
                </Button>

                {/* Voice input using microphone */}
                <Button
                  type="button"
                  variant={isRecording ? "destructive" : "secondary"}
                  size="icon"
                  onClick={isRecording ? stopRecording : startRecording}
                  disabled={isSending}
                >
                  <Mic
                    className={`w-5 h-5 ${isRecording ? "animate-pulse" : ""}`}
                  />
                </Button>
              </div>
              <Button
                variant="hero"
                size="icon"
                onClick={handleSend}
                disabled={isSending}
              >
                <Send className="w-5 h-5" />
              </Button>
            </div>
            {isRecording && (
              <p className="mt-2 text-xs text-muted-foreground">
                Listening... click the mic again to stop and send.
              </p>
            )}
          </div>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default LoanChat;
