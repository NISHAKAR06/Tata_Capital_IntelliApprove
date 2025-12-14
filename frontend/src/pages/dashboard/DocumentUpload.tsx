import { useRef, useState } from "react";
import { motion } from "framer-motion";
import { Upload, FileText, CheckCircle } from "lucide-react";
import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { toast } from "@/components/ui/sonner";
import { uploadSalarySlip } from "@/lib/api";
import { useConversation } from "@/contexts/ConversationContext";

interface UploadedFile {
  name: string;
  status: "uploaded" | "pending" | "error";
}

const DocumentUpload = () => {
  const { conversationId, setLastResponse } = useConversation();
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleFileChange = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!conversationId) {
      toast.error(
        "Start a chat first so we can link documents to your application."
      );
      return;
    }

    setFiles((prev) => [...prev, { name: file.name, status: "pending" }]);

    try {
      setIsUploading(true);
      const resp = await uploadSalarySlip(conversationId, file);
      setLastResponse(resp);

      setFiles((prev) =>
        prev.map((f) =>
          f.name === file.name
            ? {
                ...f,
                status: "uploaded",
              }
            : f
        )
      );

      toast.success("Salary slip uploaded successfully.");
    } catch (error) {
      console.error(error);
      setFiles((prev) =>
        prev.map((f) =>
          f.name === file.name
            ? {
                ...f,
                status: "error",
              }
            : f
        )
      );
      toast.error("Failed to upload salary slip. Please try again.");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  return (
    <DashboardLayout>
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Document Upload</h1>
        <p className="text-muted-foreground">
          Upload required documents for verification
        </p>
      </div>

      <div className="grid gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Card variant="glass" className="p-8">
            <div className="upload-zone text-center">
              <Upload className="w-12 h-12 text-primary mx-auto mb-4" />
              <h3 className="font-semibold text-lg mb-2">Upload Salary Slip</h3>
              <p className="text-muted-foreground mb-4">
                Select your latest salary slip to verify your income.
              </p>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                className="hidden"
                onChange={handleFileChange}
              />
              <Button
                variant="outline"
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploading}
              >
                {isUploading ? "Uploading..." : "Select File"}
              </Button>
              {!conversationId && (
                <p className="mt-3 text-xs text-warning">
                  Tip: Start a conversation in Loan Chat first so your documents
                  are linked to the right application.
                </p>
              )}
            </div>
          </Card>
        </motion.div>

        <Card variant="glass" className="p-6">
          <h3 className="font-semibold text-lg mb-4">Uploaded Documents</h3>
          <div className="space-y-3">
            {files.length === 0 && (
              <p className="text-sm text-muted-foreground">
                No documents uploaded yet.
              </p>
            )}
            {files.map((file, i) => (
              <motion.div
                key={file.name}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                className="flex items-center justify-between p-4 bg-secondary/50 rounded-xl"
              >
                <div className="flex items-center gap-3">
                  <FileText className="w-5 h-5 text-primary" />
                  <span>{file.name}</span>
                </div>
                {file.status === "uploaded" && (
                  <CheckCircle className="w-5 h-5 text-success" />
                )}
                {file.status === "pending" && (
                  <span className="text-xs text-muted-foreground">
                    Uploading...
                  </span>
                )}
                {file.status === "error" && (
                  <span className="text-xs text-destructive">Error</span>
                )}
              </motion.div>
            ))}
          </div>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default DocumentUpload;
