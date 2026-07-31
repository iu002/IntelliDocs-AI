import { useState } from "react";
import API from "../services/api";

function ChatPanel() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("🤖 AI responses will appear here...");

  const askAI = async () => {
    if (question.trim() === "") {
      alert("Please enter a question.");
      return;
    }

    setAnswer("🤖 Thinking...");

    try {
      const response = await API.post("/chat", {
        question: question,
      });

      setAnswer(response.data.answer);
    } catch (error) {
      console.error(error);
      setAnswer("❌ Something went wrong.");
    }
  };

  return (
    <div className="bg-[#F5F1E8] rounded-2xl shadow-xl p-6">
      <h2 className="text-2xl font-bold text-[#13294B] mb-6">
        💬 Ask Your Document
      </h2>

      <textarea
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask anything about your document..."
        className="w-full h-40 border rounded-lg p-3 resize-none"
      />

      <button
        onClick={askAI}
        className="mt-4 bg-[#163A6B] text-white py-3 px-6 rounded-lg hover:bg-[#214D87]"
      >
        Ask AI
      </button>

      <div className="mt-6 p-4 border rounded-lg bg-white min-h-[150px]">
        {answer}
      </div>
    </div>
  );
}

export default ChatPanel;