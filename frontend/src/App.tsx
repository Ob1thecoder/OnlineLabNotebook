import { BrowserRouter, Route, Routes } from "react-router-dom";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<div className="p-8 text-brand-700">Online Labnotebook — Phase 1 scaffold</div>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
