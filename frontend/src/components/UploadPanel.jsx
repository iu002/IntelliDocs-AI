import { useState } from "react";
import API from "../services/api";

function UploadPanel() {
  const [file, setFile] = useState(null);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [status, setStatus] = useState("");

  const uploadFile = async () => {
    if (!file) {
      alert("Please select a PDF.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setStatus("Uploading...");

      const response = await API.post("/upload", formData);

      // NOTE: /upload already calls index_document() server-side
      // (see backend/app/routers/upload.py), so a separate call to
      // /index here was redundant - it re-extracted, re-chunked, and
      // re-embedded the same file a second time on every upload, and
      // was a second point of failure. Removed.

      setStatus("✅ Uploaded & Indexed Successfully");

      setUploadedFiles((prev) => [
        ...prev,
        response.data.original_filename,
      ]);
    } catch (error) {
      console.error(error);
      setStatus("❌ Upload Failed");
    }
  };

  return (
    <div className="bg-[#F5F1E8] rounded-2xl shadow-xl p-6">
      <h2 className="text-2xl font-bold text-[#13294B] mb-6">
        📄 Upload Document
      </h2>

      <input
        type="file"
        accept=".pdf,.doc,.docx,.txt"
        onChange={(e) => setFile(e.target.files[0])}
        className="w-full border rounded-lg p-3"
      />

      <button
        onClick={uploadFile}
        className="w-full mt-4 bg-[#163A6B] text-white py-3 rounded-lg hover:bg-[#214D87]"
      >
        Upload
      </button>

      <p className="mt-3 text-green-700 font-semibold">
        {status}
      </p>

      <div className="mt-8">
        <h3 className="font-semibold text-lg">
          Uploaded Files
        </h3>

        {uploadedFiles.length === 0 ? (
          <p className="text-gray-500">
            No document uploaded
          </p>
        ) : (
          <ul className="mt-2">
            {uploadedFiles.map((name, index) => (
              <li key={index}>📄 {name}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default UploadPanel;