import { useState, useRef } from "react";
import { Upload, FileText, CheckCircle2, AlertCircle, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { uploadSalarySlip } from "@/lib/api";

interface SalarySlipUploadProps {
  language: "en" | "ta";
  conversationId?: string;
  onUploadComplete: (success: boolean) => void;
  onClose: () => void;
}

const SalarySlipUpload = ({
  language,
  conversationId,
  onUploadComplete,
  onClose,
}: SalarySlipUploadProps) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<
    "idle" | "uploading" | "success" | "error"
  >("idle");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (selectedFile.type !== "application/pdf") {
        alert(
          language === "en"
            ? "Please upload a PDF file only"
            : "PDF கோப்பை மட்டும் பதிவேற்றவும்"
        );
        return;
      }
      if (selectedFile.size > 5 * 1024 * 1024) {
        alert(
          language === "en"
            ? "File size must be less than 5MB"
            : "கோப்பு அளவு 5MB க்கும் குறைவாக இருக்க வேண்டும்"
        );
        return;
      }
      setFile(selectedFile);
    }
  };

  const handleUpload = async () => {
    if (!file || !conversationId) {
      setStatus("error");
      return;
    }

    setUploading(true);
    setStatus("uploading");

    // Simulate progress
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return prev;
        }
        return prev + 10;
      });
    }, 200);

    try {
      const result = await uploadSalarySlip(file, conversationId);
      clearInterval(progressInterval);
      setProgress(100);

      if (result.success) {
        setStatus("success");
        setTimeout(() => onUploadComplete(true), 1500);
      } else {
        setStatus("error");
      }
    } catch (error) {
      clearInterval(progressInterval);
      setStatus("error");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-card rounded-xl border border-border p-4 shadow-md animate-fade-in-up">
      <div className="flex items-center justify-between mb-3">
        <h3
          className={cn(
            "font-semibold text-foreground",
            language === "ta" && "font-tamil"
          )}
        >
          {language === "en"
            ? "Upload Salary Slip"
            : "சம்பள சீட்டை பதிவேற்றவும்"}
        </h3>
        <button
          onClick={onClose}
          className="p-1 hover:bg-muted rounded-full transition-colors"
        >
          <X className="w-4 h-4 text-muted-foreground" />
        </button>
      </div>

      {status === "success" ? (
        <div className="flex flex-col items-center py-6 text-success">
          <CheckCircle2 className="w-12 h-12 mb-2 animate-pulse-glow" />
          <p className={cn("font-medium", language === "ta" && "font-tamil")}>
            {language === "en" ? "Upload Successful!" : "பதிவேற்றம் வெற்றி!"}
          </p>
        </div>
      ) : status === "error" ? (
        <div className="flex flex-col items-center py-6 text-destructive">
          <AlertCircle className="w-12 h-12 mb-2" />
          <p className={cn("font-medium", language === "ta" && "font-tamil")}>
            {language === "en"
              ? "Upload Failed. Please try again."
              : "பதிவேற்றம் தோல்வி. மீண்டும் முயற்சிக்கவும்."}
          </p>
        </div>
      ) : (
        <>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            onChange={handleFileSelect}
            className="hidden"
          />

          {!file ? (
            <button
              onClick={() => fileInputRef.current?.click()}
              className="w-full border-2 border-dashed border-border rounded-lg p-6 hover:border-primary hover:bg-accent/50 transition-all flex flex-col items-center gap-2"
            >
              <Upload className="w-8 h-8 text-muted-foreground" />
              <span
                className={cn(
                  "text-sm text-muted-foreground",
                  language === "ta" && "font-tamil"
                )}
              >
                {language === "en"
                  ? "Tap to select PDF file"
                  : "PDF கோப்பைத் தேர்ந்தெடுக்க தட்டவும்"}
              </span>
              <span className="text-xs text-muted-foreground/70">
                {language === "en" ? "Max size: 5MB" : "அதிகபட்ச அளவு: 5MB"}
              </span>
            </button>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
                <FileText className="w-8 h-8 text-primary" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{file.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {(file.size / 1024).toFixed(1)} KB
                  </p>
                </div>
                {!uploading && (
                  <button
                    onClick={() => setFile(null)}
                    className="p-1 hover:bg-background rounded-full"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>

              {uploading && (
                <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
                  <div
                    className="h-full bg-primary transition-all duration-300 ease-out"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              )}

              <button
                onClick={handleUpload}
                disabled={uploading}
                className={cn(
                  "w-full py-3 rounded-xl font-medium transition-all",
                  "bg-primary text-primary-foreground hover:bg-primary/90",
                  "disabled:opacity-50 disabled:cursor-not-allowed",
                  language === "ta" && "font-tamil"
                )}
              >
                {uploading
                  ? language === "en"
                    ? "Uploading..."
                    : "பதிவேற்றுகிறது..."
                  : language === "en"
                  ? "Upload Document"
                  : "ஆவணத்தை பதிவேற்றவும்"}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default SalarySlipUpload;
