function Navbar() {
  return (
    <nav className="bg-[#13294B] shadow-lg">
      <div className="max-w-7xl mx-auto px-6 py-5 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white">
            🧠 IntelliDocs AI
          </h1>
          <p className="text-gray-300 text-sm">
            AI Powered RAG Document Assistant
          </p>
        </div>

        <span className="text-white font-semibold">
          React + FastAPI
        </span>
      </div>
    </nav>
  );
}

export default Navbar;