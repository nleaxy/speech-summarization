import React, { useState } from "react";
import { motion } from "framer-motion";
import { Card, CardContent } from "./components/ui/card";
import { Button } from "./components/ui/button";
import { Loader2, Upload, Mic, Languages } from "lucide-react";

export default function SpeechSummarizer() {
  const [file, setFile] = useState<File | null>(null);
  const [language, setLanguage] = useState("ru");
  const [loading, setLoading] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [summary, setSummary] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return alert("Пожалуйста, выберите аудиофайл");

    setLoading(true);
    setTranscript("");
    setSummary("");

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("language", language);

      // 👉 Подставь сюда свой реальный ML эндпоинт
      const res = await fetch("http://localhost:8000/api/transcribe", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Ошибка при обработке файла");

      const data = await res.json();

      setTranscript(data.transcript || "Распознанный текст не получен");
      setSummary(data.summary || "Суммаризация не получена");
    } catch (err) {
      console.error(err);
      alert("Ошибка при отправке файла");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-6">
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-lg"
      >
        <Card className="shadow-2xl rounded-3xl backdrop-blur-sm bg-white/80 border border-gray-100">
          <CardContent className="p-8 space-y-8">
            <div className="text-center space-y-2">
              <h1 className="text-3xl font-bold text-gray-900 tracking-tight">
                Распознавание и суммаризация речи
              </h1>
              <p className="text-gray-500 text-sm">
                Загрузите аудиофайл и получите текст + краткое содержание
              </p>
            </div>

            <div className="space-y-4">
              {/* Language Selector */}
              <div className="flex items-center gap-2">
                <Languages className="text-blue-600 w-5 h-5" />
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full border rounded-xl p-2 text-gray-700 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                >
                  <option value="ru">Русский</option>
                  <option value="en">Английский</option>
                  <option value="es">Испанский</option>
                  <option value="de">Немецкий</option>
                  <option value="fr">Французский</option>
                </select>
              </div>

              {/* File Upload */}
              <label className="flex flex-col items-center justify-center border-2 border-dashed border-blue-300 rounded-2xl p-6 cursor-pointer hover:bg-blue-50 transition">
                <Upload className="w-8 h-8 text-blue-500 mb-2" />
                <span className="text-gray-600 text-sm font-medium">
                  {file ? file.name : "Перетащите или выберите аудиофайл"}
                </span>
                <input
                  type="file"
                  accept="audio/*"
                  onChange={handleFileChange}
                  className="hidden"
                />
              </label>

              {/* Upload Button */}
              <Button
                onClick={handleUpload}
                disabled={!file || loading}
                className="w-full rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 text-base"
              >
                {loading ? (
                  <>
                    <Loader2 className="animate-spin mr-2 h-4 w-4" />{" "}
                    Обработка...
                  </>
                ) : (
                  <>
                    <Mic className="mr-2 h-4 w-4" /> Отправить на обработку
                  </>
                )}
              </Button>
            </div>

            {/* Results */}
            {(transcript || summary) && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4 }}
                className="space-y-6 mt-8"
              >
                <div>
                  <h2 className="font-semibold text-lg mb-2 text-gray-800">
                    📝 Расшифровка
                  </h2>
                  <p className="bg-gray-100 p-4 rounded-xl text-gray-700 whitespace-pre-wrap text-sm leading-relaxed">
                    {transcript}
                  </p>
                </div>
                <div>
                  <h2 className="font-semibold text-lg mb-2 text-gray-800">
                    💡 Суммаризация
                  </h2>
                  <p className="bg-gray-100 p-4 rounded-xl text-gray-700 whitespace-pre-wrap text-sm leading-relaxed">
                    {summary}
                  </p>
                </div>
              </motion.div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
