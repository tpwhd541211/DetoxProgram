"use client";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

import { useState, useEffect, useRef } from "react";
import { UploadCloud, Bell, Calendar, Home, Activity, PieChart as PieChartIcon, Network, Target, Clock, Settings, CheckCircle2, Circle } from "lucide-react";
import DeveloperInspector from "@/components/DeveloperInspector";
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, PieChart as RePieChart, Pie, Cell, LineChart, Line, BarChart, Bar } from 'recharts';
import { supabase } from "@/lib/supabase";

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

function ElapsedTimeDisplay({ startTime, pollingStage }: { startTime: number | null; pollingStage: string }) {
  const [elapsed, setElapsed] = useState(0);
  useEffect(() => {
    if (!startTime) return;
    const timer = setInterval(() => {
      setElapsed(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);
    return () => clearInterval(timer);
  }, [startTime]);
  if (!startTime) return null;
  const mins = Math.floor(elapsed / 60);
  const secs = elapsed % 60;
  const timeStr = mins > 0 ? `${mins}분 ${secs}초 경과` : `${secs}초 경과`;
  const estimateMsg: Record<string, string> = {
    queued:   "분석 준비 중...",
    parsing:  "예상 소요: 약 1분 이내",
    enriching:"예상 소요: 약 2~3분",
    scoring:  "예상 소요: 시청 기록 양에 따라 3~15분 (GCP AI 분석 중)",
    report:   "예상 소요: 약 1분 이내",
    saving:   "거의 완료됐습니다..."
  };
  return (
    <div className="mt-4 text-center space-y-1">
      <p className="text-slate-500 text-xs font-medium">{timeStr}</p>
      {estimateMsg[pollingStage] && (
        <p className="text-indigo-400 text-xs">{estimateMsg[pollingStage]}</p>
      )}
    </div>
  );
}

interface Node {
  id: number;
  label: string;
  group: string;
  size: number;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
}

interface Edge {
  source: number;
  target: number;
  value?: number;
}

const CATEGORY_COLORS: Record<string, string> = {
  channel: '#ef4444',       // 📺 채널 (원천 노드)
  business_tech: '#3b82f6', // 📈 경제/IT/테크
  entertainment: '#F59E0B', // 🍿 문화/엔터/예능
  info_society: '#10b981',  // 📖 정보/지식/시사
  life_health: '#8B5CF6',   // 🌱 일상/건강/취미
  game: '#EC4899',          // 🎮 게임
  other: '#64748B'          // ❓ 기타/미분류
};

const CATEGORY_LABELS: Record<string, string> = {
  channel: '📺 채널',
  business_tech: '📈 경제/IT/테크',
  entertainment: '🍿 문화/엔터/예능',
  info_society: '📖 정보/지식/시사',
  life_health: '🌱 일상/건강/취미',
  game: '🎮 게임',
  other: '❓ 기타/미분류'
};

function InteractiveForceGraph({ graphData, setSelectedNode, variant = 'full' }: {
  graphData: { nodes: any[]; edges: any[] };
  setSelectedNode: (node: any) => void;
  variant?: 'mini' | 'full';
}) {
  const [nodes, setNodes] = useState<Node[]>([]);
  const svgRef = useRef<SVGSVGElement | null>(null);
  const nodesRef = useRef<Node[]>([]);
  const dragNodeRef = useRef<number | null>(null);

  const isFull = variant === 'full';
  const width = isFull ? 800 : 440;
  const height = isFull ? 600 : 440;
  const centerX = width / 2;
  const centerY = height / 2;

  useEffect(() => {
    if (!graphData || !graphData.nodes) return;
    const radius = isFull ? 240 : 130;
    const initialized = graphData.nodes.map((node, idx) => {
      const angle = (idx / graphData.nodes.length) * 2 * Math.PI;
      return {
        ...node,
        x: centerX + Math.cos(angle) * radius + (Math.random() - 0.5) * 10,
        y: centerY + Math.sin(angle) * radius + (Math.random() - 0.5) * 10,
        vx: 0,
        vy: 0
      };
    });
    nodesRef.current = initialized;
    setNodes(initialized);
  }, [graphData, variant]);

  useEffect(() => {
    let animationId: number;
    const tick = () => {
      const currentNodes = nodesRef.current;
      if (currentNodes.length === 0) {
        animationId = requestAnimationFrame(tick);
        return;
      }
      const edges = graphData.edges || [];
      const kRepulsion = isFull ? 12000 : 4000;
      const kAttraction = isFull ? 0.015 : 0.03;
      const desiredLength = isFull ? 260 : 130;
      const kGravity = isFull ? 0.004 : 0.01;
      const friction = 0.85;

      for (let i = 0; i < currentNodes.length; i++) {
        for (let j = i + 1; j < currentNodes.length; j++) {
          const n1 = currentNodes[i];
          const n2 = currentNodes[j];
          const dx = n2.x! - n1.x!;
          const dy = n2.y! - n1.y!;
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          const repulsionThreshold = isFull ? 480 : 280;
          if (dist < repulsionThreshold) {
            const force = kRepulsion / (dist * dist);
            const fx = (dx / dist) * force;
            const fy = (dy / dist) * force;
            n1.vx! -= fx;
            n1.vy! -= fy;
            n2.vx! += fx;
            n2.vy! += fy;
          }
        }
      }

      edges.forEach(edge => {
        const source = currentNodes.find(n => n.id === edge.source);
        const target = currentNodes.find(n => n.id === edge.target);
        if (source && target) {
          const dx = target.x! - source.x!;
          const dy = target.y! - source.y!;
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          const force = kAttraction * (dist - desiredLength);
          const fx = (dx / dist) * force;
          const fy = (dy / dist) * force;
          source.vx! += fx;
          source.vy! += fy;
          target.vx! -= fx;
          target.vy! -= fy;
        }
      });

      const margin = isFull ? 58 : 48;
      const updated = currentNodes.map(n => {
        if (n.id === dragNodeRef.current) return n;
        const dx = centerX - n.x!;
        const dy = centerY - n.y!;
        n.vx! += dx * kGravity;
        n.vy! += dy * kGravity;
        n.vx! *= friction;
        n.vy! *= friction;
        n.x! += n.vx!;
        n.y! += n.vy!;

        if (n.x! < margin) { n.x! = margin; n.vx! = 0; }
        if (n.x! > width - margin) { n.x! = width - margin; n.vx! = 0; }
        if (n.y! < margin) { n.y! = margin; n.vy! = 0; }
        if (n.y! > height - margin) { n.y! = height - margin; n.vy! = 0; }
        return { ...n };
      });

      nodesRef.current = updated;
      setNodes(updated);
      animationId = requestAnimationFrame(tick);
    };
    animationId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animationId);
  }, [graphData, variant]);

  const handleMouseDown = (e: React.MouseEvent, nodeId: number) => {
    e.stopPropagation();
    dragNodeRef.current = nodeId;
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (dragNodeRef.current === null || !svgRef.current) return;
    const rect = svgRef.current.getBoundingClientRect();
    const mouseX = ((e.clientX - rect.left) / rect.width) * width;
    const mouseY = ((e.clientY - rect.top) / rect.height) * height;
    nodesRef.current = nodesRef.current.map(n => {
      if (n.id === dragNodeRef.current) {
        return { ...n, x: mouseX, y: mouseY, vx: 0, vy: 0 };
      }
      return n;
    });
    setNodes([...nodesRef.current]);
  };

  const handleMouseUp = () => {
    dragNodeRef.current = null;
  };

  return (
    <div className="w-full flex flex-col items-center gap-4">
      <div 
        className={`w-full ${isFull ? 'h-[600px]' : 'h-[400px]'} bg-slate-50 border border-slate-100 rounded-2xl relative overflow-hidden flex items-center justify-center select-none`}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <svg 
          ref={svgRef}
          className={`w-full h-full ${isFull ? 'max-w-full' : 'max-w-[440px]'}`} 
          viewBox={`0 0 ${width} ${height}`}
        >
          {/* Edges */}
          {(graphData.edges || []).map((edge: any, index: number) => {
            const src = nodes.find(n => n.id === edge.source);
            const tgt = nodes.find(n => n.id === edge.target);
            if (!src || !tgt) return null;
            return (
              <line 
                key={`edge-${index}`}
                x1={src.x} y1={src.y}
                x2={tgt.x} y2={tgt.y}
                stroke="#E2E8F0"
                strokeWidth={edge.value ? Math.max(1.5, edge.value * 0.4) : 2}
                strokeOpacity={0.7}
              />
            );
          })}

          {/* Nodes */}
          {nodes.map((node: any) => {
            const color = CATEGORY_COLORS[node.group] || CATEGORY_COLORS.other;
            const size = (node.size || 12) * (isFull ? 1.3 : 1.1);
            return (
              <g 
                key={`node-${node.id}`} 
                className="group cursor-grab active:cursor-grabbing"
                transform={`translate(${node.x}, ${node.y})`}
                onMouseDown={(e) => handleMouseDown(e, node.id)}
                onClick={() => setSelectedNode(node)}
              >
                <circle
                  r={size + 6}
                  fill={color}
                  fillOpacity={0.06}
                  className="transition-all duration-300 group-hover:fill-opacity-15"
                />
                <circle
                  r={size}
                  fill={color}
                  stroke="#FFFFFF"
                  strokeWidth={2}
                  className="transition-all duration-200 group-hover:scale-110 shadow-sm"
                  style={{ filter: 'drop-shadow(0px 2px 4px rgba(0, 0, 0, 0.1))' }}
                />
                <text
                  y={size + (isFull ? 22 : 18)}
                  textAnchor="middle"
                  fill="#334155"
                  className={`${isFull ? 'text-sm md:text-base' : 'text-xs'} font-extrabold select-none pointer-events-none`}
                  style={{ paintOrder: 'stroke', stroke: '#FFFFFF', strokeWidth: 3.5 }}
                >
                  {node.label}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Category Legend */}
      <div className="flex flex-wrap gap-x-3 gap-y-1.5 justify-center bg-slate-50 border border-slate-100/60 p-3 rounded-xl max-w-full">
        {Object.entries(CATEGORY_LABELS).map(([key, label]) => {
          const color = CATEGORY_COLORS[key];
          return (
            <div key={key} className={`flex items-center gap-1.5 ${isFull ? 'text-xs' : 'text-[10px]'} font-bold text-slate-500`}>
              <span className={`${isFull ? 'w-3 h-3' : 'w-2.5 h-2.5'} rounded-full border border-white shadow-sm`} style={{ backgroundColor: color }} />
              <span>{label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function DashboardLayout() {
  // Navigation & Wizard Steps
  const [step, setStep] = useState<"login" | "consent" | "survey" | "upload" | "loading" | "dashboard">("login");
  const [activeTab, setActiveTab] = useState<"dashboard" | "realtime" | "persona" | "graph" | "guide" | "contents" | "settings">("dashboard");

  // Auth states
  const [session, setSession] = useState<any>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSignUp, setIsSignUp] = useState(false);
  const [authError, setAuthError] = useState("");

  // Stepper & polling progress
  const [pollingStage, setPollingStage] = useState("queued");
  const [progressPercent, setProgressPercent] = useState(0);
  const [analysisStartTime, setAnalysisStartTime] = useState<number | null>(null);
  const [isReupload, setIsReupload] = useState(false);

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
  const [realtimeData, setRealtimeData] = useState<any>(null);
  const [personaData, setPersonaData] = useState<any>(null);
  const [graphData, setGraphData] = useState<any>(null);
  const [guideData, setGuideData] = useState<any>(null);
  const [contents, setContents] = useState<any>(null);

  // Interactivity states
  const [selectedNode, setSelectedNode] = useState<any | null>(null);
  const [completedMissions, setCompletedMissions] = useState<Set<number>>(new Set());
  const [activeCourse, setActiveCourse] = useState<3 | 7>(3);
  const [isTitlesExpanded, setIsTitlesExpanded] = useState<boolean>(false);

  const ALL_TITLES = [
    { minStreak: 0, title: "알고리즘의 노예 ⛓️", desc: "유튜브 추천의 파도에 휩쓸려 다니는 중입니다." },
    { minStreak: 4, title: "눈을 뜬 여행자 👀", desc: "편향을 인지하고 균형을 찾으려 노력 중입니다." },
    { minStreak: 8, title: "알고리즘 서퍼 🏄", desc: "추천의 파도를 스스로 타기 시작했습니다." },
    { minStreak: 22, title: "디지털 독립군 🦅", desc: "주체적인 콘텐츠 소비의 달인입니다!" }
  ];

  const hasCheckedReport = useRef(false);

  // Auth state monitor
  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session) {
        setSession(session);
        if (!hasCheckedReport.current) {
          hasCheckedReport.current = true;
          checkPreviousReport(session);
        }
      } else {
        setStep("login");
      }
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      if (session) {
        if (!hasCheckedReport.current) {
          hasCheckedReport.current = true;
          checkPreviousReport(session);
        }
      } else {
        setSession(null);
        setStep("login");
        hasCheckedReport.current = false;
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  const checkPreviousReport = async (activeSession: any) => {
    try {
      // 1. Check if the user has signed the consent form
      const consentRes = await fetch(`${API_BASE_URL}/api/consent`, {
        headers: { "Authorization": `Bearer ${activeSession.access_token}` }
      });
      let hasConsented = false;
      if (consentRes.ok) {
        const consentData = await consentRes.json();
        hasConsented = consentData.consented;
      }

      // 2. Check for existing analysis data
      const res = await fetch(`${API_BASE_URL}/api/persona`, {
        headers: { "Authorization": `Bearer ${activeSession.access_token}` }
      });
      if (res.ok) {
        const data = await res.json();
        if (data.dataset_id) {
          await fetchDashboardData(data.dataset_id, activeSession.access_token);
          await fetchTabDetails(activeSession.access_token);
          setDatasetId(data.dataset_id);
          setStep("dashboard");
          setActiveTab("dashboard");
        } else {
          setStep(hasConsented ? "survey" : "consent");
        }
      } else {
        setStep(hasConsented ? "survey" : "consent");
      }
    } catch (e) {
      console.error("Failed to check previous report, starting consent flow", e);
      setStep("consent");
    }
  };

  const handleConsent = async () => {
    if (!session) {
      setStep("survey");
      return;
    }
    try {
      const res = await fetch(`${API_BASE_URL}/api/consent`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${session.access_token}` }
      });
      if (res.ok) {
        setStep("survey");
      } else {
        alert("동의 기록 저장에 실패했습니다. 다시 시도해주세요.");
      }
    } catch (e) {
      console.error(e);
      alert("서버 연결 실패로 동의 처리를 완료할 수 없습니다.");
    }
  };

  // Load backend data if datasetId is set
  const fetchDashboardData = async (id: string, token: string) => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/dashboard/${id}`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Dashboard API error");
      const data = await res.json();
      setScores(data.scores);
      setReport(data.report);
      setContents(data.contents);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchTabDetails = async (token: string) => {
    const headers = { "Authorization": `Bearer ${token}` };

    try {
      const rtRes = await fetch(`${API_BASE_URL}/api/realtime`, { headers });
      if (rtRes.ok) {
        const rtData = await rtRes.json();
        setRealtimeData(rtData);
      }
    } catch (e) {
      console.error("Error loading realtime details:", e);
    }

    try {
      const pRes = await fetch(`${API_BASE_URL}/api/persona`, { headers });
      if (pRes.ok) {
        const pData = await pRes.json();
        setPersonaData(pData);
      }
    } catch (e) {
      console.error("Error loading persona details:", e);
    }

    try {
      const gRes = await fetch(`${API_BASE_URL}/api/graph`, { headers });
      if (gRes.ok) {
        const gData = await gRes.json();
        setGraphData(gData);
      }
    } catch (e) {
      console.error("Error loading graph details:", e);
    }

    try {
      const guRes = await fetch(`${API_BASE_URL}/api/guide`, { headers });
      if (guRes.ok) {
        const guData = await guRes.json();
        setGuideData(guData);
        if (guData.completed_indices) {
          setCompletedMissions(new Set(guData.completed_indices));
        }
      }
    } catch (e) {
      console.error("Error loading guide details:", e);
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

  // Poll background job status
  const pollJobStatus = (id: string, token: string) => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/upload/status/${id}`, {
          headers: { "Authorization": `Bearer ${token}` }
        });
        if (!res.ok) throw new Error("Status query failed");
        const data = await res.json();
        
        setPollingStage(data.current_stage);
        
        if (data.current_stage === "queued") setProgressPercent(15);
        else if (data.current_stage === "parsing") setProgressPercent(35);
        else if (data.current_stage === "enriching") setProgressPercent(60);
        else if (data.current_stage === "scoring") setProgressPercent(80);
        else if (data.current_stage === "report") setProgressPercent(90);
        else if (data.current_stage === "saving") setProgressPercent(95);
        
        if (data.status === "completed") {
          clearInterval(interval);
          setProgressPercent(100);
          await fetchDashboardData(id, token);
          await fetchTabDetails(token);
          setTimeout(() => {
            setDatasetId(id);
            setStep("dashboard");
            setActiveTab("dashboard");
          }, 500);
        } else if (data.status === "failed") {
          clearInterval(interval);
          if (data.current_stage === "P01_DATA_SHORT") {
            // 데이터 부족 판정 → 업로드 화면으로 복귀
            alert("🚨 [판정보류] 업로드한 유튜브 시청 기록이 너무 적습니다(최소 10건 이상 필요). 더 풍부한 데이터로 다시 시청 기록을 내려받아 업로드해주세요.");
            setStep("upload");
          } else {
            // 처리 오류 → 로딩바를 유지하며 재시도 폴링 시작
            // 업로드 화면으로 돌아가지 않고 계속 대기
            setPollingStage("scoring");
            setProgressPercent(80);
            pollJobStatus(data.dataset_id || id, token);
          }
        }
      } catch (e) {
        console.error("Polling error:", e);
      }
    }, 3000);
  };

  // Delete all data and consent logs + account withdrawal
  const handleDeleteAllData = async () => {
    if (!session) return;
    if (!confirm("🚨 정말로 사용자의 전체 시청 원천 데이터와 분석 이력, 동의 기록까지 일괄 영구 삭제하고 회원 탈퇴를 하시겠습니까? 이 작업은 되돌릴 수 없습니다.")) {
      return;
    }

    try {
      // 1. Wipe database entries on the backend
      if (datasetId && datasetId !== "demo-dataset") {
        const res = await fetch(`${API_BASE_URL}/api/datasets/${datasetId}`, {
          method: "DELETE",
          headers: { "Authorization": `Bearer ${session.access_token}` }
        });
        if (!res.ok) throw new Error("Deletion failed");
      }
      
      // 2. Invoke the Postgres security definer function via Supabase RPC to delete user account
      const { error } = await supabase.rpc("delete_user_account");
      if (error) {
        console.error("RPC account deletion error:", error);
        alert("회원 탈퇴 처리 중 오류가 발생했습니다: " + error.message);
      } else {
        alert("✅ 모든 데이터 파기 및 회원 탈퇴 처리가 안전하게 완료되었습니다.");
      }
      
      // 3. Log out and clean all states
      await supabase.auth.signOut();
      setDatasetId(null);
      setScores(null);
      setReport(null);
      setFile(null);
      setSession(null);
      setStep("login");
    } catch (e) {
      console.error(e);
      alert("❌ 계정 탈퇴 및 데이터 삭제 처리에 실패했습니다. 서버 상태를 확인해주세요.");
    }
  };

  // Reset all data for current user (preserving account)
  const handleResetDataOnly = async () => {
    if (!session) return;
    if (!confirm("🚨 정말로 로그인 상태는 유지한 채 사용자의 모든 시청 원천 데이터와 분석 이력, 동의 기록만 일괄 영구 삭제하고 초기화하시겠습니까? 이 작업은 되돌릴 수 없습니다.")) {
      return;
    }

    try {
      const res = await fetch(`${API_BASE_URL}/api/reset`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${session.access_token}` }
      });
      if (!res.ok) throw new Error("Data reset failed");
      
      alert("✅ 모든 데이터가 성공적으로 초기화되었습니다.");
      
      // Reset all states
      setDatasetId(null);
      setScores(null);
      setReport(null);
      setFile(null);
      setPollingStage("queued");
      setProgressPercent(0);
      setAnalysisStartTime(null);
      setIsReupload(false);
      
      // Redirect to onboarding consent screen
      setStep("consent");
    } catch (e) {
      console.error(e);
      alert("❌ 데이터 초기화 처리에 실패했습니다. 서버 상태를 확인해주세요.");
    }
  };

  // Perform backend analysis
  const handleStartAnalysis = async () => {
    if (!selectedFile) return;
    if (!session) {
      alert("로그인이 세션이 유효하지 않습니다. 다시 로그인해주세요.");
      return;
    }
    
    setStep("loading");
    setPollingStage("queued");
    setProgressPercent(10);
    setAnalysisStartTime(Date.now());
    setIsReupload(false);

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const res = await fetch(`${API_BASE_URL}/api/upload/`, {
        method: "POST",
        body: formData,
        headers: {
          "Authorization": `Bearer ${session.access_token}`
        }
      });

      if (!res.ok) throw new Error("Backend upload failed");
      const uploadResult = await res.json();
      const id = uploadResult.dataset_id;

      pollJobStatus(id, session.access_token);
    } catch (e) {
      console.error("Backend upload error:", e);
      alert("🚨 파일 분석 업로드에 실패했습니다. 서버 상태를 확인하거나 잠시 후 다시 시도해 주세요.");
      setStep("upload");
    }
  };

  // Helper variables for Recharts mapping
  const mbtiData = [
    { subject: '주제 다양성(TDS)', A: scores?.tds || scores?.diversity || 0 },
    { subject: '출처 균형(SBS)', A: scores?.sbs || scores?.diversity || 0 },
    { subject: '감정 균형(EBS)', A: scores?.ebs || scores?.stability || 0 },
    { subject: '관점 개방(VOS)', A: scores?.vos || scores?.openness || 0 },
    { subject: '유해 안전(SMS)', A: scores?.sms || scores?.stability || 0 },
    { subject: '사용자 주도(UAS)', A: scores?.uas || scores?.proactivity || 0 }
  ];

  const rawInterests = contents?.top_interests;
  let displayInterests: any[] | null = null;
  let noCategorizedData = false;
  let isInterestsMissing = false;

  if (rawInterests !== undefined && rawInterests !== null) {
    if (rawInterests.length === 0) {
      noCategorizedData = true;
    } else {
      displayInterests = [...rawInterests];
      while (displayInterests.length < 5) {
        displayInterests.push({
          name: '데이터 부족',
          percentage: 0,
          color: '#CBD5E1'
        });
      }
    }
  } else {
    isInterestsMissing = true;
  }

  const timelineData = realtimeData?.timeline_data || [];

  const barData = personaData?.history || [];

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



  // Checklist handler
  const handleMissionCheck = async (idx: number) => {
    // 1. 상태 업데이트 전, 현재 값을 바탕으로 새 배열 계산 (비동기 안전성)
    const nextSet = new Set(completedMissions);
    if (nextSet.has(idx)) nextSet.delete(idx);
    else nextSet.add(idx);
    
    const nextArr = Array.from(nextSet);
    
    // 2. UI 상태 즉시 업데이트
    setCompletedMissions(nextSet);
    
    // 3. 백엔드 동기화 (최신 배열 사용)
    if (session) {
      try {
        const res = await fetch(`${API_BASE_URL}/api/guide/sync`, {
          method: 'POST',
          headers: {
            "Authorization": `Bearer ${session.access_token}`,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ completed_indices: nextArr })
        });
        if (res.ok) {
          const data = await res.json();
          setGuideData((prev: any) => ({ ...prev, streak_days: data.current_streak }));
          
          // Milestone Popup Check
          if (data.current_streak > 0 && data.current_streak % 7 === 0 && nextArr.length === (report?.missions?.length || 3)) {
            setTimeout(() => {
              alert(`🎉 축하합니다! ${data.current_streak}일 연속 디톡스 마일스톤 달성!\n\n💡 오늘의 디톡스 시크릿 팁:\n유튜브 알고리즘은 당신의 '체류 시간'을 먹고 자랍니다. 지금처럼 주도적인 검색 습관을 계속 유지하세요!`);
            }, 600);
          }
        }
      } catch (e) {
        console.error("Failed to sync missions", e);
      }
    }
  };

  const getSuggestedQuery = (m: any) => {
    if (m.suggested_query) return m.suggested_query;
    if (m.mission_type === "역방향 쿼리") return "기후 변화 다큐멘터리";
    if (m.mission_type === "출처 전환") return "글로벌 경제 심층 인터뷰";
    if (m.mission_type === "주도성 회복") return "내가 진짜 알고싶은 취미";
    if (m.mission_type === "비구독 채널 탐색") return "글로벌 매크로 경제";
    if (m.mission_type === "숏폼 탈출") return "집중력을 올리는 10가지 방법";
    return m.mission_type;
  };

  const getStreakDays = () => {
    return guideData?.streak_days || 0;
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
                { tab: 'realtime', icon: <Activity size={20}/>, label: '시청 습관' },
                { tab: 'persona', icon: <PieChartIcon size={20}/>, label: '성향 분석' },
                { tab: 'graph', icon: <Network size={20}/>, label: '관심사 지식 그래프' },
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
              <li 
                title="설정" 
                onClick={() => { if (datasetId) setActiveTab('settings'); }}
                className={`px-4 xl:px-6 py-4 font-bold flex items-center gap-3 cursor-pointer justify-center xl:justify-start transition-colors
                  ${!datasetId ? 'opacity-50 cursor-not-allowed' : ''}
                  ${activeTab === 'settings' && datasetId ? 'bg-indigo-600' : 'hover:bg-white/10'}`}
              >
                <Settings size={20}/><span className="hidden xl:inline">설정</span>
              </li>
            </ul>
          </nav>
        </div>
        <div className="p-4 xl:p-6 border-t border-white/10 flex items-center gap-3 justify-center xl:justify-start">
          <div className="w-8 h-8 xl:w-10 xl:h-10 rounded-full bg-slate-600 flex-shrink-0"></div>
          <div className="hidden xl:block">
            <div className="font-bold text-sm truncate max-w-[120px]" title={session?.user?.email}>
              {session?.user?.email ? session.user.email.split('@')[0] : '홍길동'} 님
            </div>
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
              {activeTab === 'realtime' && '시청 습관'}
              {activeTab === 'persona' && '심층 성향 분석'}
              {activeTab === 'graph' && '관심사 지식 그래프'}
              {activeTab === 'guide' && '디톡스 가이드'}
              {activeTab === 'contents' && '콘텐츠 세부 분석'}
              {activeTab === 'settings' && '설정 및 관리'}
            </h1>
            <p className="text-sm text-slate-500">AI가 분석한 당신의 콘텐츠 소비 패턴을 확인하세요.</p>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() => {
                setIsReupload(true);
                setStep("upload");
              }}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-semibold transition-colors shadow-sm"
              title="새로운 데이터 재업로드"
            >
              <UploadCloud size={16} /> 재업로드
            </button>
            <Bell className="text-slate-500 cursor-pointer hover:text-slate-700 transition-colors" onClick={() => alert("알림: 새로운 분석 리포트가 도착했습니다!")} />
            <div className="border border-slate-300 rounded-lg px-4 py-2 text-sm font-semibold flex items-center gap-2 cursor-pointer hover:bg-slate-50 transition-colors" onClick={() => alert("기간 설정 기능은 프로 버전에서 제공됩니다.")}>
              <Calendar size={16} /> 2026.05.14 ~ 2026.05.20
            </div>
          </div>
        </header>

        {/* Content Area — C: 가로 스크롤 허용, 최소 너비 확보 */}
        <div className="flex-1 overflow-y-auto overflow-x-auto p-4 xl:p-8 relative">
          
          {/* STEP 0: LOGIN */}
          {step === "login" && (
            <div className="absolute inset-0 bg-[#0F172A] z-50 flex items-center justify-center p-8">
              <div className="bg-slate-900 border border-slate-800 p-10 rounded-2xl shadow-2xl w-full max-w-md text-left">
                <div className="text-center mb-8">
                  <div className="text-4xl mb-3">🧘</div>
                  <h2 className="text-2xl font-bold text-white mb-2">언블리버블 v2 디톡스</h2>
                  <p className="text-slate-400 text-sm">유튜브 필터버블 분석 및 도파민 치료 솔루션</p>
                </div>
                
                <div className="space-y-4">
                  {authError && (
                    <div className="bg-red-500/10 border border-red-500/20 text-red-400 text-xs p-3 rounded-lg text-center font-bold">
                      {authError}
                    </div>
                  )}
                  
                  <div>
                    <label className="text-slate-400 text-xs font-semibold block mb-2">이메일 주소</label>
                    <input 
                      type="email" 
                      placeholder="name@example.com" 
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500 text-sm"
                    />
                  </div>
                  
                  <div>
                    <label className="text-slate-400 text-xs font-semibold block mb-2">비밀번호</label>
                    <input 
                      type="password" 
                      placeholder="••••••••" 
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500 text-sm"
                    />
                  </div>
                  
                  <button 
                    onClick={async () => {
                      setAuthError("");
                      try {
                        if (isSignUp) {
                          const { error } = await supabase.auth.signUp({ email, password });
                          if (error) throw error;
                          alert("회원가입 요청이 성공했습니다. 이메일 링크를 확인하시거나 로그인해주세요.");
                          setIsSignUp(false);
                        } else {
                          const { error } = await supabase.auth.signInWithPassword({ email, password });
                          if (error) throw error;
                        }
                      } catch (err: any) {
                        setAuthError(err.message || "인증 처리 중 오류가 발생했습니다.");
                      }
                    }}
                    className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 rounded-xl transition-colors mt-2 text-sm"
                  >
                    {isSignUp ? "회원가입 완료" : "로그인"}
                  </button>
                  
                  <div className="text-center pt-4 border-t border-slate-800/60 mt-4">
                    <button 
                      onClick={() => setIsSignUp(!isSignUp)}
                      className="text-indigo-400 text-xs hover:underline font-semibold"
                    >
                      {isSignUp ? "이미 계정이 있으신가요? 로그인하기" : "아직 계정이 없으신가요? 회원가입하기"}
                    </button>
                  </div>
                  
                  <div className="text-center pt-2">
                    <button 
                      onClick={() => {
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
                        setRealtimeData({
                          time_distribution: [
                            { hour: "09:00", total: 10, dopamine: 2 },
                            { hour: "12:00", total: 15, dopamine: 14 },
                            { hour: "15:00", total: 12, dopamine: 10 },
                            { hour: "18:00", total: 20, dopamine: 5 },
                            { hour: "21:00", total: 8, dopamine: 7 }
                          ],
                          peak_message: "당신은 11시부터 13시 사이에 도파민성 콘텐츠 시청률이 가장 높게 치솟습니다! 루틴 관리가 필요해요.",
                          binge_sessions: [
                            {
                              date: "2024년 5월 15일",
                              time_range: "12:20 ~ 16:40",
                              duration_str: "4시간 20분",
                              video_count: 45,
                              main_keyword: "사건사고 뉴스",
                              message: "무려 4시간 20분 동안 '사건사고 뉴스' 위주로 연속 시청했습니다."
                            }
                          ],
                          timeline_data: [
                            { date: '05/14', 편향위험도: 85, top_keyword: '정치/사회 비평' },
                            { date: '05/15', 편향위험도: 90, top_keyword: '사건사고/이슈' },
                            { date: '05/16', 편향위험도: 95, top_keyword: '자극성 예능 숏폼' },
                            { date: '05/17', 편향위험도: 78, top_keyword: '연예/가십' },
                            { date: '05/18', 편향위험도: 90, top_keyword: '정치/사회 비평' },
                            { date: '05/19', 편향위험도: 68, top_keyword: '영화/드라마 리뷰' },
                            { date: '05/20', 편향위험도: 72, top_keyword: 'IT/테크 리뷰' }
                          ]
                        });
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
                      }}
                      className="text-slate-500 hover:text-slate-300 text-xs hover:underline font-semibold"
                    >
                      데모 모드로 체험하기 (로그인 우회)
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

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
                  onClick={handleConsent}
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
                {isReupload && (
                  <div className="w-full bg-indigo-50 border border-indigo-200 text-indigo-700 text-xs font-semibold rounded-xl px-4 py-3 mb-4 text-center">
                    🔄 새 데이터를 업로드하여 디톡스 분석 결과를 업데이트합니다.<br />
                    완료 시 이전 결과와 함께 추이가 비교 누적됩니다.
                  </div>
                )}
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
                {isReupload && (
                  <button
                    type="button"
                    onClick={() => {
                      setIsReupload(false);
                      setStep("dashboard");
                    }}
                    className="w-full bg-slate-100 text-slate-700 hover:bg-slate-200 font-bold py-2.5 rounded-xl transition-colors text-xs mb-3"
                  >
                    취소하고 대시보드로 돌아가기
                  </button>
                )}
                <button
                  type="button"
                  id="btn-demo-mode"
                  onClick={() => {
                    setStep("loading");
                    setPollingStage("queued");
                    setProgressPercent(15);
                    
                    setTimeout(() => {
                      setPollingStage("parsing");
                      setProgressPercent(35);
                    }, 400);
                    
                    setTimeout(() => {
                      setPollingStage("enriching");
                      setProgressPercent(60);
                    }, 800);
                    
                    setTimeout(() => {
                      setPollingStage("scoring");
                      setProgressPercent(80);
                    }, 1200);
                    
                    setTimeout(() => {
                      setPollingStage("report");
                      setProgressPercent(90);
                    }, 1600);
                    
                    setTimeout(() => {
                      setPollingStage("saving");
                      setProgressPercent(95);
                    }, 2000);
                    
                    setTimeout(() => {
                      setProgressPercent(100);
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
                          { mission_type: "역방향 쿼리", description: "인공지능의 윤리적 문제와 규제 필요성 영상을 검색하여 10분 이상 시청합니다.", success_condition: "관련 검색어로 동영상 시청 완료", suggested_query: "인공지능 윤리와 위험성" },
                          { mission_type: "비구독 채널 탐색", description: "평소 전혀 구독하지 않는 경제 분야 인기 채널의 영상을 1개 시청합니다.", success_condition: "영상 시청 완료", suggested_query: "글로벌 매크로 경제" },
                          { mission_type: "숏폼 탈출", description: "오늘 하루 유튜브 숏츠 시청 시간을 30분 이내로 조절합니다.", success_condition: "숏츠 시청 제한 달성", suggested_query: "집중력을 올리는 10가지 방법" }
                        ]
                      });
                      setRealtimeData({
                        time_distribution: [
                          { hour: "09:00", total: 10, dopamine: 2 },
                          { hour: "12:00", total: 15, dopamine: 14 },
                          { hour: "15:00", total: 12, dopamine: 10 },
                          { hour: "18:00", total: 20, dopamine: 5 },
                          { hour: "21:00", total: 8, dopamine: 7 }
                        ],
                        peak_message: "당신은 11시부터 13시 사이에 도파민성 콘텐츠 시청률이 가장 높게 치솟습니다! 루틴 관리가 필요해요.",
                        binge_sessions: [
                          {
                            date: "2024년 5월 15일",
                            time_range: "12:20 ~ 16:40",
                            duration_str: "4시간 20분",
                            video_count: 45,
                            main_keyword: "사건사고 뉴스",
                            message: "무려 4시간 20분 동안 '사건사고 뉴스' 위주로 연속 시청했습니다."
                          }
                        ],
                        timeline_data: [
                          { date: '05/14', 편향위험도: 85, top_keyword: '정치/사회 비평' },
                          { date: '05/15', 편향위험도: 90, top_keyword: '사건사고/이슈' },
                          { date: '05/16', 편향위험도: 95, top_keyword: '자극성 예능 숏폼' },
                          { date: '05/17', 편향위험도: 78, top_keyword: '연예/가십' },
                          { date: '05/18', 편향위험도: 90, top_keyword: '정치/사회 비평' },
                          { date: '05/19', 편향위험도: 68, top_keyword: '영화/드라마 리뷰' },
                          { date: '05/20', 편향위험도: 72, top_keyword: 'IT/테크 리뷰' }
                        ]
                      });
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
                    }, 2400);
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
              <div className="bg-white p-10 rounded-2xl shadow-xl w-full max-w-lg text-left">
                <h2 className="text-2xl font-bold text-slate-900 mb-2 text-center">유튜브 알고리즘 분석 중</h2>
                <p className="text-slate-500 mb-6 text-sm text-center">업로드된 시청 이력 데이터를 정밀 분석하고 있습니다.</p>
                
                {/* Progress Bar */}
                <div className="w-full bg-slate-100 rounded-full h-3 mb-6 overflow-hidden">
                  <div className="bg-indigo-600 h-full transition-all duration-500 rounded-full" style={{ width: `${progressPercent}%` }}></div>
                </div>
                
                {/* Stage Stepper UI */}
                <div className="space-y-4 mb-6">
                  {[
                    { key: "parsing", label: "1. 유튜브 시청 기록 파일 파싱" },
                    { key: "enriching", label: "2. 채널 및 동영상 카테고리 분류" },
                    { key: "scoring", label: "3. 6축 편향성 지수 연산 및 점수화" },
                    { key: "report", label: "4. AI 디톡스 치료 처방 코멘트 작성" }
                  ].map((stage, idx) => {
                    const stagesOrder = ["queued", "parsing", "enriching", "scoring", "report", "saving", "completed"];
                    const currentIdx = stagesOrder.indexOf(pollingStage);
                    const stageIdx = stagesOrder.indexOf(stage.key);
                    
                    let statusColor = "text-slate-400";
                    let icon = <span className="w-4 h-4 rounded-full border border-slate-300 inline-block"></span>;
                    
                    if (currentIdx > stageIdx) {
                      statusColor = "text-emerald-600 font-semibold";
                      icon = <span className="text-emerald-600 font-bold">✓</span>;
                    } else if (pollingStage === stage.key) {
                      statusColor = "text-indigo-600 font-bold animate-pulse";
                      icon = <span className="w-4 h-4 rounded-full border-2 border-indigo-600 border-t-transparent animate-spin inline-block"></span>;
                    }
                    
                    return (
                      <div key={idx} className="flex items-center gap-3 text-sm">
                        <div className="w-6 h-6 flex items-center justify-center font-bold text-xs">{icon}</div>
                        <span className={statusColor}>{stage.label}</span>
                      </div>
                    );
                  })}
                </div>
                
                <div className="text-center text-indigo-600 font-extrabold">{progressPercent}% 진행 중</div>
                <ElapsedTimeDisplay startTime={analysisStartTime} pollingStage={pollingStage} />
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
                    <h3 className="font-bold text-slate-900 mb-4 flex items-center gap-2">
                      편향 위험도 (조종 지수)
                      <div className="group relative inline-block">
                        <span className="text-slate-400 hover:text-indigo-500 cursor-help flex items-center justify-center w-5 h-5 rounded-full border border-slate-300 text-[10px]">?</span>
                        <div className="absolute hidden group-hover:block w-64 bg-slate-800 text-white text-xs rounded-xl p-4 -top-2 left-8 z-50 shadow-xl pointer-events-none font-normal">
                          <strong className="block mb-2 text-indigo-300">💡 BRS 산출 공식</strong>
                          <p className="mb-2 leading-relaxed">
                            AI가 분석한 6가지 지표를 가중 평균하여 100점에서 뺀 수치입니다. (높을수록 위험)
                          </p>
                          <ul className="text-[10px] text-slate-300 space-y-1 bg-slate-900/50 p-2 rounded-lg">
                            <li>• 주제 다양성 (20%), 관점 개방성 (20%)</li>
                            <li>• 출처 균형 (15%), 감정 균형 (15%)</li>
                            <li>• 유해 안전성 (15%), 사용자 주도성 (15%)</li>
                          </ul>
                        </div>
                      </div>
                    </h3>
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
                    <h3 className="font-bold text-slate-900 mb-4 flex items-center gap-2">
                      알고리즘 성향 (DSAO)
                      <div className="group relative inline-block">
                        <span className="text-slate-400 hover:text-indigo-500 cursor-help flex items-center justify-center w-5 h-5 rounded-full border border-slate-300 text-[10px]">?</span>
                        <div className="absolute hidden group-hover:block w-64 bg-slate-800 text-white text-xs rounded-xl p-4 -top-2 left-8 z-50 shadow-xl pointer-events-none font-normal">
                          <strong className="block mb-2 text-indigo-300">💡 DSAO 분류 기준</strong>
                          <p className="mb-2 leading-relaxed">
                            MBTI처럼 시청 패턴을 16가지 유형으로 분류합니다.
                          </p>
                          <ul className="text-[10px] text-slate-300 space-y-1 bg-slate-900/50 p-2 rounded-lg">
                            <li>• <b>D / P</b> : 직접 검색(D) vs 수동적 추천(P)</li>
                            <li>• <b>W / N</b> : 넓은 주제(W) vs 좁은 주제(N)</li>
                            <li>• <b>S / M</b> : 자극적 성향(S) vs 안정적 성향(M)</li>
                            <li>• <b>F / L</b> : 짧고 빠른(F) vs 깊고 긴(L)</li>
                          </ul>
                        </div>
                      </div>
                    </h3>
                    <div className="flex-1 flex items-center justify-between">
                      <div className="flex-1 pr-2 min-w-0">
                        <div className="flex items-center gap-2 mb-1 flex-wrap">
                          <span className="text-3xl font-black text-slate-950">{personaType}</span>
                          <span className="text-2xl">{dsao.character}</span>
                          {scores && scores.persona_type !== "UNKN" && scores.confidence !== undefined && (
                            <span className={`text-[9px] font-black px-1.5 py-0.5 rounded-full ml-1 ${
                              scores.data_quality === "high" ? "bg-emerald-100 text-emerald-700" :
                              scores.data_quality === "medium" ? "bg-amber-100 text-amber-700" :
                              "bg-red-100 text-red-700"
                            }`}>
                              신뢰도 {Math.round(scores.confidence * 100)}%
                            </span>
                          )}
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

                  <div className="bg-white rounded-2xl shadow-sm p-5 min-h-[240px] xl:min-h-[280px] flex flex-col justify-between">
                    <div>
                      <h3 className="font-bold text-slate-900 mb-4">최근 주요 관심사 TOP 5</h3>
                      {isInterestsMissing ? (
                        <div className="flex flex-col justify-center items-center py-8 text-center px-4">
                          <span className="text-3xl mb-2">🔄</span>
                          <p className="text-xs font-bold text-slate-500 leading-relaxed">
                            분석 데이터를 불러오지 못했거나<br />결과가 존재하지 않습니다.
                          </p>
                        </div>
                      ) : noCategorizedData ? (
                        <div className="flex flex-col justify-center items-center py-8 text-center px-4">
                          <span className="text-3xl mb-2">📊</span>
                          <p className="text-xs font-bold text-slate-500 leading-relaxed">
                            충분한 분류 데이터가 부족하여<br />주요 관심사를 산출할 수 없습니다.
                          </p>
                        </div>
                      ) : (
                        <div className="space-y-4">
                          {displayInterests?.map((item: any, i: number) => (
                            <div key={i} className="flex items-center gap-3">
                              <div className="w-8 h-8 rounded-full text-white flex items-center justify-center text-xs font-bold" style={{ backgroundColor: item.color }}>
                                {item.name.charAt(0)}
                              </div>
                              <div className="flex-1">
                                <div className="flex justify-between text-xs font-semibold text-slate-900 mb-1">
                                  <span>{i + 1}. {item.name}</span>
                                  <span>{item.percentage}%</span>
                                </div>
                                <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                                  <div className="h-full rounded-full transition-all duration-500" style={{ width: `${item.percentage}%`, backgroundColor: item.color }}></div>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                    {contents?.uncategorized && (
                      <div className="mt-4 pt-3 border-t border-slate-100 space-y-1">
                        <div className="flex items-center justify-between text-xs text-slate-500">
                          <span className="flex items-center gap-1 font-medium">
                            🔍 분류되지 않은 시청 기록
                          </span>
                          <span className="font-black text-slate-700 bg-slate-100 px-2 py-0.5 rounded-full">
                            {contents.uncategorized.percentage}%
                          </span>
                        </div>
                        {contents.uncategorized.percentage > 20 && (
                          <p className="text-[10px] text-slate-400 leading-snug">
                            ℹ️ {contents.uncategorized.message}
                          </p>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Middle Row — B: 전체 너비 */}
                  <div className="md:col-span-2 xl:col-span-3 bg-white rounded-2xl shadow-sm p-5">
                    <div className="mb-6">
                      <h3 className="font-bold text-slate-900 flex items-center gap-2">
                        관심사 편향 변화 (타임라인)
                        <span className="text-xs bg-red-50 text-red-600 px-2 py-1 rounded font-bold">높을수록 나쁨 🚨</span>
                        <div className="group relative inline-block">
                          <span className="text-slate-400 hover:text-indigo-500 cursor-help flex items-center justify-center w-5 h-5 rounded-full border border-slate-300 text-[10px]">?</span>
                          <div className="absolute hidden group-hover:block w-64 bg-slate-800 text-white text-xs rounded-xl p-4 -top-2 left-8 z-50 shadow-xl pointer-events-none font-normal">
                            <strong className="block mb-2 text-indigo-300">💡 BRS 산출 공식</strong>
                            <p className="mb-2 leading-relaxed">
                              AI가 분석한 6가지 지표를 가중 평균하여 100점에서 뺀 수치입니다. (높을수록 위험)
                            </p>
                            <ul className="text-[10px] text-slate-300 space-y-1 bg-slate-900/50 p-2 rounded-lg">
                              <li>• 주제 다양성 (20%), 관점 개방성 (20%)</li>
                              <li>• 출처 균형 (15%), 감정 균형 (15%)</li>
                              <li>• 유해 안전성 (15%), 사용자 주도성 (15%)</li>
                            </ul>
                          </div>
                        </div>
                      </h3>
                      <p className="text-xs text-slate-500 mt-1">
                        과거부터 현재까지의 '편향 위험도(BRS)' 추이입니다. 숫자가 높을수록 알고리즘에 갇혀 한쪽으로 치우친 시청을 하고 있다는 의미입니다.
                      </p>
                    </div>
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
                          <YAxis axisLine={false} tickLine={false} tick={{fill: '#94A3B8', fontSize: 12}} domain={[0, 100]} />
                          <Tooltip 
                            content={({ active, payload, label }: any) => {
                              if (active && payload && payload.length) {
                                return (
                                  <div className="bg-slate-800 text-white text-xs rounded-xl p-3 shadow-xl">
                                    <p className="font-bold mb-1 text-slate-400">{label}</p>
                                    <p className="font-bold text-indigo-300 mb-2">편향 위험도(BRS): <span className="text-white text-sm">{payload[0].value}</span></p>
                                    <div className="bg-slate-900/50 rounded p-2 border border-slate-700">
                                      <span className="text-slate-400 block mb-0.5 text-[10px]">주요 시청 관심사</span>
                                      <span className="text-white font-semibold">🎬 {payload[0].payload.top_keyword}</span>
                                    </div>
                                  </div>
                                );
                              }
                              return null;
                            }}
                          />
                          <Area type="monotone" dataKey="편향위험도" stroke="#475569" fillOpacity={1} fill="url(#colorScore)" />
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
                    <div className="flex-1 bg-white rounded-xl overflow-hidden flex items-center justify-center">
                      {graphData?.state === "empty" || !graphData?.nodes || graphData.nodes.length === 0 ? (
                        <div className="text-center text-slate-400 p-6 flex flex-col items-center justify-center">
                          <span className="text-3xl mb-2">🌐</span>
                          <p className="text-xs font-semibold leading-relaxed">분석된 관심사 데이터가 부족하거나 존재하지 않아 지식 그래프를 렌더링할 수 없습니다.</p>
                        </div>
                      ) : (
                        <InteractiveForceGraph graphData={graphData} setSelectedNode={setSelectedNode} variant="mini" />
                      )}
                    </div>
                  </div>

                  <div className="md:col-span-1 xl:col-span-2 bg-white rounded-2xl shadow-sm p-5 min-h-[320px] xl:min-h-[400px] flex flex-col">
                    <div className="flex justify-between items-center mb-2">
                      <h3 className="font-bold text-slate-900">디톡스 미션</h3>
                      <span className="text-xs text-indigo-600 font-bold hover:underline cursor-pointer" onClick={() => setActiveTab("guide")}>전체 보기 &gt;</span>
                    </div>
                    <div className="flex gap-6 items-center flex-1">
                      <div className="relative w-40 h-40 flex items-center justify-center">
                        <ResponsiveContainer width="100%" height="100%">
                          <RePieChart>
                            <Pie 
                              data={[
                                { value: completedMissions.size }, 
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
                        {report?.missions?.map((m: any, idx: number) => {
                          const isCompleted = completedMissions.has(idx);
                          return (
                            <div 
                              key={idx} 
                              onClick={() => {
                                handleMissionCheck(idx);
                                window.open(`https://www.youtube.com/results?search_query=${encodeURIComponent(getSuggestedQuery(m))}`, '_blank');
                              }}
                              className={`flex items-center gap-3 p-3 border rounded-lg cursor-pointer transition-colors ${
                                isCompleted 
                                  ? 'bg-emerald-50 border-emerald-100 text-emerald-800' 
                                  : 'bg-slate-50 border-slate-100 text-slate-700 hover:bg-slate-100/70'
                              }`}
                            >
                              <div className={`w-3 h-3 rounded-full border flex items-center justify-center flex-shrink-0 ${
                                isCompleted ? 'bg-emerald-500 border-emerald-500 text-white' : 'border-slate-300 bg-white'
                              }`}>
                                {isCompleted && <span className="text-[8px] font-bold leading-none">✓</span>}
                              </div>
                              <div className={`flex-1 text-xs font-semibold truncate ${isCompleted ? 'text-emerald-600' : 'text-slate-700'}`}>
                                {getSuggestedQuery(m)}
                              </div>
                              <span 
                                onClick={(e) => {
                                  e.stopPropagation();
                                  window.open(`https://www.youtube.com/results?search_query=${encodeURIComponent(getSuggestedQuery(m))}`, '_blank');
                                }}
                                className={`text-[10px] px-2 py-0.5 rounded font-bold transition-colors ${
                                  isCompleted ? 'text-emerald-600 bg-emerald-100 hover:bg-emerald-200' : 'text-indigo-600 bg-indigo-50 hover:bg-indigo-100'
                                }`}
                              >
                                검색
                              </span>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* === REALTIME TAB === */}
              {activeTab === 'realtime' && (
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 xl:gap-6">
                  {/* Left Column: Peak message & Bar chart */}
                  <div className="flex flex-col gap-4 xl:gap-6">
                    {/* Peak Message Alert */}
                    <div className="bg-red-50 border-l-4 border-red-500 rounded-r-2xl p-6 shadow-sm relative overflow-hidden">
                      <div className="absolute top-0 right-0 p-4 opacity-10 text-4xl">🚨</div>
                      <h3 className="font-bold text-red-900 mb-2 flex items-center gap-2">
                        <span className="text-xl">⚠️</span> 취약 시간대 경고
                      </h3>
                      <p className="text-red-800 font-medium leading-relaxed">
                        {realtimeData?.peak_message || "분석 중입니다..."}
                      </p>
                    </div>
                    
                    {/* Bar Chart for 24h Habit */}
                    <div className="bg-white rounded-2xl shadow-sm p-6 flex-1 border border-slate-100">
                      <h3 className="font-bold text-slate-900 mb-6 flex items-center justify-between">
                        <span>나의 24시간 시청 생체리듬</span>
                        <span className="text-xs font-normal text-slate-400">총 시청 vs 고도파민 시청</span>
                      </h3>
                      <div className="w-full h-72">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={realtimeData?.time_distribution || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                            <XAxis dataKey="hour" axisLine={false} tickLine={false} tick={{fontSize: 12, fill: '#94a3b8'}} />
                            <YAxis axisLine={false} tickLine={false} tick={{fontSize: 12, fill: '#94a3b8'}} />
                            <Tooltip cursor={{fill: '#f8fafc'}} contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} />
                            <Bar dataKey="total" name="전체 시청" fill="#e2e8f0" radius={[4, 4, 0, 0]} barSize={20} />
                            <Bar dataKey="dopamine" name="고도파민 시청" fill="#ef4444" radius={[4, 4, 0, 0]} barSize={20} />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  </div>
                  
                  {/* Right Column: Binge Sessions */}
                  <div className="flex flex-col gap-4 xl:gap-6">
                    <div className="bg-white rounded-2xl shadow-sm p-6 flex-1 border border-slate-100">
                      <div className="flex items-center justify-between mb-6">
                        <h3 className="font-bold text-slate-900 flex items-center gap-2">
                          <span className="text-xl">🍿</span> 최악의 도파민 폭식 세션
                        </h3>
                      </div>
                      
                      <div className="space-y-4">
                        {realtimeData?.binge_sessions?.length > 0 ? (
                          realtimeData.binge_sessions.map((session: any, idx: number) => (
                            <div key={idx} className="bg-slate-50 border border-slate-100 rounded-xl p-5 hover:border-red-200 hover:shadow-sm transition-all group">
                              <div className="flex items-start justify-between mb-3">
                                <div>
                                  <div className="text-xs font-bold text-slate-400 mb-1">{session.date} • {session.time_range}</div>
                                  <h4 className="font-bold text-slate-800 text-lg group-hover:text-red-600 transition-colors">
                                    {session.duration_str} 연속 시청
                                  </h4>
                                </div>
                                <div className="bg-red-100 text-red-600 text-xs font-bold px-3 py-1.5 rounded-full flex items-center gap-1">
                                  <span>🔥</span> {session.video_count}개 시청
                                </div>
                              </div>
                              
                              <div className="bg-white rounded-lg p-3 border border-slate-100 flex items-start gap-3">
                                <div className="text-2xl mt-1">🕵️</div>
                                <div>
                                  <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-0.5">주범 키워드 / 채널</div>
                                  <div className="text-sm font-bold text-slate-700">{session.message}</div>
                                </div>
                              </div>
                            </div>
                          ))
                        ) : (
                          <div className="text-center py-12 text-slate-400">
                            <span className="text-4xl block mb-3">🌱</span>
                            <p>연속 시청 기록이 없습니다. 아주 훌륭해요!</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* === PERSONA TAB === */}
              {activeTab === 'persona' && (
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 xl:gap-6">
                  <div className="flex flex-col gap-4 xl:gap-6">
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

                    {/* 지난 분석 대비 변화 추이 카드 */}
                    <div className="bg-white rounded-2xl shadow-sm p-6">
                      <h3 className="font-bold text-slate-900 mb-4">🔄 지난 분석 대비 시청 습관 변화</h3>
                      <div className="space-y-3">
                        {personaData?.comparison_statements && personaData.comparison_statements.length > 0 ? (
                          personaData.comparison_statements.map((stmt: string, idx: number) => {
                            const isPositive = stmt.includes("상승") || stmt.includes("개선") || (stmt.includes("감소") && (stmt.includes("유해") || stmt.includes("위험도")));
                            const isWarning = stmt.includes("의존도") || stmt.includes("늘어") || stmt.includes("경보") || stmt.includes("좁아지는");
                            let cardBg = "bg-slate-50 border-slate-100 text-slate-700";
                            if (isPositive) cardBg = "bg-emerald-50/50 border-emerald-100 text-emerald-800";
                            else if (isWarning) cardBg = "bg-amber-50/50 border-amber-100 text-amber-800";

                            return (
                              <div key={idx} className={`p-3.5 rounded-xl border text-xs font-semibold leading-relaxed flex items-start gap-2.5 ${cardBg}`}>
                                <span className="text-sm mt-0.5">ℹ️</span>
                                <div>{stmt}</div>
                              </div>
                            );
                          })
                        ) : (
                          <div className="text-slate-400 text-xs text-center py-4">
                            이전 분석 이력이 존재하지 않거나 변동 사항이 없습니다.
                          </div>
                        )}
                      </div>
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
                      <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
                        <h3 className="font-bold text-slate-900">알고리즘 성향 상세 분석 ({personaType})</h3>
                        {personaData && personaData.type !== "UNKN" && personaData.confidence !== undefined && (
                          <div className="flex items-center gap-1.5">
                            <span className={`text-[10px] font-black px-2 py-0.5 rounded-full ${
                              personaData.data_quality === "high" ? "bg-emerald-100 text-emerald-700" :
                              personaData.data_quality === "medium" ? "bg-amber-100 text-amber-700" :
                              "bg-red-100 text-red-700"
                            }`}>
                              데이터 등급: {personaData.data_quality === "high" ? "상" : personaData.data_quality === "medium" ? "중" : "하"}
                            </span>
                            <span className="text-[10px] text-slate-500 font-bold">
                              AI 신뢰도: {Math.round(personaData.confidence * 100)}%
                            </span>
                          </div>
                        )}
                      </div>
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
                    <h3 className="font-bold text-slate-900">관심사 지식 그래프</h3>
                    <div className="text-xs text-slate-400">노드를 클릭하여 세부 분석 및 조종 위험도를 체크하세요.</div>
                  </div>
                  <div className="w-full bg-white rounded-2xl flex items-center justify-center min-h-[400px]">
                    {graphData?.state === "empty" || !graphData?.nodes || graphData.nodes.length === 0 ? (
                      <div className="text-center text-slate-400 p-12 flex flex-col items-center justify-center border border-dashed border-slate-200 rounded-2xl w-full">
                        <span className="text-5xl mb-4">🌐</span>
                        <p className="text-sm font-semibold leading-relaxed">충분한 양의 시청 기록이 분석된 후 관심사 간의 관계를 보여주는 지식 그래프가 활성화됩니다.</p>
                      </div>
                    ) : (
                      <InteractiveForceGraph graphData={graphData} setSelectedNode={setSelectedNode} variant="full" />
                    )}
                  </div>
                </div>
              )}

              {/* === GUIDE TAB === */}
              {activeTab === 'guide' && (
                <div className="grid grid-cols-1 xl:grid-cols-3 gap-4 xl:gap-6">
                  {/* Left Column: Mission Roadmap */}
                  <div className="xl:col-span-2 bg-white rounded-2xl shadow-sm p-6">
                    <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
                      <div>
                        <h3 className="text-xl font-black text-slate-900">디톡스 로드맵</h3>
                        <p className="text-sm text-slate-500 mt-1">AI가 추천하는 개인 맞춤형 알고리즘 탈출 플랜입니다.</p>
                      </div>
                      <div className="flex items-center gap-2 bg-slate-50 p-1 rounded-xl border border-slate-100">
                        <button 
                          onClick={() => setActiveCourse(3)}
                          className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${
                            activeCourse === 3 ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-200/50'
                          }`}
                        >
                          🔥 오늘의 미션
                        </button>
                        <button 
                          onClick={() => alert("7일 정규 집중 코스는 프리미엄(유료) 플랜에서 제공됩니다. 💎")}
                          className={`px-4 py-2 rounded-lg text-sm font-bold transition-all text-slate-400 hover:bg-slate-200/30 flex items-center gap-1`}
                        >
                          <span>🌱 7일 정규 코스</span>
                          <span className="text-xs">🔒</span>
                        </button>
                      </div>
                    </div>

                    <div className="relative pl-4 md:pl-8 border-l-2 border-indigo-100 space-y-8 pb-4">
                      {report?.missions?.map((m: any, idx: number) => {
                        const isCompleted = completedMissions.has(idx);
                        return (
                          <div key={idx} className="relative group">
                            {/* Roadmap Node */}
                            <div className={`absolute -left-[21px] md:-left-[37px] top-1 w-10 h-10 rounded-full flex items-center justify-center border-4 border-white transition-colors duration-300 ${
                              isCompleted ? 'bg-emerald-500' : 'bg-slate-200 group-hover:bg-indigo-200'
                            }`}>
                              {isCompleted ? <span className="text-white font-bold">✓</span> : <span className="text-slate-500 font-bold text-sm">{idx + 1}</span>}
                            </div>
                            
                            {/* Mission Card */}
                            <div 
                              className={`bg-white rounded-2xl border-2 transition-all duration-300 cursor-pointer overflow-hidden ${
                                isCompleted ? 'border-emerald-500 shadow-md' : 'border-slate-100 hover:border-indigo-300 shadow-sm hover:shadow-md'
                              }`}
                            >
                              {/* Header (Clickable) */}
                              <div 
                                onClick={() => handleMissionCheck(idx)}
                                className={`p-5 flex items-center justify-between ${isCompleted ? 'bg-emerald-50/50' : 'bg-white'}`}
                              >
                                <div>
                                  <div className="flex items-center gap-3 mb-2">
                                    <span className={`text-xs font-black px-2.5 py-1 rounded-md uppercase tracking-wider ${
                                      isCompleted ? 'bg-emerald-100 text-emerald-700' : 'bg-indigo-100 text-indigo-700'
                                    }`}>
                                      {m.mission_type}
                                    </span>
                                    {isCompleted && <span className="text-xs font-bold text-emerald-500 flex items-center gap-1">✨ 미션 완료!</span>}
                                  </div>
                                  <h4 className={`text-lg font-bold ${isCompleted ? 'text-emerald-900 line-through opacity-70' : 'text-slate-800'}`}>
                                    "{getSuggestedQuery(m)}" 검색해보기
                                  </h4>
                                </div>
                                
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      window.open(`https://www.youtube.com/results?search_query=${encodeURIComponent(getSuggestedQuery(m))}`, '_blank');
                                      handleMissionCheck(idx);
                                    }}
                                    className={`px-4 py-2.5 rounded-xl font-bold text-sm flex items-center gap-2 transition-transform hover:scale-105 active:scale-95 ${
                                      isCompleted 
                                        ? 'bg-emerald-500 text-white shadow-emerald-200 shadow-lg' 
                                        : 'bg-indigo-600 text-white shadow-indigo-200 shadow-lg'
                                    }`}
                                  >
                                    유튜브 검색 🚀
                                  </button>
                              </div>
                              
                              {/* Details Body */}
                              <div className="px-5 pb-5 pt-2 bg-slate-50 border-t border-slate-100">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3">
                                  <div>
                                    <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1">🎯 왜 해야 하나요?</span>
                                    <p className="text-sm text-slate-700 font-medium leading-relaxed">{m.description}</p>
                                  </div>
                                  <div>
                                    <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1">✅ 성공 기준</span>
                                    <p className="text-sm text-slate-700 font-medium leading-relaxed bg-white border border-slate-200 p-2 rounded-lg">
                                      {m.success_condition}
                                    </p>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Right Column: Gamification & Streak */}
                  <div className="flex flex-col gap-4 xl:gap-6">
                    <div className="flex flex-col shadow-lg rounded-2xl overflow-hidden">
                      <div className="bg-gradient-to-br from-indigo-900 via-indigo-800 to-slate-900 p-6 text-white relative">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full blur-2xl -mr-10 -mt-10"></div>
                        <h3 className="font-bold text-indigo-200 mb-2 opacity-80">나의 디톡스 칭호</h3>
                        
                        {(() => {
                          const streak = getStreakDays();
                          const currentTitleObj = [...ALL_TITLES].reverse().find(t => streak >= t.minStreak) || ALL_TITLES[0];
                          
                          return (
                            <div className="relative z-10">
                              <div className="text-2xl font-black mb-1">{currentTitleObj.title}</div>
                              <div className="text-sm text-indigo-100 opacity-90">{currentTitleObj.desc}</div>
                            </div>
                          );
                        })()}
                      </div>
                      
                      <button 
                        onClick={() => setIsTitlesExpanded(!isTitlesExpanded)}
                        className="bg-slate-100 hover:bg-slate-200 text-slate-600 font-bold text-xs py-2.5 px-4 flex justify-center items-center transition-colors border-t border-slate-200/50"
                      >
                        {isTitlesExpanded ? "접기 ▲" : "칭호 도감 보기 ▼"}
                      </button>
                      
                      <div 
                        className={`bg-slate-50 transition-all duration-300 ease-in-out overflow-hidden ${
                          isTitlesExpanded ? "max-h-80 border-t border-slate-200/50" : "max-h-0"
                        }`}
                      >
                        <div className="p-4 space-y-3 overflow-y-auto max-h-80 custom-scrollbar">
                          {(() => {
                            const streak = getStreakDays();
                            const currentTitleObj = [...ALL_TITLES].reverse().find(t => streak >= t.minStreak) || ALL_TITLES[0];
                            
                            return ALL_TITLES.map((t, idx) => {
                              const isUnlocked = streak >= t.minStreak;
                              const isCurrent = t.title === currentTitleObj.title;
                              
                              return (
                                <div 
                                  key={idx} 
                                  className={`p-3 rounded-xl border transition-all ${
                                    isCurrent ? 'bg-indigo-50 border-indigo-200 shadow-sm' : 
                                    isUnlocked ? 'bg-white border-slate-200 shadow-sm' : 'bg-slate-100/50 border-transparent opacity-50'
                                  }`}
                                >
                                  <div className="flex justify-between items-start mb-1">
                                    <div className={`font-bold flex items-center gap-1.5 ${isCurrent ? 'text-indigo-900' : isUnlocked ? 'text-slate-800' : 'text-slate-500'}`}>
                                      {!isUnlocked && <span>🔒</span>}
                                      {isUnlocked ? t.title : '???'}
                                    </div>
                                    {isCurrent && <span className="text-[10px] bg-indigo-600 text-white px-2 py-0.5 rounded-full font-black tracking-wide">장착중</span>}
                                  </div>
                                  <div className={`text-xs leading-relaxed ${isCurrent ? 'text-indigo-700' : isUnlocked ? 'text-slate-600' : 'text-slate-400'}`}>
                                    {isUnlocked ? t.desc : `${t.minStreak}일 연속 달성 시 해금됩니다.`}
                                  </div>
                                </div>
                              );
                            });
                          })()}
                        </div>
                      </div>
                    </div>

                    <div className="bg-white rounded-2xl shadow-sm p-6 flex-1 border border-slate-100">
                      <div className="flex items-end justify-between mb-6">
                        <div>
                          <h3 className="font-bold text-slate-900">주간 불꽃 트래커</h3>
                          <p className="text-xs text-slate-400 mt-1">오늘 3개의 미션을 완료하면 불꽃이 켜집니다!</p>
                        </div>
                        <div className="text-4xl font-black text-orange-500 tracking-tighter">
                          {getStreakDays()}<span className="text-lg text-slate-400 ml-1 font-bold">일 🔥</span>
                        </div>
                      </div>
                      
                      {/* 7 Days Duolingo-style Grid */}
                      <div className="flex justify-between items-center bg-slate-50 rounded-2xl p-4 border border-slate-100">
                        {(() => {
                          const curr = new Date();
                          const first = curr.getDate() - curr.getDay() + (curr.getDay() === 0 ? -6 : 1);
                          const weekDates: string[] = [];
                          for(let i = 0; i < 7; i++) {
                            const d = new Date(curr);
                            d.setDate(first + i);
                            const yyyy = d.getFullYear();
                            const mm = String(d.getMonth() + 1).padStart(2, '0');
                            const dd = String(d.getDate()).padStart(2, '0');
                            weekDates.push(`${yyyy}-${mm}-${dd}`);
                          }
                          
                          return ['월', '화', '수', '목', '금', '토', '일'].map((day, i) => {
                            const dateStr = weekDates[i];
                            const todayIndex = new Date().getDay() === 0 ? 6 : new Date().getDay() - 1; 
                            const isToday = i === todayIndex;
                            const isTodayComplete = completedMissions.size === (report?.missions?.length || 3);
                            
                            let hasFlame = false;
                            // Check if this date is in the backend's completed history
                            if (guideData?.streak_history?.includes(dateStr)) {
                              hasFlame = true;
                            }
                            // Optimistic UI update for today
                            if (isToday && isTodayComplete) {
                              hasFlame = true;
                            }
                            
                            return (
                              <div key={i} className="flex flex-col items-center gap-2">
                                <div className={`w-10 h-10 rounded-full flex items-center justify-center transition-all duration-500 relative ${
                                  hasFlame ? 'bg-orange-100' : 'bg-slate-200/50'
                                } ${isToday && !hasFlame ? 'ring-2 ring-indigo-400 ring-offset-2' : ''}`}>
                                  {hasFlame ? (
                                    <span className="text-2xl drop-shadow-sm animate-bounce" style={{animationDuration: '2s'}}>🔥</span>
                                  ) : (
                                    <span className="w-3 h-3 rounded-full bg-slate-300"></span>
                                  )}
                                  {hasFlame && isToday && (
                                    <span className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-500 border-2 border-white rounded-full"></span>
                                  )}
                                </div>
                                <span className={`text-[11px] font-bold ${isToday ? 'text-indigo-600' : 'text-slate-400'}`}>{day}</span>
                              </div>
                            );
                          });
                        })()}
                      </div>
                      <div className="mt-6 bg-indigo-50/50 border border-indigo-100 p-4 rounded-xl text-sm text-indigo-800 flex items-start gap-3">
                        <span className="text-xl leading-none mt-0.5">💡</span>
                        <div className="flex-1">
                          <p className="font-bold mb-1">꾸준함의 마법</p>
                          <p className="text-indigo-600/80 text-xs leading-relaxed">21일 연속으로 디톡스를 진행하면 뇌의 신경 회로가 재편성되어 알고리즘에 끌려다니지 않는 탄탄한 주도적 습관이 형성됩니다!</p>
                        </div>
                      </div>
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

              {/* === SETTINGS TAB === */}
              {activeTab === 'settings' && (
                <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 max-w-2xl mx-auto mt-6 text-left">
                  <h3 className="text-xl font-bold text-slate-900 mb-2">설정 및 데이터 관리</h3>
                  <p className="text-slate-500 text-sm mb-6">사용자의 계정 상태 및 저장된 원천 데이터를 관리할 수 있습니다.</p>
                  
                  <div className="space-y-6">
                    <div className="border-t border-slate-100 pt-6">
                      <h4 className="text-sm font-semibold text-slate-800 mb-1">📂 새 시청 기록 업로드 (재분석)</h4>
                      <p className="text-slate-500 text-xs mb-3">
                        새로운 유튜브 시청 기록(Takeout 파일)을 업로드하여 디톡스 분석 결과를 업데이트합니다. 
                        기존의 분석 이력과 함께 새로운 회차로 누적되어 비교할 수 있습니다.
                      </p>
                      <button
                        onClick={() => {
                          setIsReupload(true);
                          setStep("upload");
                        }}
                        className="px-4 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-600 border border-indigo-200 rounded-lg text-xs font-bold transition-colors"
                      >
                        새 파일 업로드하기
                      </button>
                    </div>

                    <div className="border-t border-slate-100 pt-6">
                      <h4 className="text-sm font-semibold text-orange-600 mb-1">⚠️ 데이터만 초기화 (로그인 계정 유지)</h4>
                      <p className="text-slate-500 text-xs mb-3">
                        로그인 계정은 유지한 채, 서버에 저장된 시청 데이터와 모든 디톡스 분석 이력 및 개인정보 동의 기록만을 완전히 초기화합니다.
                      </p>
                      <button
                        onClick={handleResetDataOnly}
                        className="px-4 py-2 bg-orange-50 hover:bg-orange-100 text-orange-600 border border-orange-200 rounded-lg text-xs font-bold transition-colors"
                      >
                        데이터만 초기화하기
                      </button>
                    </div>

                    <div className="border-t border-slate-100 pt-6">
                      <h4 className="text-sm font-semibold text-slate-800 mb-1">로그인 계정</h4>
                      <p className="text-slate-500 text-xs mb-3">{session?.user?.email}</p>
                      <button
                        onClick={() => supabase.auth.signOut()}
                        className="px-4 py-2 bg-slate-100 hover:bg-slate-200 border border-slate-200 rounded-lg text-slate-700 text-xs font-bold transition-colors"
                      >
                        로그아웃
                      </button>
                    </div>
                    
                    <div className="border-t border-slate-100 pt-6">
                      <h4 className="text-sm font-semibold text-red-600 mb-1">데이터 영구 삭제 및 회원 탈퇴</h4>
                      <p className="text-slate-500 text-xs mb-4 leading-relaxed">
                        서버에 저장된 유튜브 시청 기록, 형태소 분류 결과, 산출된 6축 편향성 점수, AI 코멘트 리포트 및 개인정보 동의 기록 등 모든 데이터를 일괄 파기하고 계정을 안전하게 삭제합니다. 이 작업은 취소할 수 없습니다.
                      </p>
                      <button
                        onClick={handleDeleteAllData}
                        className="px-4 py-2 bg-red-50 hover:bg-red-100 text-red-600 border border-red-200 rounded-lg text-xs font-bold transition-colors"
                      >
                        데이터 일괄 삭제 및 회원 탈퇴
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
      
      <DeveloperInspector 
        state={{
          step,
          datasetId,
          scores,
          report,
          personaData,
          graphData,
          realtimeData,
          guideData,
          contents
        }}
      />
    </div>
  );
}
