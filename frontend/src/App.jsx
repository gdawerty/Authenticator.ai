import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from 'react-hot-toast';
import Login from "./pages/Login";
import Upload from "./pages/Upload";
import Verify from "./pages/Verify";
import Dashboard from "./pages/Dashboard";
import { useAuthStore } from "./context/useAuthStore";

// Protected Route wrapper
const ProtectedRoute = ({ children }) => {
  const token = useAuthStore((state) => state.token);
  return token ? children : <Navigate to="/login" />;
};

export default function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-right" />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/upload" element={<ProtectedRoute><Upload /></ProtectedRoute>} />
        <Route path="/verify/:docId" element={<ProtectedRoute><Verify /></ProtectedRoute>} />
      </Routes>
    </BrowserRouter>
  );
}
