import React, { useState } from "react";
import { Card, CardContent } from "./components/ui/card";
import { Button } from "./components/ui/button";
import { Loader2 } from "lucide-react";

export default function SpeechSummarizer() {
  const [file, setFile] = useState<File | null>(null);
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
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-6">
      <Card className="w-full max-w-lg shadow-lg rounded-2xl">
        <CardContent className="p-6 space-y-6">
          <h1 className="text-2xl font-semibold text-center">
            Распознавание и суммаризация речи
          </h1>

          <div className="flex flex-col items-center gap-3">
            <input
              type="file"
              accept="audio/*"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
            <Button
              onClick={handleUpload}
              disabled={!file || loading}
              className="w-full"
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin mr-2 h-4 w-4" /> Обработка...
                </>
              ) : (
                "Отправить на обработку"
              )}
            </Button>
          </div>

          {(transcript || summary) && (
            <div className="space-y-4 mt-6">
              <div>
                <h2 className="font-medium text-lg mb-1">📝 Расшифровка</h2>
                <p className="bg-gray-100 p-3 rounded-xl text-gray-800 whitespace-pre-wrap">
                  {transcript}
                </p>
              </div>
              <div>
                <h2 className="font-medium text-lg mb-1">💡 Суммаризация</h2>
                <p className="bg-gray-100 p-3 rounded-xl text-gray-800 whitespace-pre-wrap">
                  {summary}
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
