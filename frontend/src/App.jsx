import Navbar from "./components/Navbar";
import UploadPanel from "./components/UploadPanel";
import ChatPanel from "./components/ChatPanel";

function App() {
  return (
    <div className="min-h-screen bg-[#0B1F3A]">
      <Navbar />

      <div className="max-w-7xl mx-auto p-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <UploadPanel />

          <div className="lg:col-span-2">
            <ChatPanel />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;