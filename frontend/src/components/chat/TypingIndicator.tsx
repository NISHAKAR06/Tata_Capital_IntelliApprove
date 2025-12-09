const TypingIndicator = () => {
  return (
    <div className="flex items-center gap-3 animate-fade-in-up">
      <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
        <span className="text-primary-foreground text-xs font-semibold">AI</span>
      </div>
      <div className="chat-bubble-bot flex items-center gap-1 py-4">
        <span className="w-2 h-2 bg-muted-foreground/60 rounded-full animate-typing-dot" />
        <span className="w-2 h-2 bg-muted-foreground/60 rounded-full animate-typing-dot-2" />
        <span className="w-2 h-2 bg-muted-foreground/60 rounded-full animate-typing-dot-3" />
      </div>
    </div>
  );
};

export default TypingIndicator;
