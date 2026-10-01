import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import { applySavedTheme } from "./hooks/useTheme";
import "./index.css";
import "./styles/factory.css";

applySavedTheme();

createRoot(document.getElementById("root")!).render(<App />);
