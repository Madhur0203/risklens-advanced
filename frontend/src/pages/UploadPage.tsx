import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "../api/client";

export default function UploadPage() {
  const [files, setFiles] = useState<FileList | null>(null);
  const qc = useQueryClient();
  const upload = useMutation({ mutationFn: async () => { if (!files?.length) throw new Error("No files selected."); const formData = new FormData(); Array.from(files).forEach((file) => formData.append("files", file)); return (await api.post("/upload", formData, { headers: { "Content-Type": "multipart/form-data" } })).data; }, onSuccess: () => { qc.invalidateQueries({ queryKey: ["dashboard"] }); qc.invalidateQueries({ queryKey: ["cases"] }); } });
  const retrain = useMutation({ mutationFn: async () => (await api.post("/retrain")).data, onSuccess: () => { qc.invalidateQueries({ queryKey: ["dashboard"] }); qc.invalidateQueries({ queryKey: ["cases"] }); } });
  return (
    <div className="page"><div className="page-top"><div><h2>Ingestion & Learning</h2><p className="muted">Upload enterprise-style datasets and retrain the hybrid detection layer.</p></div></div><div className="card"><h3>Upload Files</h3><p className="muted">Supported: CSV, XLSX. Files should include the required columns from the README.</p><input type="file" multiple onChange={(e) => setFiles(e.target.files)} /><div className="button-row"><button className="primary-btn" onClick={() => upload.mutate()}>{upload.isPending ? "Processing..." : "Ingest & Score"}</button><button className="ghost-btn" onClick={() => retrain.mutate()}>{retrain.isPending ? "Retraining..." : "Retrain on Current Feedback"}</button></div>{upload.data ? <p className="success-text">{upload.data.message} ({upload.data.rows} rows)</p> : null}{retrain.data ? <p className="success-text">{retrain.data.message}</p> : null}</div><div className="card"><h3>Suggested data files</h3><ul className="reason-list"><li>shipments.csv</li><li>vendor_master.xlsx</li><li>exceptions_log.csv</li><li>daily_filing_export.xlsx</li></ul></div></div>
  );
}
