import "./App.css";
import NavBar from "./components/NavBar";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import { Home } from "./components/Pages/Home";
import { Sender } from "./components/Pages/Sender";
import { Receiver } from "./components/Pages/Receiver";
import { ProjectContributor } from "./components/Pages/ProjectContributor";
import VoiceComparison from './components/Pages/VoiceChecker';

function App() {
  return (
    <>
      <Router>
        <NavBar />

        <div className="pages">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/Sender" element={<Sender />} />
            <Route path="/Receiver" element={<Receiver />} />
            <Route path="/VoiceChecker" element={<VoiceComparison />} /> 
            <Route
              path="/ProjectContributor"
              element={<ProjectContributor />}
            />
          </Routes>
        </div>
      </Router>
    </>
  );
}

export default App;
