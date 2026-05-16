import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyAEyYpsJrZ3nzicS7FxVDJ8IFWNjxBWnh8",
  authDomain: "krishibot-itznoth.firebaseapp.com",
  projectId: "krishibot-itznoth",
  storageBucket: "krishibot-itznoth.firebasestorage.app",
  messagingSenderId: "226283909644",
  appId: "1:226283909644:web:ff46dcaa9e9a24364b3429"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export default app;
