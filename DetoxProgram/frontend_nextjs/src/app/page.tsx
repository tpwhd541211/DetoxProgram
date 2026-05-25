"use client";

import { useState, useEffect } from "react";
import { UploadCloud, Bell, Calendar, Home, Activity, PieChart as PieChartIcon, Network, Target, Clock, Settings, CheckCircle2, Circle } from "lucide-react";
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, PieChart as RePieChart, Pie, Cell, LineChart, Line, BarChart, Bar } from 'recharts';

const DSAO_TYPES: Record<string, {
  name: string;
  alias: string;
  desc: string;
  strengths: string[];
  risks: string[];
  detox: string;
  character: string;
}> = {
  "DWSF": {
    name: "주도적 고자극 확산형",
    alias: "도파민 탐험가",
    desc: "직접 검색하거나 스스로 관심사를 찾아가며 다양한 주제를 소비하지만, 빠르고 자극적인 콘텐츠에 강하게 반응하는 유형입니다.",
    strengths: ["트렌드 감지 속도가 빠름", "다양한 분야에 호기심이 많음", "스스로 검색하는 주도성이 있음"],
    risks: ["자극적인 제목과 썸네일에 쉽게 끌림", "깊이 있는 검토보다 빠른 소비가 많아질 수 있음", "관심사가 넓지만 정리가 약할 수 있음"],
    detox: "자극적인 콘텐츠를 본 뒤 같은 주제의 차분한 해설 콘텐츠 1개를 추가로 보기",
    character: "🧭"
  },
  "DWSL": {
    name: "주도적 고자극 관찰형",
    alias: "마라맛 큐레이터",
    desc: "직접 다양한 주제를 찾아보면서, 논쟁적이거나 감정적으로 강한 콘텐츠를 긴 시간 소비하는 유형입니다.",
    strengths: ["다양한 이슈를 능동적으로 탐색함", "긴 콘텐츠도 집중해서 볼 수 있음", "사회적 이슈나 논쟁 구조를 빠르게 파악함"],
    risks: ["갈등형 콘텐츠에 오래 노출될 수 있음", "감정적으로 강한 주장에 영향을 받을 수 있음", "균형 자료보다 자극적 자료를 우선할 수 있음"],
    detox: "논쟁형 콘텐츠를 본 뒤 중립적인 배경 설명이나 통계 자료를 함께 확인하기",
    character: "🌶️"
  },
  "DWMF": {
    name: "주도적 안정 확산형",
    alias: "지식 스낵 탐색가",
    desc: "직접 다양한 주제를 찾아보지만, 짧고 부담 없는 안정적인 콘텐츠를 선호하는 유형입니다.",
    strengths: ["다양한 정보를 부담 없이 접함", "자극보다 실용적 정보에 관심이 많음", "직접 검색하는 능동성이 있음"],
    risks: ["얕은 이해에서 멈출 수 있음", "긴 자료를 피할 가능성이 있음", "정보가 많지만 체계화가 부족할 수 있음"],
    detox: "짧은 요약 콘텐츠를 본 뒤 원문이나 긴 설명 자료 1개를 연결해서 보기",
    character: "🍿"
  },
  "DWML": {
    name: "주도적 안정 확장형",
    alias: "지식 탐구형 선장",
    desc: "직접 검색하고 다양한 분야를 넓게 보며, 안정적이고 긴 호흡의 콘텐츠도 잘 소비하는 유형입니다.",
    strengths: ["알고리즘 추천에만 의존하지 않음", "다양한 주제를 깊게 탐색함", "학습형 콘텐츠와 긴 자료에 강함"],
    risks: ["관심 범위가 너무 넓어 정리가 어려울 수 있음", "지나치게 많은 정보를 모으기만 할 수 있음", "실행보다 탐색에 머무를 수 있음"],
    detox: "소비한 콘텐츠를 주제별로 정리하고 핵심 관점 3개를 기록하기",
    character: "⛵"
  },
  "DNSF": {
    name: "주도적 고자극 집중형",
    alias: "마라맛 쇼츠 광부",
    desc: "특정 관심 주제를 직접 찾아보며, 자극적이고 짧은 콘텐츠를 반복적으로 소비하는 유형입니다.",
    strengths: ["관심 주제를 빠르게 파고듦", "직접 찾고 비교하는 힘이 있음", "특정 이슈의 흐름을 빠르게 따라감"],
    risks: ["비슷한 자극 콘텐츠를 반복 소비할 수 있음", "숏폼 중심이라 맥락 이해가 부족해질 수 있음", "한 주제에 과몰입할 수 있음"],
    detox: "반복 시청 중인 주제에서 반대 관점 키워드 2개를 직접 검색하기",
    character: "⛏️"
  },
  "DNSL": {
    name: "주도적 고자극 몰입형",
    alias: "심연의 마라맛 광부",
    desc: "특정 자극적 주제를 직접 검색해 긴 영상까지 깊게 파고드는 유형입니다.",
    strengths: ["특정 주제에 대한 몰입력이 강함", "긴 콘텐츠도 끝까지 볼 수 있음", "스스로 자료를 찾아보는 능력이 있음"],
    risks: ["자극적 주제에 장시간 머물 수 있음", "시야가 한 방향으로 좁아질 수 있음", "감정 피로와 불안이 커질 수 있음"],
    detox: "같은 주제의 원인 분석, 통계, 제도적 배경 콘텐츠를 함께 보기",
    character: "🌋"
  },
  "DNMF": {
    name: "주도적 안정 집중형",
    alias: "조용한 기술 덕후",
    desc: "특정 분야를 직접 찾아보며, 짧고 안정적인 학습형 콘텐츠를 반복 소비하는 유형입니다.",
    strengths: ["특정 분야 학습에 집중력이 있음", "자극보다 실용 정보에 강함", "직접 찾아보며 반복 학습함"],
    risks: ["짧은 팁 중심으로 머물 수 있음", "깊은 원리 이해가 부족할 수 있음", "관심 분야가 좁아질 수 있음"],
    detox: "짧은 학습 콘텐츠를 공식 문서, 긴 강의, 실습 과제로 연결하기",
    character: "🔧"
  },
  "DNML": {
    name: "주도적 안정 몰입형",
    alias: "한우물 연구자",
    desc: "특정 주제를 직접 찾아 깊고 오래 파고드는 안정적 몰입형입니다.",
    strengths: ["깊이 있는 학습에 강함", "긴 콘텐츠를 안정적으로 소화함", "전문성 축적에 유리함"],
    risks: ["관심 분야가 좁아질 수 있음", "새로운 관점을 놓칠 수 있음", "한 분야의 정보만 과도하게 소비할 수 있음"],
    detox: "주 관심사와 인접한 다른 분야 콘텐츠를 주 1개 이상 추가하기",
    character: "🔬"
  },
  "PWSF": {
    name: "추천형 고자극 확산형",
    alias: "알고리즘 롤러코스터",
    desc: "추천 피드를 따라 다양한 자극적 숏폼 콘텐츠를 빠르게 소비하는 유형입니다.",
    strengths: ["트렌드를 빠르게 접함", "다양한 이슈를 넓게 봄", "짧은 시간에 많은 콘텐츠를 소비함"],
    risks: ["알고리즘 피드에 쉽게 끌림", "감정 자극이 누적될 수 있음", "깊은 검토 없이 다음 콘텐츠로 넘어갈 수 있음"],
    detox: "쇼츠 시청 시간을 제한하고, 추천 피드 대신 직접 검색 1회를 추가하기",
    character: "🎢"
  },
  "PWSL": {
    name: "추천형 고자극 관람형",
    alias: "자동재생 극장 관객",
    desc: "추천 알고리즘이 띄워주는 다양한 자극적 콘텐츠를 긴 호흡으로 이어 보는 유형입니다.",
    strengths: ["다양한 콘텐츠를 오래 볼 수 있음", "추천 흐름을 통해 새로운 주제를 접함", "긴 콘텐츠도 소비 가능함"],
    risks: ["자동재생에 의해 수동 소비가 길어질 수 있음", "자극적 이슈에 감정적으로 끌릴 수 있음", "선택권이 알고리즘에 넘어갈 수 있음"],
    detox: "자동재생을 끄고 30분마다 지금 보는 주제가 필요한지 점검하기",
    character: "🎬"
  },
  "PWMF": {
    name: "추천형 안정 확산형",
    alias: "유튜브 유람선 탑승객",
    desc: "추천 피드가 보여주는 짧고 안정적인 콘텐츠를 가볍게 탐색하는 유형입니다.",
    strengths: ["부담 없이 다양한 콘텐츠를 접함", "자극적 콘텐츠에 과하게 끌리지 않음", "짧은 정보 습득에 유리함"],
    risks: ["무의식적 킬링타임이 길어질 수 있음", "깊은 학습으로 이어지지 않을 수 있음", "추천 피드에 수동적으로 머물 수 있음"],
    detox: "추천 숏폼 시청 후 저장하거나 기록할 가치가 있는 정보만 남기기",
    character: "🚢"
  },
  "PWML": {
    name: "추천형 안정 관람형",
    alias: "편안한 자동재생러",
    desc: "추천 피드의 안정적이고 긴 콘텐츠를 오래 틀어두고 소비하는 유형입니다.",
    strengths: ["자극이 적은 콘텐츠를 선호함", "긴 콘텐츠도 편안하게 소비함", "배경지식이나 취미 콘텐츠에 친화적임"],
    risks: ["자동재생으로 시간이 길어질 수 있음", "직접 탐색보다 추천에 의존할 수 있음", "목적 없는 시청이 늘어날 수 있음"],
    detox: "추천 영상 3개 중 1개는 직접 검색한 영상으로 바꾸기",
    character: "🛋️"
  },
  "PNSF": {
    name: "추천형 고자극 집중형",
    alias: "알고리즘 도파민 루프",
    desc: "추천 피드 안에서 특정 자극 주제의 짧은 콘텐츠를 반복 소비하는 유형입니다.",
    strengths: ["관심 주제에 빠르게 반응함", "트렌드 변화에 민감함", "짧은 콘텐츠에서 핵심 자극을 빠르게 포착함"],
    risks: ["추천 피드에 의해 비슷한 자극이 반복 강화될 수 있음", "관점 다양성이 낮아질 수 있음", "짧은 영상 반복으로 시간 통제력이 약해질 수 있음"],
    detox: "추천 영상 3개를 본 뒤 직접 검색한 균형 콘텐츠 1개를 추가로 보기",
    character: "🔄"
  },
  "PNSL": {
    name: "추천형 고자극 몰입형",
    alias: "알고리즘 심연 정주행러",
    desc: "추천 알고리즘을 따라 특정 자극 주제의 긴 콘텐츠를 계속 파고드는 유형입니다.",
    strengths: ["특정 주제에 대한 몰입력이 있음", "긴 영상도 끝까지 볼 수 있음", "추천 흐름을 통해 관련 콘텐츠를 많이 접함"],
    risks: ["알고리즘이 비슷한 자극 주제를 계속 강화할 수 있음", "한쪽 관점에 오래 머물 수 있음", "감정 피로와 불안이 누적될 수 있음"],
    detox: "자극적 이슈를 본 뒤 사실 확인 자료와 다른 관점의 해설을 함께 보기",
    character: "🕳️"
  },
  "PNMF": {
    name: "추천형 안정 집중형",
    alias: "조용한 추천 루틴러",
    desc: "추천 피드 안에서 특정 안정적 주제의 짧은 콘텐츠를 반복 소비하는 유형입니다.",
    strengths: ["안정적인 관심 루틴이 있음", "자극성 낮은 콘텐츠를 선호함", "짧은 실용 정보를 반복적으로 얻음"],
    risks: ["추천 피드 안에서만 관심사가 반복될 수 있음", "직접 탐색이 줄어들 수 있음", "짧은 정보 소비에서 실제 행동으로 이어지지 않을 수 있음"],
    detox: "반복 소비 중인 주제에서 실천 과제 1개를 정해 실제 행동으로 연결하기",
    character: "📅"
  },
  "PNML": {
    name: "추천형 안정 몰입형",
    alias: "자동재생 한우물러",
    desc: "추천 알고리즘이 이어주는 특정 안정적 롱폼 콘텐츠를 오래 소비하는 유형입니다.",
    strengths: ["긴 콘텐츠를 안정적으로 소비함", "특정 관심사에 꾸준히 몰입함", "자극성이 낮아 피로감이 적음"],
    risks: ["직접 선택보다 추천 흐름에 의존할 수 있음", "비슷한 콘텐츠만 계속 볼 수 있음", "시청 시간이 길어질 수 있음"],
    detox: "추천 정주행 후 직접 검색으로 다음 학습 주제를 선택하기",
    character: "🪵"
  }
};

const getDsaoInfo = (code: string) => {
  const defaultInfo = {
    name: "추천형 고자극 집중형",
    alias: "알고리즘 도파민 루프",
    desc: "추천 피드 안에서 특정 자극 주제의 짧은 콘텐츠를 반복 소비하는 유형입니다.",
    strengths: ["관심 주제에 빠르게 반응함", "트렌드 변화에 민감함", "짧은 콘텐츠에서 핵심 자극을 빠르게 포착함"],
    risks: ["추천 피드에 의해 비슷한 자극이 반복 강화될 수 있음", "관점 다양성이 낮아질 수 있음", "짧은 영상 반복으로 시간 통제력이 약해질 수 있음"],
    detox: "추천 영상 3개를 본 뒤 직접 검색한 균형 콘텐츠 1개를 추가로 보기",
    character: "🔄"
  };
  const key = code ? code.trim().toUpperCase() : "PNSF";
  return DSAO_TYPES[key] || defaultInfo;
};

export default function DashboardLayout() {
  // Navigation & Wizard Steps
  const [step, setStep] = useState<"consent" | "survey" | "upload" | "loading" | "dashboard">("consent");
  const [activeTab, setActiveTab] = useState<"dashboard" | "realtime" | "persona" | "graph" | "guide" | "contents">("dashboard");

  // Survey state (Self-Assessment Questionnaire)
  const [surveyData, setSurveyData] = useState({ div: 50, sta: 50, ini: 50, ope: 50 });

  // File Upload states
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  // Backend response states
  const [datasetId, setDatasetId] = useState<string | null>(null);
  const [scores, setScores] = useState<any>(null);
  const [report, setReport] = useState<any>(null);
  const [realtimeData, setRealtimeData] = useState<any[]>([]);
  const [personaData, setPersonaData] = useState<any>(null);
  const [graphData, setGraphData] = useState<any>(null);
  const [guideData, setGuideData] = useState<any>(null);
  const [contents, setContents] = useState<any>(null);

  // Interactivity states
  const [selectedNode, setSelectedNode] = useState<any | null>(null);
  const [completedMissions, setCompletedMissions] = useState<Set<number>>(new Set());
  const [activeCourse, setActiveCourse] = useState<3 | 7>(3);

  // Load backend data if datasetId is set
  const fetchDashboardData = async (id: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/dashboard/${id}`);
      if (!res.ok) throw new Error("Dashboard API error");
      const data = await res.json();
      setScores(data.scores);
      setReport(data.report);
      setContents(data.contents);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchTabDetails = async () => {
    try {
      const rtRes = await fetch("http://localhost:8000/api/realtime");
      const rtData = await rtRes.json();
      setRealtimeData(rtData.today_trend || []);

      const pRes = await fetch("http://localhost:8000/api/persona");
      const pData = await pRes.json();
      setPersonaData(pData);

      const gRes = await fetch("http://localhost:8000/api/graph");
      const gData = await gRes.json();
      setGraphData(gData);

      const guRes = await fetch("http://localhost:8000/api/guide");
      const guData = await guRes.json();
      setGuideData(guData);
    } catch (e) {
      console.error("Error loading tab details, using fallback:", e);
    }
  };

  // File drag & drop triggers
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.name.endsWith('.json') || file.name.endsWith('.html')) {
        setFile(file);
      } else {
        alert("JSON 또는 HTML 파일만 업로드할 수 있습니다.");
      }
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.name.endsWith('.json') || file.name.endsWith('.html')) {
        setFile(file);
      } else {
        alert("JSON 또는 HTML 파일만 업로드할 수 있습니다.");
      }
    }
  };

  // Perform backend analysis
  const handleStartAnalysis = async () => {
    if (!selectedFile) return;
    setStep("loading");
    setUploadProgress(10);

    const interval = setInterval(() => {
      setUploadProgress(prev => {
        const next = prev + Math.floor(Math.random() * 15) + 5;
        return next > 90 ? 90 : next;
      });
    }, 200);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const res = await fetch("http://localhost:8000/api/upload/", {
        method: "POST",
        body: formData
      });

      if (!res.ok) throw new Error("Backend upload failed");
      const uploadResult = await res.json();
      const id = uploadResult.dataset_id;

      await fetchDashboardData(id);
      await fetchTabDetails();

      clearInterval(interval);
      setUploadProgress(100);

      setTimeout(() => {
        setDatasetId(id);
        setStep("dashboard");
        setActiveTab("dashboard");
      }, 500);
    } catch (e) {
      console.error(e);
      clearInterval(interval);
      setUploadProgress(100);
      alert("⚠️ 파이썬 서버(/api/upload)가 응답하지 않아 오프라인 모드(더미 데이터)로 전환합니다.");

      setTimeout(() => {
        // Fallback demo data configuration
        setDatasetId("demo-dataset");
        setScores({
          diversity: 38.0,
          stability: 76.0,
          proactivity: 56.0,
          openness: 41.0,
          manipulation_index: 72.0,
          persona_type: "PNSF"
        });
        setReport({
          overall_summary: "특정 분야에 과도하게 매몰되어 다른 관점을 수용하지 못할 위험(확증편향)이 큽니다.",
          axis_comments: [
            "다양성 점수는 38/100으로 특정 장르에 지나치게 쏠림 현상이 관찰됩니다.",
            "안정성 점수는 76/100으로 비교적 안전한 영상을 시청하고 있습니다.",
            "주도성 점수는 56/100으로 추천 영상을 주로 소비합니다.",
            "개방성 점수는 41/100으로 고정된 취향을 가집니다."
          ],
          key_findings: "IT/테크 중심의 편향 시청이 관찰됩니다.",
          recommendations: "역방향 쿼리를 사용한 적극적 탐색이 필요합니다.",
          caution_notes: "알고리즘 필터 버블 주의",
          missions: [
            { mission_type: "역방향 쿼리", description: "인공지능의 윤리적 문제와 규제 필요성 영상을 검색하여 10분 이상 시청합니다.", success_condition: "관련 검색어로 동영상 시청 완료" },
            { mission_type: "비구독 채널 탐색", description: "평소 전혀 구독하지 않는 경제 분야 인기 채널의 영상을 1개 시청합니다.", success_condition: "영상 시청 완료" },
            { mission_type: "숏폼 탈출", description: "오늘 하루 유튜브 숏츠 시청 시간을 30분 이내로 조절합니다.", success_condition: "숏츠 시청 제한 달성" }
          ]
        });
        setRealtimeData([
          { time: '09:00', dopamine: 40 },
          { time: '12:00', dopamine: 65 },
          { time: '15:00', dopamine: 85 },
          { time: '18:00', dopamine: 92 },
          { time: 'Now', dopamine: 45 }
        ]);
        setPersonaData({
          type: "PNSF",
          weakness: "특정 분야에 과도하게 매몰되어 다른 관점을 수용하지 못할 위험(확증편향)이 큽니다.",
          ai_scores: { div: 38, sta: 76, ini: 56, ope: 41 },
          history: [ { month: '1월', objectivity: 70 }, { month: '3월', objectivity: 65 }, { month: '5월', objectivity: 56 } ]
        });
        setGraphData({
          nodes: [
            { id: 1, label: "인공지능", group: "tech", size: 30 },
            { id: 2, label: "기술/IT", group: "tech", size: 25 },
            { id: 3, label: "경제/금융", group: "economy", size: 20 },
            { id: 4, label: "딥러닝", group: "tech", size: 15 },
            { id: 5, label: "챗GPT", group: "tech", size: 15 },
            { id: 6, label: "AI 윤리", group: "tech", size: 15 },
            { id: 7, label: "투자/주식", group: "economy", size: 15 },
            { id: 8, label: "글로벌 경제", group: "economy", size: 15 },
            { id: 9, label: "생산성", group: "self", size: 15 },
            { id: 10, label: "마인드셋", group: "self", size: 15 }
          ],
          edges: [
            { source: 1, target: 4 }, { source: 1, target: 5 }, { source: 1, target: 6 },
            { source: 1, target: 2 }, { source: 2, target: 9 }, { source: 2, target: 10 },
            { source: 1, target: 3 }, { source: 3, target: 7 }, { source: 3, target: 8 },
            { source: 2, target: 8 }
          ]
        });
        setGuideData({
          streak_days: 12,
          daily_missions: [
            { id: 1, task: "반대 성향 영상 1개 끝까지 시청", completed: true },
            { id: 2, task: "구독하지 않은 채널 영상 시청", completed: true },
            { id: 3, task: "숏폼 영상 30분 미만 시청", completed: false }
          ],
          streak_history: []
        });
        setContents({
          watch_history: [
            { id: 1, title: "인공지능 혁명과 인간 존엄성에 대한 철학적 성찰", channel_name: "인문학 명강의", watch_time: new Date().toISOString(), video_id: "", dopamine_tag: "🧘 저도파민/유익" },
            { id: 2, title: "[쇼츠] 롤 펜타킬 역대급 피지컬 순간 모음", channel_name: "게이머TV", watch_time: new Date().toISOString(), video_id: "", dopamine_tag: "⚡ 고도파민" },
            { id: 3, title: "글로벌 거시 경제 리스크 진단 및 자산 배분 전략", channel_name: "삼프로티비", watch_time: new Date().toISOString(), video_id: "", dopamine_tag: "🧘 저도파민/유익" },
            { id: 4, title: "경악을 금치 못하는 충격 폭로 실태 단독 보도", channel_name: "연예이슈뉴스", watch_time: new Date().toISOString(), video_id: "", dopamine_tag: "⚡ 고도파민" }
          ],
          top_channels: [
            { name: "게이머TV", count: 18, percentage: 38.0 },
            { name: "연예이슈뉴스", count: 12, percentage: 25.0 },
            { name: "삼프로티비", count: 9, percentage: 19.0 },
            { name: "인문학 명강의", count: 5, percentage: 10.0 },
            { name: "기타 채널", count: 4, percentage: 8.0 }
          ]
        });
        setStep("dashboard");
        setActiveTab("dashboard");
      }, 500);
    }
  };

  // Helper variables for Recharts mapping
  const mbtiData = [
    { subject: '주제 다양성(TDS)', A: scores?.tds || scores?.diversity || 38 },
    { subject: '출처 균형(SBS)', A: scores?.sbs || scores?.diversity || 50 },
    { subject: '감정 균형(EBS)', A: scores?.ebs || scores?.stability || 76 },
    { subject: '관점 개방(VOS)', A: scores?.vos || scores?.openness || 41 },
    { subject: '유해 안전(SMS)', A: scores?.sms || scores?.stability || 76 },
    { subject: '사용자 주도(UAS)', A: scores?.uas || scores?.proactivity || 56 }
  ];

  const timelineData = [
    { date: '04/20', score: 85 }, { date: '04/24', score: 90 }, { date: '04/29', score: 95 },
    { date: '05/04', score: 78 }, { date: '05/09', score: 90 }, { date: '05/13', score: 68 },
    { date: '05/18', score: 52 }, { date: '05/20', score: scores?.brs || scores?.manipulation_index || 72 }
  ];

  const barData = personaData?.history || [
    { month: '1월', objectivity: 70 }, { month: '3월', objectivity: 65 }, { month: '5월', objectivity: 56 }
  ];

  const getBrsStyle = (val: number) => {
    if (val < 20) return { color: "#10B981", textColor: "text-emerald-500", label: "안전" };
    if (val < 40) return { color: "#84CC16", textColor: "text-lime-500", label: "양호" };
    if (val < 60) return { color: "#F59E0B", textColor: "text-amber-500", label: "보통" };
    if (val < 80) return { color: "#F97316", textColor: "text-orange-500", label: "경고" };
    return { color: "#EF4444", textColor: "text-red-500", label: "위험" };
  };
  const currentBrs = scores?.brs || scores?.manipulation_index || 72;
  const brsInfo = getBrsStyle(currentBrs);
  const personaType = scores?.persona_type || "PNSF";
  const dsao = getDsaoInfo(personaType);

  // Calculated Gap logic (Mirror Therapy)
  const calculateGapWarning = () => {
    const aiScores = personaData?.ai_scores || { div: 38, sta: 76, ini: 56, ope: 41, tds: 38, sbs: 50, ebs: 76, vos: 41, sms: 76, uas: 56 };
    const gaps = [
      { name: '주제 다양성(TDS)', diff: surveyData.div - (aiScores.tds || aiScores.div || 38) },
      { name: '출처 균형(SBS)', diff: surveyData.div - (aiScores.sbs || aiScores.div || 50) },
      { name: '감정 균형(EBS)', diff: surveyData.sta - (aiScores.ebs || aiScores.sta || 76) },
      { name: '관점 개방(VOS)', diff: surveyData.ope - (aiScores.vos || aiScores.ope || 41) },
      { name: '유해 안전(SMS)', diff: surveyData.sta - (aiScores.sms || aiScores.sta || 76) },
      { name: '사용자 주도(UAS)', diff: surveyData.ini - (aiScores.uas || aiScores.ini || 56) }
    ];
    const maxGap = gaps.reduce((prev, curr) => (curr.diff > prev.diff) ? curr : prev);
    if (maxGap.diff > 20) {
      return `거울 치료: 본인은 스스로 [${maxGap.name}] 항목이 높다고 평가했지만, 실제 시청 기록 데이터는 현저히 낮습니다. 스스로 치우침 없이 본다고 믿었으나, 특정 영역만 반복 시청하고 있을 가능성이 매우 큽니다!`;
    } else {
      return "본인이 인지하는 시청 성향과 AI가 실제로 도출한 데이터 분석 결과가 상당히 가깝습니다.";
    }
  };

  // Recharts Multi-polygon Radar Data
  const comparisonRadarData = [
    { subject: '주제 다양성', A: surveyData.div, B: personaData?.ai_scores?.tds || personaData?.ai_scores?.div || 38 },
    { subject: '출처 균형', A: surveyData.div, B: personaData?.ai_scores?.sbs || personaData?.ai_scores?.div || 50 },
    { subject: '감정 균형', A: surveyData.sta, B: personaData?.ai_scores?.ebs || personaData?.ai_scores?.sta || 76 },
    { subject: '관점 개방', A: surveyData.ope, B: personaData?.ai_scores?.vos || personaData?.ai_scores?.ope || 41 },
    { subject: '유해 안전', A: surveyData.sta, B: personaData?.ai_scores?.sms || personaData?.ai_scores?.sta || 76 },
    { subject: '사용자 주도', A: surveyData.ini, B: personaData?.ai_scores?.uas || personaData?.ai_scores?.ini || 56 }
  ];

  // custom SVG graph rendering
  const renderSvgGraph = () => {
    if (!graphData || !graphData.nodes) return null;
    const nodes = graphData.nodes;
    const edges = graphData.edges || [];
    const width = 500;
    const height = 500;
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = 160;

    const positionedNodes = nodes.map((node: any, idx: number) => {
      if (idx === 0) {
        return { ...node, x: centerX, y: centerY };
      } else {
        const angle = ((idx - 1) / (nodes.length - 1)) * 2 * Math.PI;
        return {
          ...node,
          x: centerX + Math.cos(angle) * radius,
          y: centerY + Math.sin(angle) * radius
        };
      }
    });

    return (
      <svg className="w-full h-full max-w-[500px] mx-auto" viewBox={`0 0 ${width} ${height}`}>
        {edges.map((edge: any, index: number) => {
          const src = positionedNodes.find((n: any) => n.id === edge.source);
          const tgt = positionedNodes.find((n: any) => n.id === edge.target);
          if (!src || !tgt) return null;
          return (
            <line 
              key={`edge-${index}`}
              x1={src.x} y1={src.y}
              x2={tgt.x} y2={tgt.y}
              stroke="#CBD5E1"
              strokeWidth={edge.value ? Math.max(1, edge.value * 0.5) : 2}
            />
          );
        })}
        {positionedNodes.map((node: any) => {
          const color = node.group === 'tech' ? '#8B5CF6' : (node.group === 'economy' ? '#3B82F6' : '#10B981');
          const size = node.size || 15;
          return (
            <g key={`node-${node.id}`} className="group cursor-pointer" onClick={() => setSelectedNode(node)}>
              <circle
                cx={node.x} cy={node.y}
                r={size}
                fill={color}
                stroke="#FFFFFF"
                strokeWidth={2}
                className="transition-transform duration-200 hover:scale-125"
              />
              <text
                x={node.x} y={node.y + size + 14}
                textAnchor="middle"
                fill="#475569"
                className="text-xs font-bold pointer-events-none select-none"
              >
                {node.label}
              </text>
            </g>
          );
        })}
      </svg>
    );
  };

  // Checklist handler
  const handleMissionCheck = (idx: number) => {
    setCompletedMissions(prev => {
      const next = new Set(prev);
      if (next.has(idx)) next.delete(idx);
      else next.add(idx);
      return next;
    });
  };

  const getStreakDays = () => {
    const baseStreak = guideData?.streak_days || 12;
    return baseStreak + (completedMissions.size * 1);
  };

  return (
    <div className="flex h-screen bg-[#F8FAFC] font-sans text-slate-800 w-full overflow-hidden">
      {/* Sidebar — C: 작은 화면에서 w-16 아이콘 전용, 큰 화면에서 w-64 전체 */}
      <aside className="w-16 xl:w-64 bg-[#1E1B4B] text-white flex-shrink-0 flex flex-col justify-between transition-all duration-300">
        <div>
          <div 
            onClick={() => {
              setStep("consent");
              setFile(null);
              setDatasetId(null);
            }}
            className="p-4 xl:p-6 text-2xl font-bold flex items-center gap-3 cursor-pointer hover:bg-white/5 justify-center xl:justify-start"
          >
            <span>♻️</span>
            <span className="hidden xl:inline">Bias Detox</span>
          </div>
          <nav className="mt-6">
            <ul className="space-y-1">
              {[
                { tab: 'dashboard', icon: <Home size={20}/>, label: '대시보드' },
                { tab: 'realtime', icon: <Activity size={20}/>, label: '실시간 분석' },
                { tab: 'persona', icon: <PieChartIcon size={20}/>, label: '성향 분석' },
                { tab: 'graph', icon: <Network size={20}/>, label: '지식 그래프' },
                { tab: 'guide', icon: <Target size={20}/>, label: '디톡스 가이드' },
                { tab: 'contents', icon: <Clock size={20}/>, label: '콘텐츠 분석' },
              ].map(({ tab, icon, label }) => (
                <li
                  key={tab}
                  onClick={() => { if (datasetId) setActiveTab(tab as any); }}
                  title={label}
                  className={`px-4 xl:px-6 py-4 font-bold flex items-center gap-3 cursor-pointer justify-center xl:justify-start transition-colors
                    ${!datasetId ? 'opacity-50 cursor-not-allowed' : ''}
                    ${activeTab === tab && datasetId ? 'bg-indigo-600' : 'hover:bg-white/10'}`}
                >
                  {icon}
                  <span className="hidden xl:inline">{label}</span>
                </li>
              ))}
              <li title="설정" className="px-4 xl:px-6 py-4 opacity-50 flex items-center gap-3 cursor-not-allowed justify-center xl:justify-start">
                <Settings size={20}/><span className="hidden xl:inline">설정</span>
              </li>
            </ul>
          </nav>
        </div>
        <div className="p-4 xl:p-6 border-t border-white/10 flex items-center gap-3 justify-center xl:justify-start">
          <div className="w-8 h-8 xl:w-10 xl:h-10 rounded-full bg-slate-600 flex-shrink-0"></div>
          <div className="hidden xl:block">
            <div className="font-bold text-sm">홍길동 님</div>
            <div className="text-xs text-slate-400">Free Plan</div>
          </div>
        </div>
      </aside>

      {/* Main Content — C: min-w 설정으로 최소 너비 보장 + 가로 스크롤 허용 */}
      <main className="flex-1 flex flex-col h-full overflow-hidden min-w-0">
        {/* Header */}
        <header className="h-16 xl:h-20 bg-white border-b border-slate-200 flex items-center justify-between px-4 xl:px-8 flex-shrink-0">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">
              {activeTab === 'dashboard' && '대시보드'}
              {activeTab === 'realtime' && '실시간 분석'}
              {activeTab === 'persona' && '심층 성향 분석'}
              {activeTab === 'graph' && '대화형 지식 그래프'}
              {activeTab === 'guide' && '디톡스 가이드'}
              {activeTab === 'contents' && '콘텐츠 세부 분석'}
            </h1>
            <p className="text-sm text-slate-500">AI가 분석한 당신의 콘텐츠 소비 패턴을 확인하세요.</p>
          </div>
          <div className="flex items-center gap-4">
            <Bell className="text-slate-500 cursor-pointer" onClick={() => alert("알림: 새로운 분석 리포트가 도착했습니다!")} />
            <div className="border border-slate-300 rounded-lg px-4 py-2 text-sm font-semibold flex items-center gap-2 cursor-pointer" onClick={() => alert("기간 설정 기능은 프로 버전에서 제공됩니다.")}>
              <Calendar size={16} /> 2026.05.14 ~ 2026.05.20
            </div>
          </div>
        </header>

        {/* Content Area — C: 가로 스크롤 허용, 최소 너비 확보 */}
        <div className="flex-1 overflow-y-auto overflow-x-auto p-4 xl:p-8 relative">
          
          {/* STEP 1: CONSENT */}
          {step === "consent" && (
            <div className="absolute inset-0 bg-[#F8FAFC] z-50 flex items-center justify-center p-8">
              <div className="bg-white p-10 rounded-2xl shadow-xl w-full max-w-lg text-center">
                <h2 className="text-2xl font-bold text-slate-900 mb-2">데이터 수집 및 이용 동의 (1/3)</h2>
                <p className="text-slate-500 mb-6 text-sm">유튜브 시청 패턴 및 필터버블 분석을 위해 아래 항목의 동의가 필요합니다.</p>
                <div className="bg-slate-50 p-5 rounded-xl text-left text-xs text-slate-600 space-y-2 mb-8 max-h-48 overflow-y-auto border border-slate-100">
                  <p className="font-bold">1. 개인정보 수집 목적</p>
                  <p>- 유튜브 테이크아웃 파일 시청 빈도 분석 및 편향 지수 연산.</p>
                  <p className="font-bold">2. 수집 항목</p>
                  <p>- 유튜브 시청 비디오 제목, 채널 이름, 시청 타임스탬프, 검색어 이력.</p>
                  <p className="font-bold">3. 보유 및 이용 기간</p>
                  <p className="text-indigo-600 font-bold">- 분석 즉시 점수 데이터로 익명 가공처리 후 원본 파일은 서버에서 즉시 영구 삭제처리됩니다.</p>
                </div>
                <button 
                  onClick={() => setStep("survey")}
                  className="w-full bg-indigo-600 text-white font-bold py-3 rounded-xl hover:bg-indigo-700 transition-colors"
                >
                  동의하고 다음으로
                </button>
              </div>
            </div>
          )}

          {/* STEP 2: SURVEY QUESTIONNAIRE */}
          {step === "survey" && (
            <div className="absolute inset-0 bg-[#F8FAFC] z-50 flex items-center justify-center p-8">
              <div className="bg-white p-10 rounded-2xl shadow-xl w-full max-w-lg">
                <h2 className="text-2xl font-bold text-slate-900 mb-2 text-center">메타인지 자가진단 (2/3)</h2>
                <p className="text-slate-500 mb-8 text-sm text-center">본인이 스스로 생각하는 시청 성향을 평가해주세요 (0~100점).</p>
                
                <div className="space-y-6 mb-8">
                  <div>
                    <div className="flex justify-between text-sm font-bold text-slate-800 mb-2">
                      <span>주제 다양성 (여러 주제 시청)</span>
                      <span className="text-indigo-600">{surveyData.div}점</span>
                    </div>
                    <input 
                      type="range" min="0" max="100" value={surveyData.div}
                      onChange={(e) => setSurveyData({...surveyData, div: parseInt(e.target.value)})}
                      className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                    />
                  </div>
                  <div>
                    <div className="flex justify-between text-sm font-bold text-slate-800 mb-2">
                      <span>유해 회피력 (자극적 영상 자제)</span>
                      <span className="text-indigo-600">{surveyData.sta}점</span>
                    </div>
                    <input 
                      type="range" min="0" max="100" value={surveyData.sta}
                      onChange={(e) => setSurveyData({...surveyData, sta: parseInt(e.target.value)})}
                      className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                    />
                  </div>
                  <div>
                    <div className="flex justify-between text-sm font-bold text-slate-800 mb-2">
                      <span>탐색 주도성 (직접 검색 시청)</span>
                      <span className="text-indigo-600">{surveyData.ini}점</span>
                    </div>
                    <input 
                      type="range" min="0" max="100" value={surveyData.ini}
                      onChange={(e) => setSurveyData({...surveyData, ini: parseInt(e.target.value)})}
                      className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                    />
                  </div>
                  <div>
                    <div className="flex justify-between text-sm font-bold text-slate-800 mb-2">
                      <span>관점 개방성 (다양한 의견 수용)</span>
                      <span className="text-indigo-600">{surveyData.ope}점</span>
                    </div>
                    <input 
                      type="range" min="0" max="100" value={surveyData.ope}
                      onChange={(e) => setSurveyData({...surveyData, ope: parseInt(e.target.value)})}
                      className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                    />
                  </div>
                </div>

                <button 
                  onClick={() => setStep("upload")}
                  className="w-full bg-indigo-600 text-white font-bold py-3 rounded-xl hover:bg-indigo-700 transition-colors"
                >
                  다음으로 (파일 업로드)
                </button>
              </div>
            </div>
          )}

          {/* STEP 3: FILE UPLOAD CONTAINER */}
          {step === "upload" && (
            <div className="absolute inset-0 bg-[#F8FAFC] z-50 flex items-center justify-center p-8">
              <div className="bg-white p-10 rounded-2xl shadow-xl w-full max-w-lg text-center">
                <h2 className="text-2xl font-bold text-slate-900 mb-2">시청 기록 업로드 (3/3)</h2>
                <p className="text-slate-500 mb-8">구글 테이크아웃에서 다운로드한 시청 데이터(.json 또는 .html)를 드롭해주세요.</p>
                <div 
                  onDragEnter={handleDrag} onDragOver={handleDrag} onDragLeave={handleDrag} onDrop={handleDrop}
                  className={`border-2 border-dashed rounded-xl p-12 mb-8 cursor-pointer transition-colors ${
                    dragActive ? 'border-indigo-600 bg-indigo-50' : 'border-slate-300 hover:border-indigo-500 hover:bg-indigo-50/50'
                  }`}
                  onClick={() => document.getElementById("file-picker")?.click()}
                >
                  <UploadCloud className="w-12 h-12 mx-auto text-slate-400 mb-4" />
                  <h3 className="font-semibold text-slate-700">{selectedFile ? selectedFile.name : "파일 드래그 앤 드롭 또는 클릭"}</h3>
                  <input id="file-picker" type="file" accept=".json,.html" hidden onChange={handleFileSelect} />
                </div>
                <button 
                  onClick={handleStartAnalysis}
                  disabled={!selectedFile}
                  className={`w-full font-bold py-3 rounded-xl transition-colors mb-3 ${
                    selectedFile ? 'bg-indigo-600 text-white hover:bg-indigo-700' : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                  }`}
                >
                  AI 분석 시작하기
                </button>
                <button
                  type="button"
                  id="btn-demo-mode"
                  onClick={() => {
                    setStep("loading");
                    setUploadProgress(20);
                    setTimeout(() => setUploadProgress(60), 300);
                    setTimeout(() => setUploadProgress(100), 600);
                    setTimeout(() => {
                      setDatasetId("demo-dataset");
                      setScores({
                        diversity: 38.0,
                        stability: 76.0,
                        proactivity: 56.0,
                        openness: 41.0,
                        manipulation_index: 72.0,
                        persona_type: "PNSF"
                      });
                      setReport({
                        overall_summary: "특정 분야에 과도하게 매몰되어 다른 관점을 수용하지 못할 위험(확증편향)이 큽니다.",
                        axis_comments: [
                          "다양성 점수는 38/100으로 특정 장르에 지나치게 쏠림 현상이 관찰됩니다.",
                          "안정성 점수는 76/100으로 비교적 안전한 영상을 시청하고 있습니다.",
                          "주도성 점수는 56/100으로 추천 영상을 주로 소비합니다.",
                          "개방성 점수는 41/100으로 고정된 취향을 가집니다."
                        ],
                        key_findings: "IT/테크 중심의 편향 시청이 관찰됩니다.",
                        recommendations: "역방향 쿼리를 사용한 적극적 탐색이 필요합니다.",
                        caution_notes: "알고리즘 필터 버블 주의",
                        missions: [
                          { mission_type: "역방향 쿼리", description: "인공지능의 윤리적 문제와 규제 필요성 영상을 검색하여 10분 이상 시청합니다.", success_condition: "관련 검색어로 동영상 시청 완료" },
                          { mission_type: "비구독 채널 탐색", description: "평소 전혀 구독하지 않는 경제 분야 인기 채널의 영상을 1개 시청합니다.", success_condition: "영상 시청 완료" },
                          { mission_type: "숏폼 탈출", description: "오늘 하루 유튜브 숏츠 시청 시간을 30분 이내로 조절합니다.", success_condition: "숏츠 시청 제한 달성" }
                        ]
                      });
                      setRealtimeData([
                        { time: '09:00', dopamine: 40 },
                        { time: '12:00', dopamine: 65 },
                        { time: '15:00', dopamine: 85 },
                        { time: '18:00', dopamine: 92 },
                        { time: 'Now', dopamine: 45 }
                      ]);
                      setPersonaData({
                        type: "PNSF",
                        weakness: "특정 분야에 과도하게 매몰되어 다른 관점을 수용하지 못할 위험(확증편향)이 큽니다.",
                        ai_scores: { div: 38, sta: 76, ini: 56, ope: 41 },
                        history: [ { month: '1월', objectivity: 70 }, { month: '3월', objectivity: 65 }, { month: '5월', objectivity: 56 } ]
                      });
                      setGraphData({
                        nodes: [
                          { id: 1, label: "인공지능", group: "tech", size: 30 },
                          { id: 2, label: "기술/IT", group: "tech", size: 25 },
                          { id: 3, label: "경제/금융", group: "economy", size: 20 },
                          { id: 4, label: "딥러닝", group: "tech", size: 15 },
                          { id: 5, label: "챗GPT", group: "tech", size: 15 },
                          { id: 6, label: "AI 윤리", group: "tech", size: 15 },
                          { id: 7, label: "투자/주식", group: "economy", size: 15 },
                          { id: 8, label: "글로벌 경제", group: "economy", size: 15 },
                          { id: 9, label: "생산성", group: "self", size: 15 },
                          { id: 10, label: "마인드셋", group: "self", size: 15 }
                        ],
                        edges: [
                          { source: 1, target: 4 }, { source: 1, target: 5 }, { source: 1, target: 6 },
                          { source: 1, target: 2 }, { source: 2, target: 9 }, { source: 2, target: 10 },
                          { source: 1, target: 3 }, { source: 3, target: 7 }, { source: 3, target: 8 },
                          { source: 2, target: 8 }
                        ]
                      });
                      setGuideData({
                        streak_days: 12,
                        daily_missions: [
                          { id: 1, task: "반대 성향 영상 1개 끝까지 시청", completed: true },
                          { id: 2, task: "구독하지 않은 채널 영상 시청", completed: true },
                          { id: 3, task: "숏폼 영상 30분 미만 시청", completed: false }
                        ],
                        streak_history: []
                      });
                      setContents({
                        watch_history: [
                          { id: 1, title: "인공지능 혁명과 인간 존엄성에 대한 철학적 성찰", channel_name: "인문학 명강의", watch_time: new Date().toISOString(), video_id: "", dopamine_tag: "🧘 저도파민/유익" },
                          { id: 2, title: "[쇼츠] 롤 펜타킬 역대급 피지컬 순간 모음", channel_name: "게이머TV", watch_time: new Date().toISOString(), video_id: "", dopamine_tag: "⚡ 고도파민" },
                          { id: 3, title: "글로벌 거시 경제 리스크 진단 및 자산 배분 전략", channel_name: "삼프로티비", watch_time: new Date().toISOString(), video_id: "", dopamine_tag: "🧘 저도파민/유익" },
                          { id: 4, title: "경악을 금치 못하는 충격 폭로 실태 단독 보도", channel_name: "연예이슈뉴스", watch_time: new Date().toISOString(), video_id: "", dopamine_tag: "⚡ 고도파민" }
                        ],
                        top_channels: [
                          { name: "게이머TV", count: 18, percentage: 38.0 },
                          { name: "연예이슈뉴스", count: 12, percentage: 25.0 },
                          { name: "삼프로티비", count: 9, percentage: 19.0 },
                          { name: "인문학 명강의", count: 5, percentage: 10.0 },
                          { name: "기타 채널", count: 4, percentage: 8.0 }
                        ]
                      });
                      setStep("dashboard");
                      setActiveTab("dashboard");
                    }, 800);
                  }}
                  className="w-full text-indigo-600 hover:text-indigo-800 font-semibold py-2 rounded-xl transition-colors text-sm border border-indigo-100 hover:bg-indigo-50/30"
                >
                  데모 모드로 시작하기
                </button>
              </div>
            </div>
          )}

          {/* STEP 4: ANALYTIC PROGRESS BAR */}
          {step === "loading" && (
            <div className="absolute inset-0 bg-[#F8FAFC] z-50 flex items-center justify-center p-8">
              <div className="bg-white p-10 rounded-2xl shadow-xl w-full max-w-lg text-center">
                <h2 className="text-2xl font-bold text-slate-900 mb-2">알고리즘 분석 중</h2>
                <p className="text-slate-500 mb-8 text-sm">데이터의 형태소를 분류하고 편향 위험도를 측정하고 있습니다...</p>
                <div className="w-full bg-slate-100 rounded-full h-4 mb-4 overflow-hidden">
                  <div className="bg-indigo-600 h-full transition-all duration-300 rounded-full" style={{ width: `${uploadProgress}%` }}></div>
                </div>
                <div className="text-indigo-600 font-bold">{uploadProgress}% 완료</div>
              </div>
            </div>
          )}

          {/* STEP 5: DASHBOARD DISPLAY */}
          {step === "dashboard" && (
            <div className="w-full min-w-[900px] max-w-[1400px] mx-auto pb-12">
              
              {/* === DASHBOARD TAB === */}
              {activeTab === 'dashboard' && (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 xl:gap-6">
                  {/* Top Row */}
                  <div className="bg-white rounded-2xl shadow-sm p-5 flex flex-col min-h-[240px] xl:min-h-[280px]">
                    <h3 className="font-bold text-slate-900 mb-4">편향 위험도 (조종 지수)</h3>
                    <div className="flex-1 flex flex-col items-center justify-center relative">
                      <div className="w-full h-32">
                        <ResponsiveContainer width="100%" height="100%">
                          <RePieChart>
                            <Pie data={[{v:1},{v:1},{v:1},{v:1},{v:1}]} cx="50%" cy="100%" startAngle={180} endAngle={0} innerRadius={60} outerRadius={80} paddingAngle={0} dataKey="v" stroke="none">
                              <Cell fill="#3B82F6"/><Cell fill="#10B981"/><Cell fill="#F59E0B"/><Cell fill="#F97316"/><Cell fill="#EF4444"/>
                            </Pie>
                          </RePieChart>
                        </ResponsiveContainer>
                      </div>
                      <div className="absolute bottom-4 text-center">
                        <div className={`text-5xl font-black ${brsInfo.textColor} leading-none`}>
                          {Math.round(currentBrs)}<span className="text-2xl opacity-80">/100</span>
                        </div>
                        <div className={`${brsInfo.textColor} font-bold text-sm mt-1`}>{brsInfo.label}</div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white rounded-2xl shadow-sm p-5 flex flex-col min-h-[240px] xl:min-h-[280px]">
                    <h3 className="font-bold text-slate-900 mb-4">알고리즘 성향 (DSAO)</h3>
                    <div className="flex-1 flex items-center justify-between">
                      <div className="flex-1 pr-2 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-3xl font-black text-slate-950">{personaType}</span>
                          <span className="text-2xl">{dsao.character}</span>
                        </div>
                        <div className="inline-block px-2.5 py-1 bg-indigo-50 text-indigo-600 text-xs font-bold rounded-lg mb-3 truncate max-w-full">
                          {dsao.alias}
                        </div>
                        <p className="text-[11px] font-bold text-slate-400 mb-1">{dsao.name}</p>
                        <p className="text-[11px] text-slate-600 leading-snug line-clamp-3">{dsao.desc}</p>
                      </div>
                      <div className="w-32 h-32 flex-shrink-0 relative">
                        <div className="absolute inset-0 bg-gradient-to-br from-indigo-50 to-slate-100 rounded-2xl flex flex-col items-center justify-center border border-indigo-100/50 shadow-inner">
                          <span className="text-4xl filter drop-shadow">{dsao.character}</span>
                          <span className="text-[9px] font-bold text-indigo-500 mt-2 tracking-wider">유형 캐릭터</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white rounded-2xl shadow-sm p-5 min-h-[240px] xl:min-h-[280px]">
                    <h3 className="font-bold text-slate-900 mb-4">최근 주요 관심사 TOP 5</h3>
                    <div className="space-y-4">
                      {[
                        { n: '1. 인공지능', p: 32, c: '#8B5CF6' },
                        { n: '2. 경제/금융', p: 24, c: '#3B82F6' },
                        { n: '3. 자기계발', p: 16, c: '#10B981' },
                        { n: '4. 정치/시사', p: 14, c: '#F97316' },
                        { n: '5. 기술/IT', p: 14, c: '#F59E0B' }
                      ].map((item, i) => (
                        <div key={i} className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full text-white flex items-center justify-center text-xs font-bold" style={{backgroundColor: item.c}}>{item.n.charAt(3)}</div>
                          <div className="flex-1">
                            <div className="flex justify-between text-xs font-semibold text-slate-900 mb-1">
                              <span>{item.n}</span><span>{item.p}%</span>
                            </div>
                            <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                              <div className="h-full rounded-full" style={{width: `${item.p}%`, backgroundColor: item.c}}></div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Middle Row — B: 전체 너비 */}
                  <div className="md:col-span-2 xl:col-span-3 bg-white rounded-2xl shadow-sm p-5">
                    <h3 className="font-bold text-slate-900 mb-6">관심사 편향 변화 (타임라인)</h3>
                    <div className="w-full h-56 xl:h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={timelineData}>
                          <defs>
                            <linearGradient id="colorScore" x1="0" y1="0" x2="1" y2="0">
                              <stop offset="5%" stopColor="#EF4444" stopOpacity={0.4}/>
                              <stop offset="50%" stopColor="#F59E0B" stopOpacity={0.4}/>
                              <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.4}/>
                            </linearGradient>
                          </defs>
                          <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{fill: '#94A3B8', fontSize: 12}} />
                          <YAxis axisLine={false} tickLine={false} tick={{fill: '#94A3B8', fontSize: 12}} />
                          <Tooltip />
                          <Area type="monotone" dataKey="score" stroke="#475569" fillOpacity={1} fill="url(#colorScore)" />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* Bottom Row — B: 2컬럼 */}
                  <div className="md:col-span-1 xl:col-span-1 bg-white rounded-2xl shadow-sm p-5 flex flex-col min-h-[320px] xl:min-h-[400px]">
                    <div className="flex justify-between items-center mb-4">
                      <h3 className="font-bold text-slate-900">관심사 지식 그래프</h3>
                      <span className="text-xs text-indigo-600 font-bold hover:underline cursor-pointer" onClick={() => setActiveTab("graph")}>전체 보기 &gt;</span>
                    </div>
                    <div className="flex-1 bg-slate-50 rounded-xl overflow-hidden flex items-center justify-center border border-slate-100">
                      {renderSvgGraph()}
                    </div>
                  </div>

                  <div className="md:col-span-1 xl:col-span-2 bg-white rounded-2xl shadow-sm p-5 min-h-[320px] xl:min-h-[400px] flex flex-col">
                    <h3 className="font-bold text-slate-900 mb-2">디톡스 미션</h3>
                    <div className="flex gap-6 items-center flex-1">
                      <div className="relative w-40 h-40 flex items-center justify-center">
                        <ResponsiveContainer width="100%" height="100%">
                          <RePieChart>
                            <Pie 
                              data={[
                                { value: completedMissions.size || 1 }, 
                                { value: Math.max(0, 3 - completedMissions.size) }
                              ]} 
                              cx="50%" cy="50%" innerRadius={55} outerRadius={70} startAngle={90} endAngle={-270} stroke="none" dataKey="value"
                            >
                              <Cell fill="#10B981"/>
                              <Cell fill="#E2E8F0"/>
                            </Pie>
                          </RePieChart>
                        </ResponsiveContainer>
                        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                          <span className="text-2xl font-black text-slate-800">{completedMissions.size}/3</span>
                          <span className="text-xs text-slate-400">진행률</span>
                        </div>
                      </div>
                      <div className="flex-1 space-y-3">
                        <div className="font-bold text-xs text-slate-400">추천 키워드 (역방향 쿼리)</div>
                        {report?.missions?.map((m: any, idx: number) => (
                          <div 
                            key={idx} 
                            onClick={() => window.open(`https://www.youtube.com/results?search_query=${encodeURIComponent(m.mission_type)}`, '_blank')}
                            className="flex items-center gap-3 p-3 bg-slate-50 hover:bg-slate-100/70 border border-slate-100 rounded-lg cursor-pointer transition-colors"
                          >
                            <div className="w-2 h-2 rounded-full bg-indigo-500"></div>
                            <div className="flex-1 text-xs font-semibold text-slate-700 truncate">{m.mission_type}</div>
                            <span className="text-[10px] text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded font-bold">검색</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* === REALTIME TAB === */}
              {activeTab === 'realtime' && (
                <div className="bg-white rounded-2xl shadow-sm p-6">
                  <h3 className="font-bold text-slate-900 mb-6">오늘의 도파민 수치 추이</h3>
                  <div className="w-full h-96">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={realtimeData}>
                        <XAxis dataKey="time" />
                        <YAxis />
                        <Tooltip />
                        <Line type="monotone" dataKey="dopamine" stroke="#EF4444" strokeWidth={3} dot={{r: 5}} fill="rgba(239, 68, 68, 0.1)" />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}

              {/* === PERSONA TAB === */}
              {activeTab === 'persona' && (
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 xl:gap-6">
                  <div className="bg-white rounded-2xl shadow-sm p-5">
                    <h3 className="font-bold text-slate-900 mb-6">자가진단 vs AI 실제 분석 대조</h3>
                    <div className="w-full h-96">
                      <ResponsiveContainer width="100%" height="100%">
                        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={comparisonRadarData}>
                          <PolarGrid />
                          <PolarAngleAxis dataKey="subject" />
                          <Radar name="자가진단" dataKey="A" stroke="#F59E0B" fill="rgba(245, 158, 11, 0.3)" />
                          <Radar name="AI 분석" dataKey="B" stroke="#4F46E5" fill="rgba(79, 70, 229, 0.3)" />
                          <Tooltip />
                        </RadarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                  <div className="flex flex-col gap-4 xl:gap-6">
                    <div className="bg-white rounded-2xl shadow-sm p-6">
                      <h3 className="font-bold text-slate-900 mb-4">취약점 분석 (거울 치료)</h3>
                      <p className="text-red-600 font-bold bg-red-50 p-4 rounded-xl text-sm leading-relaxed border border-red-100">
                        {calculateGapWarning()}
                      </p>
                      <p className="text-slate-600 text-xs mt-3 leading-relaxed">
                        {report?.overall_summary}
                      </p>
                    </div>
                    <div className="bg-white rounded-2xl shadow-sm p-6 flex-1 flex flex-col justify-between">
                      <h3 className="font-bold text-slate-900 mb-4">알고리즘 성향 상세 분석 ({personaType})</h3>
                      <div className="bg-indigo-50/50 border border-indigo-100 rounded-xl p-4 mb-4 flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <div className="w-10 h-10 rounded-lg bg-indigo-100 flex items-center justify-center text-2xl shadow-sm">
                            {dsao.character}
                          </div>
                          <div>
                            <h4 className="font-bold text-sm text-slate-900">{dsao.alias}</h4>
                            <p className="text-xs text-slate-400">{dsao.name}</p>
                          </div>
                        </div>
                        <p className="text-xs text-slate-600 leading-relaxed">{dsao.desc}</p>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4 text-xs mb-4">
                        <div className="bg-emerald-50/30 border border-emerald-100 p-3 rounded-lg">
                          <div className="font-bold text-emerald-700 mb-2">💪 유형 강점</div>
                          <ul className="list-disc list-inside space-y-1 text-slate-600 text-[11px]">
                            {dsao.strengths.map((s, i) => <li key={i}>{s}</li>)}
                          </ul>
                        </div>
                        <div className="bg-rose-50/30 border border-rose-100 p-3 rounded-lg">
                          <div className="font-bold text-rose-700 mb-2">⚠️ 위험 신호</div>
                          <ul className="list-disc list-inside space-y-1 text-slate-600 text-[11px]">
                            {dsao.risks.map((r, i) => <li key={i}>{r}</li>)}
                          </ul>
                        </div>
                      </div>

                      <div className="bg-slate-50 border border-slate-200/60 p-3.5 rounded-lg text-xs">
                        <span className="font-bold text-slate-800">🥗 디톡스 실천 방향:</span>
                        <p className="text-indigo-600 font-semibold mt-1 text-[11px]">{dsao.detox}</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* === GRAPH TAB === */}
              {activeTab === 'graph' && (
                <div className="bg-white rounded-2xl shadow-sm p-6">
                  <div className="flex justify-between items-center mb-6">
                    <h3 className="font-bold text-slate-900">대화형 지식 그래프</h3>
                    <div className="text-xs text-slate-400">노드를 클릭하여 세부 분석 및 조종 위험도를 체크하세요.</div>
                  </div>
                  <div className="w-full h-[550px] bg-slate-50 border border-slate-200/60 rounded-2xl flex items-center justify-center p-4">
                     {renderSvgGraph()}
                  </div>
                </div>
              )}

              {/* === GUIDE TAB === */}
              {activeTab === 'guide' && (
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 xl:gap-6">
                  <div className="bg-white rounded-2xl shadow-sm p-5">
                    <div className="flex justify-between items-center mb-6">
                      <h3 className="font-bold text-slate-900">오늘의 미션 보드</h3>
                      <div className="flex gap-2">
                        <button 
                          onClick={() => { setActiveCourse(3); alert("3일 단기 디톡스 코스로 변경되었습니다."); }}
                          className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                            activeCourse === 3 ? 'bg-indigo-600 text-white' : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                          }`}
                        >
                          3일 코스
                        </button>
                        <button 
                          onClick={() => { setActiveCourse(7); alert("7일 집중 디톡스 코스로 변경되었습니다."); }}
                          className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                            activeCourse === 7 ? 'bg-indigo-600 text-white' : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                          }`}
                        >
                          7일 코스
                        </button>
                      </div>
                    </div>
                    <div className="space-y-4">
                      {report?.missions?.map((m: any, idx: number) => {
                        const isCompleted = completedMissions.has(idx);
                        return (
                          <div 
                            key={idx} 
                            onClick={() => handleMissionCheck(idx)}
                            className={`flex items-center gap-3 p-4 rounded-xl cursor-pointer transition-colors border ${
                              isCompleted 
                                ? 'bg-emerald-50 border-emerald-100 text-emerald-800' 
                                : 'bg-slate-50 border-slate-100 text-slate-700 hover:bg-slate-100/50'
                            }`}
                          >
                            {isCompleted ? <CheckCircle2 className="text-emerald-500 flex-shrink-0" /> : <Circle className="text-slate-400 flex-shrink-0" />}
                            <div className="flex-1">
                              <span className={`font-bold text-sm ${isCompleted ? 'line-through text-emerald-600' : ''}`}>
                                [{m.mission_type}] {m.description}
                              </span>
                              <div className={`text-xs mt-1 ${isCompleted ? 'text-emerald-500' : 'text-slate-400'}`}>
                                달성 기준: {m.success_condition}
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                  <div className="bg-white rounded-2xl shadow-sm p-5">
                    <h3 className="font-bold text-slate-900 mb-6">연속 달성 기록 (Streak)</h3>
                    <div className="text-4xl font-black text-indigo-600 mb-6">{getStreakDays()}일 연속 🔥</div>
                    
                    <div className="grid grid-cols-7 gap-2">
                      {Array.from({length: 35}).map((_, i) => {
                        const hasData = i < (guideData?.streak_days || 12) + completedMissions.size;
                        return (
                          <div 
                            key={i} 
                            title={`Day ${i+1}`}
                            className={`aspect-square rounded transition-all duration-300 ${hasData ? 'bg-emerald-500 shadow-sm shadow-emerald-200' : 'bg-slate-200'}`}
                          ></div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              )}

              {/* === CONTENTS TAB === */}
              {activeTab === 'contents' && (
                <div className="grid grid-cols-1 xl:grid-cols-12 gap-4 xl:gap-6">
                  {/* Left Column: Watch History */}
                  <div className="xl:col-span-8 bg-white rounded-2xl shadow-sm p-5 flex flex-col min-h-[400px] xl:h-[600px]">
                    <div className="flex justify-between items-center mb-6">
                      <div>
                        <h3 className="font-bold text-lg text-slate-900">최근 시청 영상 분석</h3>
                        <p className="text-xs text-slate-400 mt-1">사용자의 유튜브 시청 데이터에서 추출한 개별 콘텐츠별 위험도 태그입니다.</p>
                      </div>
                      <span className="text-xs text-slate-500 font-semibold bg-slate-100 px-2.5 py-1 rounded-full">
                        총 {contents?.watch_history?.length || 0}개 분석됨
                      </span>
                    </div>
                    
                    <div className="flex-1 overflow-y-auto space-y-3 pr-2 scrollbar-thin scrollbar-thumb-slate-200">
                      {contents?.watch_history && contents.watch_history.length > 0 ? (
                        contents.watch_history.map((video: any) => (
                          <div 
                            key={video.id} 
                            onClick={() => { if (video.video_id) window.open(`https://www.youtube.com/watch?v=${video.video_id}`, '_blank'); }}
                            className="flex items-center gap-4 p-4 bg-slate-50 hover:bg-indigo-50/50 border border-slate-100 hover:border-indigo-100 rounded-xl cursor-pointer transition-all"
                          >
                            {/* Video Icon */}
                            <div className="w-10 h-10 rounded-lg bg-slate-100 flex items-center justify-center text-lg shadow-inner">
                              🎬
                            </div>
                            {/* Title & Channel */}
                            <div className="flex-1 min-w-0">
                              <h4 className="font-bold text-xs text-slate-800 truncate mb-1">{video.title}</h4>
                              <div className="flex items-center gap-2 text-[11px] text-slate-500">
                                <span className="font-semibold text-indigo-600">{video.channel_name}</span>
                                <span>•</span>
                                <span>{video.watch_time ? new Date(video.watch_time).toLocaleString('ko-KR', { hour: '2-digit', minute: '2-digit' }) : ""}</span>
                              </div>
                            </div>
                            {/* Dopamine Tag */}
                            <span className={`text-[10px] font-bold px-3 py-1.5 rounded-full shadow-sm ${
                              video.dopamine_tag.includes("⚡") 
                                ? 'bg-red-50 text-red-600 border border-red-100' 
                                : 'bg-emerald-50 text-emerald-600 border border-emerald-100'
                            }`}>
                              {video.dopamine_tag}
                            </span>
                          </div>
                        ))
                      ) : (
                        <div className="h-full flex flex-col items-center justify-center text-slate-400">
                          <Clock className="w-12 h-12 mb-3 text-slate-300" />
                          <p className="text-sm">분석 완료된 시청 기록이 없습니다.</p>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Right Column: Top Channels & Alternative Advice */}
                  <div className="xl:col-span-4 flex flex-col gap-4 xl:gap-6">
                    {/* Top Channels */}
                    <div className="bg-white rounded-2xl shadow-sm p-5 flex flex-col min-h-[240px] xl:h-[320px]">
                      <h3 className="font-bold text-slate-900 mb-4">선호 시청 채널 TOP 5</h3>
                      <div className="flex-1 space-y-4 overflow-y-auto">
                        {contents?.top_channels && contents.top_channels.length > 0 ? (
                          contents.top_channels.map((ch: any, idx: number) => {
                            const colors = ['bg-indigo-600', 'bg-blue-500', 'bg-emerald-500', 'bg-amber-500', 'bg-rose-500'];
                            return (
                              <div key={idx} className="space-y-1">
                                <div className="flex justify-between text-xs font-bold text-slate-700">
                                  <span className="truncate max-w-[200px]">{idx + 1}. {ch.name}</span>
                                  <span>{ch.count}회 ({ch.percentage}%)</span>
                                </div>
                                <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                                  <div className={`h-full rounded-full ${colors[idx % colors.length]}`} style={{ width: `${ch.percentage}%` }}></div>
                                </div>
                              </div>
                            );
                          })
                        ) : (
                          <p className="text-sm text-slate-400 text-center py-12">데이터가 존재하지 않습니다.</p>
                        )}
                      </div>
                    </div>

                    {/* Content Advice Card */}
                    <div className="bg-gradient-to-br from-indigo-900 to-slate-900 text-white rounded-2xl shadow-lg p-6 flex-1 flex flex-col justify-between">
                      <div>
                        <div className="inline-block px-3 py-1 bg-white/10 rounded-full text-[10px] font-bold tracking-wider mb-4">
                          AI DIETARY ADVICE
                        </div>
                        <h4 className="font-extrabold text-base leading-snug mb-3">
                          도파민 디톡스를 위한 시청 가이드라인
                        </h4>
                        <p className="text-xs text-slate-300 leading-relaxed">
                          현재 {contents?.top_channels?.[0]?.name || "일부"} 채널 시청 비율이 높게 집중되어 있어 정보의 필터 버블 현상이 우려됩니다.
                          <br /><br />
                          영상 탐색 시 <strong>쇼츠/자극성 썸네일</strong> 대신, 15분 이상의 <strong>다큐멘터리, 인문학 지식 콘텐츠</strong>를 검색하여 알고리즘 노출 구도를 능동적으로 전환하세요.
                        </p>
                      </div>
                      <button 
                        onClick={() => setActiveTab("guide")}
                        className="w-full bg-white text-indigo-950 font-bold py-3 rounded-xl hover:bg-slate-100 transition-colors text-xs mt-6"
                      >
                        디톡스 미션 수행하기
                      </button>
                    </div>
                  </div>
                </div>
              )}

            </div>
          )}
        </div>
      </main>

      {/* SVG node click detail overlay modal */}
      {selectedNode && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl p-6 max-w-sm w-full shadow-2xl border border-slate-100">
            <h3 className="text-xl font-bold text-slate-950 mb-3 flex items-center gap-2">
              <span>🔗</span> {selectedNode.label} 분석
            </h3>
            <p className="text-slate-600 text-sm leading-relaxed mb-6">
              [{selectedNode.label}] 주제에 대한 공출현 빈도가 매우 높습니다. 
              특정 주제의 필터 버블(Filter Bubble)을 예방하고 보다 폭넓은 객관성을 유지하기 위해, 
              평소 구독하지 않거나 반대 논조를 펼치는 채널의 영상들을 주도적으로 탐색해보시길 권장합니다.
            </p>
            <button 
              onClick={() => setSelectedNode(null)}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2.5 rounded-xl transition-colors"
            >
              닫기
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
