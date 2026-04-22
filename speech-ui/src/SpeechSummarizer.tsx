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
  Search,
  Send,
  Cpu,
  BookOpen
} from "lucide-react";

const SUMMARY_TYPES = {
  brief: "⚡ Кратко",
  detailed: "📄 Подробно",
  structured: "📑 Структурированно",
  bullet_points: "🔑 Ключевые пункты",
  executive: "👔 Для руководителей",
};

const TOPICS = {
  general: { name: "Общая", icon: <BookOpen className="w-3 h-3" /> },
  informatics: { name: "Информатика", icon: <Cpu className="w-3 h-3" /> },
};

export default function SpeechSummarizer() {
  const [file, setFile] = useState<File | null>(null);
  const [language, setLanguage] = useState("ru");
  const [summaryType, setSummaryType] = useState<keyof typeof SUMMARY_TYPES>("brief");
  const [topic, setTopic] = useState<keyof typeof TOPICS>("general");

  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("Обработка нейросетью...");
  const [transcript, setTranscript] = useState("");
  const [summary, setSummary] = useState("");
  const [activeTab, setActiveTab] = useState<"transcript" | "summary">("summary");
  const [copied, setCopied] = useState(false);
  
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [isAsking, setIsAsking] = useState(false);

  const [availableSummaryTypes, setAvailableSummaryTypes] = useState<{[key: string]: {id: string, name: string}}>({});

  useEffect(() => {
    const fetchSummaryTypes = async () => {
      try {
        const res = await fetch("http://localhost:5000/api/summarization-types");
        if (!res.ok) return;
        const data = await res.json();
        setAvailableSummaryTypes(data);
        const firstType = Object.keys(data)[0];
        if(firstType) setSummaryType(firstType as keyof typeof SUMMARY_TYPES);
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
      setAnswer("");
    }
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleAsk = async () => {
    if (!transcript) {
      alert("Сначала загрузите и обработайте аудиофайл!");
      return;
    }
    if (!question.trim()) return;
    setIsAsking(true);
    try {
      const res = await fetch("http://localhost:5000/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: transcript, question: question }),
      });
      const data = await res.json();
      setAnswer(data.answer || data.error);
    } catch (err) {
      alert("Ошибка связи с сервером");
    } finally {
      setIsAsking(false);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setTranscript("");
    setSummary("");
    setAnswer("");
    setActiveTab("summary");
    setLoadingMessage("1/3: Загрузка файла...");

    try {
      const formData = new FormData();
      formData.append("audio_file", file);
      formData.append("language", language);
      formData.append("compression_level", summaryType);
      formData.append("topic", topic);

      const processRes = await fetch("http://localhost:5000/api/process", {
        method: "POST",
        body: formData,
      });

      if (!processRes.ok) throw new Error("Ошибка при отправке файла");
      const processData = await processRes.json();
      const { task_id } = processData;

      setLoadingMessage("2/3: Идет транскрибация...");
      while (true) {
        const statusRes = await fetch(`http://localhost:5000/api/status/${task_id}`);
        const statusData = await statusRes.json();
        if (statusData.status === 'completed') break;
        if (statusData.status === 'failed') throw new Error('Ошибка обработки на сервере');
        await new Promise(resolve => setTimeout(resolve, 3000));
      }

      setLoadingMessage("3/3: Получение результата...");
      const resultRes = await fetch(`http://localhost:5000/api/result/${task_id}`);
      const resultData = await resultRes.json();

      setTranscript(resultData.text || "Текст не получен.");
      if (resultData.summary_data && !resultData.summary_data.error) {
        setSummary(resultData.summary_data.summary);
      } else {
        setSummary(`Ошибка: ${resultData.summary_data?.error}`);
      }
    } catch (err: any) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-slate-900 via-gray-900 to-black flex items-center justify-center p-4 md:p-8 text-white font-sans">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-2xl">
        <Card className="shadow-2xl border border-white/10 bg-black/40 backdrop-blur-xl rounded-3xl overflow-hidden">
          <CardContent className="p-8 md:p-10 space-y-8">
            
            {/* Header */}
            <div className="text-center space-y-3">
              <div className="inline-flex items-center justify-center p-3 bg-white/5 rounded-2xl mb-2 border border-white/10">
                <Sparkles className="w-6 h-6 text-indigo-400" />
              </div>
              <h1 className="text-3xl font-bold text-white tracking-tight">ИИ Анализатор Речи</h1>
              <p className="text-gray-400 text-sm">Персонализированная обработка под вашу сферу деятельности</p>
            </div>

            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Language Selection */}
                <div className="space-y-3">
                  <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-2">
                    <Languages className="w-4 h-4 text-indigo-400" /> Язык аудио:
                  </label>
                  <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-gray-200 outline-none hover:bg-white/10 transition-all appearance-none cursor-pointer"
                  >
                    <option className="bg-gray-900" value="ru">🇷🇺 Русский</option>
                    <option className="bg-gray-900" value="en">🇺🇸 English</option>
                    <option className="bg-gray-900" value="de">🇩🇪 Deutsch</option>
                  </select>
                </div>

                {/* Topic Selection (НОВОЕ) */}
                <div className="space-y-3">
                  <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-2">
                    <Cpu className="w-4 h-4 text-indigo-400" /> Тема (Domain):
                  </label>
                  <div className="flex gap-2">
                    {Object.entries(TOPICS).map(([id, info]) => (
                      <button
                        key={id}
                        type="button"
                        onClick={() => setTopic(id as any)}
                        className={`flex-1 flex items-center justify-center gap-2 px-3 py-3 rounded-xl text-xs font-bold border transition-all ${
                          topic === id
                            ? "bg-indigo-600 border-indigo-500 text-white shadow-lg shadow-indigo-500/20"
                            : "bg-white/5 border-white/10 text-gray-400 hover:bg-white/10"
                        }`}
                      >
                        {info.icon} {info.name}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Summary Style Buttons */}
              <div className="space-y-3">
                <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider flex items-center gap-2">
                  <Shrink className="w-4 h-4 text-indigo-400" /> Стиль суммаризации:
                </label>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(SUMMARY_TYPES).map(([id, name]) => (
                    <button
                      key={id}
                      type="button"
                      onClick={() => setSummaryType(id as any)}
                      className={`px-4 py-2 rounded-xl text-xs font-medium border transition-all ${
                        summaryType === id
                          ? "bg-indigo-600 border-indigo-500 text-white shadow-lg"
                          : "bg-white/5 border-white/10 text-gray-400 hover:bg-white/10"
                      }`}
                    >
                      {name}
                    </button>
                  ))}
                </div>
              </div>

              {/* File Upload */}
              <label className={`relative flex flex-col items-center justify-center w-full py-8 border-2 border-dashed rounded-xl cursor-pointer transition-all ${file ? "border-green-500/50 bg-green-500/10" : "border-white/10 hover:border-indigo-400/50"}`}>
                <input type="file" accept=".mp3, .m4a, .ogg, .wav" onChange={handleFileChange} className="hidden" />
                {file ? (
                  <div className="flex items-center gap-3 text-green-400">
                    <FileAudio className="w-6 h-6" /><span className="font-semibold truncate max-w-[200px]">{file.name}</span><CheckCircle2 className="w-5 h-5" />
                  </div>
                ) : (
                  <div className="flex flex-col items-center text-center text-gray-400">
                    <Upload className="w-8 h-8 mb-2 text-indigo-400" />
                    <span className="text-sm font-medium">Загрузите аудио</span>
                    <span className="text-xs text-gray-500 mt-1 uppercase tracking-widest">MP3, M4A, OGG, WAV</span>
                  </div>
                )}
              </label>
            </div>

            <Button
              onClick={handleUpload}
              disabled={!file || loading}
              className={`w-full py-6 text-lg font-semibold rounded-xl transition-all ${loading ? "bg-white/5 shadow-none" : "bg-gradient-to-r from-indigo-600 to-purple-600 hover:scale-[1.01] shadow-xl shadow-indigo-500/20"}`}
            >
              {loading ? <div className="flex items-center gap-2"><Loader2 className="animate-spin" /><span>{loadingMessage}</span></div> : "🚀 Запустить анализ"}
            </Button>

            {/* Results Tabs */}
            <AnimatePresence>
              {(transcript || summary) && (
                <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} className="space-y-4">
                  <div className="flex p-1 bg-black/40 border border-white/10 rounded-xl">
                    <button onClick={() => setActiveTab("summary")} className={`flex-1 py-2 text-sm font-semibold rounded-lg transition-colors ${activeTab === "summary" ? "bg-indigo-600 text-white" : "text-gray-400"}`}>💡 Результат ИИ</button>
                    <button onClick={() => setActiveTab("transcript")} className={`flex-1 py-2 text-sm font-semibold rounded-lg transition-colors ${activeTab === "transcript" ? "bg-indigo-600 text-white" : "text-gray-400"}`}>📝 Полный текст</button>
                  </div>
                  <div className="relative bg-black/30 border border-white/10 p-6 rounded-2xl max-h-[300px] overflow-y-auto custom-scrollbar">
                    <Button size="sm" className="absolute top-2 right-2 bg-white/10 hover:bg-white/20 h-8 w-8 p-0" onClick={() => handleCopy(activeTab === "summary" ? summary : transcript)}>
                      {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4 text-white" />}
                    </Button>
                    <p className="text-gray-300 text-sm leading-relaxed whitespace-pre-wrap">{activeTab === "summary" ? summary : transcript}</p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* AI Assistant Chat - ВИДЕН ВСЕГДА */}
            <div className="pt-8 border-t border-white/10 space-y-4">
              <div className="flex items-center gap-2 text-indigo-400 font-bold text-xs uppercase tracking-widest">
                <Search className="w-4 h-4" /> AI Поиск по содержанию
              </div>
              <div className="relative">
                <input
                  type="text"
                  placeholder={transcript ? "Спросите: 'О чем шла речь?' или 'Найди цифры'..." : "Сначала загрузите аудио для анализа..."}
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleAsk()}
                  className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-4 text-sm text-white placeholder:text-gray-400 focus:ring-2 focus:ring-indigo-500 focus:bg-white/15 outline-none transition-all"
                />
                <Button 
                  onClick={handleAsk} 
                  disabled={isAsking || !question.trim()} 
                  className="absolute right-2 top-1/2 -translate-y-1/2 h-10 w-10 p-0 bg-indigo-600 hover:bg-indigo-500 shadow-lg"
                >
                  {isAsking ? <Loader2 className="animate-spin w-5 h-5" /> : <Send className="w-5 h-5" />}
                </Button>
              </div>
              {answer && (
                <motion.div initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }} className="bg-indigo-500/20 border border-indigo-500/30 p-5 rounded-2xl text-sm text-gray-100 shadow-inner">
                  <div className="flex gap-3">
                    <Sparkles className="w-5 h-5 text-indigo-400 flex-shrink-0" />
                    <p className="leading-relaxed"><span className="text-indigo-400 font-bold uppercase text-[10px] block mb-1">Ответ ассистента:</span>{answer}</p>
                  </div>
                </motion.div>
              )}
            </div>

          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
