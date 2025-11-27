import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent } from "./components/ui/card";
import { Button } from "./components/ui/button";
import {
  Loader2,
  Upload,
  Sparkles,
  Languages,
  FileAudio,
  CheckCircle2,
  Copy,
  Check,
  Shrink,
} from "lucide-react";

const SUMMARY_TYPES = {
  brief: "⚡ Кратко",
  detailed: "📄 Подробно",
  structured: "📑 Структурированно",
  bullet_points: "🔑 Ключевые пункты",
  executive: "👔 Для руководителей",
};

export default function SpeechSummarizer() {
  const [file, setFile] = useState<File | null>(null);
  const [language, setLanguage] = useState("ru");
  
  // Тип суммаризации теперь называется summaryType, чтобы соответствовать API
  const [summaryType, setSummaryType] = useState<keyof typeof SUMMARY_TYPES>("brief");

  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("Обработка нейросетью...");
  const [transcript, setTranscript] = useState("");
  const [summary, setSummary] = useState("");
  const [activeTab, setActiveTab] = useState<"transcript" | "summary">("summary");
  const [copied, setCopied] = useState(false);
  
  // НОВОЕ: Состояние для хранения доступных типов с сервера
  const [availableSummaryTypes, setAvailableSummaryTypes] = useState<{[key: string]: {id: string, name: string}}>({});

  useEffect(() => {
    const fetchSummaryTypes = async () => {
      try {
        const res = await fetch("http://localhost:5000/api/summarization-types");
        if (!res.ok) return;
        const data = await res.json();
        setAvailableSummaryTypes(data);
        // Устанавливаем первый доступный тип как дефолтный
        const firstType = Object.keys(data)[0];
        if(firstType) {
          setSummaryType(firstType as keyof typeof SUMMARY_TYPES);
        }
      } catch (error) {
        console.error("Не удалось загрузить типы суммаризации", error);
      }
    };
    fetchSummaryTypes();
  }, []);


  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setTranscript("");
      setSummary("");
    }
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setTranscript("");
    setSummary("");
    setActiveTab("summary");
    setLoadingMessage("1/3: Загрузка файла...");

    try {
      // --- ЭТАП 1: Отправка файла и получение ID задачи ---
      const formData = new FormData();
      formData.append("audio_file", file);
      formData.append("language", language);
      // Отправляем тип саммари с правильным именем 'summary_type'
      formData.append("summary_type", summaryType);

      const processRes = await fetch("http://localhost:5000/api/process", {
        method: "POST",
        body: formData,
      });

      if (!processRes.ok) throw new Error("Ошибка при отправке файла на обработку");
      const processData = await processRes.json();
      const { task_id } = processData;
      if (!task_id) throw new Error("Не удалось получить ID задачи от сервера");

      // --- ЭТАП 2: Опрос сервера до готовности результата ---
      setLoadingMessage("2/3: Идет транскрибация...");
      
      while (true) {
        const statusRes = await fetch(`http://localhost:5000/api/status/${task_id}`);
        const statusData = await statusRes.json();

        if (statusData.status === 'completed') break; // Задача готова, выходим из цикла
        if (statusData.status === 'failed') throw new Error('Ошибка обработки файла на сервере.');
        
        await new Promise(resolve => setTimeout(resolve, 3000)); // Ждем 3 секунды
      }

      // --- ЭТАП 3: Запрос и отображение финального результата ---
      setLoadingMessage("3/3: Получение результата...");
      const resultRes = await fetch(`http://localhost:5000/api/result/${task_id}`);
      if (!resultRes.ok) throw new Error("Ошибка при получении финального результата");

      const resultData = await resultRes.json();

      // Отображаем данные из правильных полей ответа бэкенда
      setTranscript(resultData.text || "Текст не получен.");
      
      if (resultData.summary_data && !resultData.summary_data.error) {
        setSummary(resultData.summary_data.summary || "Краткое содержание не получено.");
      } else {
        const errorMessage = resultData.summary_data?.error || "Ошибка при получении краткого содержания.";
        setSummary(`Ошибка: ${errorMessage}`);
      }

    } catch (err: any) {
      console.error(err);
      alert(err.message || "Произошла неизвестная ошибка");
      setSummary(`Произошла ошибка: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-slate-900 via-gray-900 to-black flex items-center justify-center p-4 md:p-8 text-white">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-2xl"
      >
        <Card className="shadow-2xl border border-white/10 bg-black/40 backdrop-blur-xl rounded-3xl overflow-hidden ring-1 ring-white/5">
          <CardContent className="p-8 md:p-10 space-y-8">
            {/* ... Header остается без изменений ... */}
            <div className="text-center space-y-3">
              <div className="inline-flex items-center justify-center p-3 bg-white/5 rounded-2xl mb-2 border border-white/10">
                <Sparkles className="w-6 h-6 text-indigo-400" />
              </div>
              <h1 className="text-3xl font-bold text-white tracking-tight">
                ИИ Транскрибация и Суммаризация Речи
              </h1>
              <p className="text-gray-400">
                Преобразуем голос в текст с настройкой детализации
              </p>
            </div>
            {/* Controls Group */}
            <div className="space-y-4">
              {/* Row 1: Language & Summarization Type */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* ... Language Selector остается без изменений ... */}
                <div className="relative group">
                  <Languages className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 group-hover:text-indigo-400 transition-colors w-5 h-5" />
                  <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-gray-200 font-medium focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all appearance-none cursor-pointer hover:bg-white/10"
                  >
                    <option className="bg-gray-900" value="ru">🇷🇺 Русский</option>
                    <option className="bg-gray-900" value="en">🇺🇸 English</option>
                    <option className="bg-gray-900" value="es">🇪🇸 Español</option>
                    <option className="bg-gray-900" value="de">🇩🇪 Deutsch</option>
                    <option className="bg-gray-900" value="fr">🇫🇷 Français</option>
                  </select>
                </div>

                {/* ============================================================================ */}
                {/* ОБНОВЛЕННЫЙ СЕЛЕКТОР ТИПА СУММАРИЗАЦИИ (ЗАГРУЖАЕТ ДАННЫЕ С СЕРВЕРА) */}
                {/* ============================================================================ */}
                <div className="relative group">
                  <Shrink className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 group-hover:text-indigo-400 transition-colors w-5 h-5" />
                  <select
                    value={summaryType}
                    onChange={(e) => setSummaryType(e.target.value as keyof typeof SUMMARY_TYPES)}
                    className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-gray-200 font-medium focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all appearance-none cursor-pointer hover:bg-white/10"
                  >
                    {Object.keys(availableSummaryTypes).length > 0 ? (
                      Object.entries(availableSummaryTypes).map(([key, value]) => (
                        <option key={key} className="bg-gray-900" value={value.id}>
                          {SUMMARY_TYPES[value.id as keyof typeof SUMMARY_TYPES] || value.name}
                        </option>
                      ))
                    ) : (
                      <option className="bg-gray-900">Загрузка типов...</option>
                    )}
                  </select>
                </div>
              </div>

              {/* ... File Upload остается без изменений ... */}
              <label className={`relative flex flex-col items-center justify-center w-full py-8 border-2 border-dashed rounded-xl cursor-pointer transition-all duration-300 ${file ? "border-green-500/50 bg-green-500/10" : "border-white/10 hover:border-indigo-400/50 hover:bg-white/5"}`}>
                <input type="file" accept="audio/*" onChange={handleFileChange} className="hidden" />
                {file ? (
                  <div className="flex items-center gap-3 text-green-400 animate-in fade-in zoom-in duration-300">
                    <FileAudio className="w-6 h-6" /><span className="font-semibold truncate max-w-[200px]">{file.name}</span><CheckCircle2 className="w-5 h-5" />
                  </div>
                ) : (
                  <div className="flex flex-col items-center text-gray-400">
                    <Upload className="w-8 h-8 mb-2 text-indigo-400" /><span className="text-sm font-medium">Загрузите аудиофайл</span>
                  </div>
                )}
              </label>
            </div>

            {/* ============================================================================ */}
            {/* ОБНОВЛЕННАЯ КНОПКА С ДИНАМИЧЕСКИМ ТЕКСТОМ ЗАГРУЗКИ */}
            {/* ============================================================================ */}
            <Button
              onClick={handleUpload}
              disabled={!file || loading}
              className={`w-full py-6 text-lg font-semibold rounded-xl shadow-lg transition-all duration-300 border border-white/10 ${loading ? "bg-white/5 text-gray-500 cursor-not-allowed" : "bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white hover:shadow-indigo-500/20"}`}
            >
              {loading ? (
                <div className="flex items-center gap-2">
                  <Loader2 className="animate-spin h-5 w-5" />
                  <span>{loadingMessage}</span>
                </div>
              ) : (
                <div className="flex items-center gap-2"><span>🚀 Запустить анализ</span></div>
              )}
            </Button>

            {/* ... Results (табы и контент) остаются без изменений ... */}
            <AnimatePresence mode="wait">
              {(transcript || summary) && (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} transition={{ duration: 0.4 }} className="mt-8 space-y-4">
                  <div className="flex p-1 bg-black/40 border border-white/10 rounded-xl">
                    <button onClick={() => setActiveTab("summary")} className={`flex-1 py-2 text-sm font-semibold rounded-lg transition-all ${activeTab === "summary" ? "bg-indigo-600 text-white shadow-sm" : "text-gray-400 hover:text-gray-200"}`}>💡 Суммаризация</button>
                    <button onClick={() => setActiveTab("transcript")} className={`flex-1 py-2 text-sm font-semibold rounded-lg transition-all ${activeTab === "transcript" ? "bg-indigo-600 text-white shadow-sm" : "text-gray-400 hover:text-gray-200"}`}>📝 Полный текст</button>
                  </div>
                  <div className="relative group">
                    <div className="absolute top-4 right-4 z-10 opacity-0 group-hover:opacity-100 transition-opacity">
                      <Button size="sm" variant="secondary" className="h-8 w-8 p-0 bg-white/10 backdrop-blur border border-white/10 hover:bg-white/20 text-white" onClick={() => handleCopy(activeTab === "summary" ? summary : transcript)}>
                        {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                      </Button>
                    </div>
                    <motion.div key={activeTab} initial={{opacity: 0, x: activeTab === "summary" ? -20 : 20}} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.3 }} className="bg-black/30 border border-white/10 p-6 rounded-2xl min-h-[150px] max-h-[400px] overflow-y-auto custom-scrollbar">
                      <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">{activeTab === "summary" ? summary : transcript}</p>
                    </motion.div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
