import React from "react";
import SpeechSummarizer from "./SpeechSummarizer";
import AnimatedBackground from "./components/AnimatedBackground";

export default function App() {
  return (
    <AnimatedBackground>
      <SpeechSummarizer />
    </AnimatedBackground>
  );
}
