import { useState } from "react";
import { motion } from "framer-motion";
import { Upload, FileText, CheckCircle, X } from "lucide-react";
import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const DocumentUpload = () => {
  const [files, setFiles] = useState<{name: string; status: string}[]>([
    { name: "aadhaar_card.pdf", status: "uploaded" },
    { name: "pan_card.pdf", status: "uploaded" },
  ]);

  return (
    <DashboardLayout>
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Document Upload</h1>
        <p className="text-muted-foreground">Upload required documents for verification</p>
      </div>

      <div className="grid gap-6">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <Card variant="glass" className="p-8">
            <div className="upload-zone">
              <Upload className="w-12 h-12 text-primary mx-auto mb-4" />
              <h3 className="font-semibold text-lg mb-2">Drag & Drop Files Here</h3>
              <p className="text-muted-foreground mb-4">or click to browse</p>
              <Button variant="outline">Select Files</Button>
            </div>
          </Card>
        </motion.div>

        <Card variant="glass" className="p-6">
          <h3 className="font-semibold text-lg mb-4">Uploaded Documents</h3>
          <div className="space-y-3">
            {files.map((file, i) => (
              <motion.div key={file.name} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }} className="flex items-center justify-between p-4 bg-secondary/50 rounded-xl">
                <div className="flex items-center gap-3">
                  <FileText className="w-5 h-5 text-primary" />
                  <span>{file.name}</span>
                </div>
                <CheckCircle className="w-5 h-5 text-success" />
              </motion.div>
            ))}
          </div>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default DocumentUpload;
