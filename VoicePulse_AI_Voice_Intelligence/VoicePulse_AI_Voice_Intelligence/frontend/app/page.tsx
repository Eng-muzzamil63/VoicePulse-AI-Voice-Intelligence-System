import type { ReactNode } from 'react';
'use client';

import { useEffect, useMemo, useState } from 'react';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

type Call = {
  id: string; customer_name: string; agent_name: string; duration_sec: number;
  sentiment: string; sentiment_score: number; intent: string; intent_score?: number;
  urgency: string; urgency_score?: number; resolution: string; csat?: number;
  summary: string; topics: string[]; action_items: {owner:string; action:string; due:string}[];
  transcript: string; created_at: string; sentiment_method?: string; intent_method?: string;
};

type Overview = {calls_today:number; negative_sentiment_pct:number; high_urgency_calls:number; resolution_rate:number; avg_csat:number; deep_learning: Record<string,string>};

function Icon({name}:{name:string}){
  const paths: Record<string, ReactNode> = {
    wave:<><path d="M3 12h2l2-6 4 12 3-8 2 4h5"/></>,
    phone:<><path d="M22 16.9v3a2 2 0 0 1-2.2 2A19.8 19.8 0 0 1 11.2 18a19.5 19.5 0 0 1-6-9.8A2 2 0 0 1 7.2 6h3a2 2 0 0 1 2 1.7c.1.8.3 1.5.6 2.2a2 2 0 0 1-.5 2.1L11 13.3a16 16 0 0 0 5.7 5.7l1.3-1.3a2 2 0 0 1 2.1-.5c.7.3 1.4.5 2.2.6A2 2 0 0 1 22 16.9Z"/></>,
    pulse:<><path d="M3 12h4l2-6 4 12 2-5h6"/></>,
    sparkle:<><path d="m12 3 1.7 5.3L19 10l-5.3 1.7L12 17l-1.7-5.3L5 10l5.3-1.7L12 3Z"/><path d="m19 15 .7 2.3L22 18l-2.3.7L19 21l-.7-2.3L16 18l2.3-.7L19 15Z"/></>,
    upload:<><path d="M12 16V4"/><path d="m7 9 5-5 5 5"/><path d="M5 20h14"/></>,
    search:<><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></>,
    x:<><path d="M6 6l12 12M18 6 6 18"/></>,
    arrow:<><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></>,
  };
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden>{paths[name] || paths.wave}</svg>
}

export default function Home(){
  const [overview,setOverview]=useState<Overview|null>(null);
  const [calls,setCalls]=useState<Call[]>([]);
  const [selected,setSelected]=useState<Call|null>(null);
  const [search,setSearch]=useState('');
  const [sentiment,setSentiment]=useState('all');
  const [urgency,setUrgency]=useState('all');
  const [transcript,setTranscript]=useState('');
  const [analysis,setAnalysis]=useState<Call|null>(null);
  const [busy,setBusy]=useState(false);
  const [uploadMessage,setUploadMessage]=useState('');
  const [error,setError]=useState('');

  async function load(){
    try{
      const [o,c]=await Promise.all([
        fetch(`${API}/api/overview`).then(r=>r.json()),
        fetch(`${API}/api/calls?search=${encodeURIComponent(search)}&sentiment=${sentiment}&urgency=${urgency}`).then(r=>r.json())
      ]);
      setOverview(o); setCalls(c); setError('');
    }catch(e){setError('Backend unavailable. Start FastAPI on port 8000.');}
  }
  useEffect(()=>{load()},[search,sentiment,urgency]);

  const negativeCount = useMemo(()=>calls.filter(c=>c.sentiment==='Negative').length,[calls]);
  const high = useMemo(()=>calls.filter(c=>c.urgency==='High'||c.urgency==='Critical').length,[calls]);

  async function analyze(){
    if(transcript.trim().length<10) return;
    setBusy(true); setError('');
    try{
      const r=await fetch(`${API}/api/analyze`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({customer_name:'Live customer',agent_name:'Analyst',transcript})});
      const data=await r.json(); if(!r.ok) throw new Error(data.detail||'Analysis failed');
      setAnalysis(data); setTranscript('');
    }catch(e:any){setError(e.message)} finally{setBusy(false)}
  }

  async function upload(file:File){
    setBusy(true); setUploadMessage('Transcribing with Whisper...'); setError('');
    const fd=new FormData(); fd.append('file',file);
    try{
      const r=await fetch(`${API}/api/transcribe`,{method:'POST',body:fd});
      const data=await r.json(); if(!r.ok) throw new Error(data.detail||'Transcription failed');
      setAnalysis({id:`UPLOAD-${Date.now()}`,customer_name:'Uploaded call',agent_name:'Whisper',duration_sec:0,csat:undefined,...data});
      setUploadMessage('Transcription complete');
    }catch(e:any){setError(e.message);setUploadMessage('')}
    finally{setBusy(false)}
  }

  return <main className="shell">
    <header className="nav">
      <div className="brand"><div className="brandMark"><Icon name="wave"/></div><div><div className="eyebrow">VOICE OPERATIONS INTELLIGENCE</div><h1>VoicePulse <span>AI</span></h1></div></div>
      <div className="navRight"><div className="live"><i/> Models ready</div><button className="ghost" onClick={load}>Refresh</button></div>
    </header>

    {error && <div className="errorBar">{error}</div>}

    <section className="hero">
      <div className="heroCopy">
        <div className="eyebrow">CUSTOMER CONVERSATION INTELLIGENCE</div>
        <h2>Turn every conversation into an operational signal.</h2>
        <p>VoicePulse turns calls into searchable intelligence: speech-to-text, deep-learning sentiment, semantic intent, urgency, topics, action items and resolution signals.</p>
        <div className="chips"><span><Icon name="pulse"/> Whisper transcription</span><span><Icon name="sparkle"/> Transformer NLP</span><span><Icon name="arrow"/> Actionable output</span></div>
      </div>
      <div className="heroPanel">
        <div className="heroPanelHead"><div><div className="tiny">MODEL STACK</div><strong>Voice → Decision</strong></div><div className="accuracy">LIVE</div></div>
        <div className="pipeline"><div className="stage"><b>01</b><span>Whisper</span><small>speech to text</small></div><div className="connector"/><div className="stage"><b>02</b><span>DistilBERT</span><small>sentiment</small></div><div className="connector"/><div className="stage"><b>03</b><span>Embeddings</span><small>intent + topics</small></div></div>
      </div>
    </section>

    <section className="metrics">
      {[['Calls today',overview?.calls_today ?? '--','+ live'],['Negative sentiment',overview?`${overview.negative_sentiment_pct}%`:'--',negativeCount+' flagged'],['High urgency',overview?.high_urgency_calls ?? '--',high+' priority'],['Resolution rate',overview?`${overview.resolution_rate}%`:'--','case outcome'],['Avg. CSAT',overview?.avg_csat ?? '--','/ 5.0']].map(([l,v,s],i)=><div className="metric" key={i}><div className="metricLabel">{l}</div><div className="metricValue">{v}</div><div className="metricSub">{s}</div></div>)}
    </section>

    <section className="gridTop">
      <div className="panel trendPanel">
        <div className="panelHead"><div><div className="tiny">VOICE SIGNALS</div><h3>Conversation health</h3><p>Sentiment pressure and urgency across the current call set.</p></div><div className="legend"><span><i className="pink"/>Sentiment</span><span><i className="blue"/>Urgency</span></div></div>
        <div className="chart"><div className="ylabels"><span>100</span><span>75</span><span>50</span><span>25</span><span>0</span></div><svg viewBox="0 0 760 230" preserveAspectRatio="none"><defs><linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#7c3aed" stopOpacity=".18"/><stop offset="1" stopColor="#7c3aed" stopOpacity="0"/></linearGradient></defs><path d="M0 176 C70 165 82 125 145 141 S220 183 285 151 S348 84 404 112 S470 148 522 120 S598 62 655 91 S718 72 760 48 V230 H0Z" fill="url(#area)"/><path d="M0 176 C70 165 82 125 145 141 S220 183 285 151 S348 84 404 112 S470 148 522 120 S598 62 655 91 S718 72 760 48" fill="none" stroke="#7c3aed" strokeWidth="3"/><path d="M0 184 C74 175 110 168 158 171 S241 165 291 157 S354 146 403 151 S487 142 532 147 S615 137 662 132 S716 121 760 112" fill="none" stroke="#0ea5e9" strokeWidth="2" strokeDasharray="6 6"/></svg></div>
      </div>
      <div className="panel insightPanel">
        <div className="panelHead"><div><div className="tiny">AI CASE BRIEF</div><h3>What teams should know</h3><p>Highest-priority signals from live conversation analysis.</p></div><div className="priority">PRIORITY</div></div>
        <div className="brief"><div className="briefIcon"><Icon name="sparkle"/></div><div><strong>{high || 0} calls need attention</strong><p>High-urgency conversations should be reviewed before the next support shift.</p></div></div>
        <div className="brief"><div className="briefIcon"><Icon name="phone"/></div><div><strong>Negative sentiment is a routing signal</strong><p>Use sentiment alongside intent and urgency to prioritize escalation, not as a standalone verdict.</p></div></div>
        <div className="brief"><div className="briefIcon"><Icon name="arrow"/></div><div><strong>Action items are ready to review</strong><p>VoicePulse turns conversation language into owners, actions and suggested response windows.</p></div></div>
      </div>
    </section>

    <section className="workbench">
      <div className="panel callsPanel">
        <div className="panelHead"><div><div className="tiny">CALL QUEUE</div><h3>Conversation inbox</h3><p>Search, filter and open any analyzed call.</p></div><div className="count">{calls.length} calls</div></div>
        <div className="filters"><div className="search"><Icon name="search"/><input placeholder="Search customer, intent or transcript" value={search} onChange={e=>setSearch(e.target.value)}/></div><select value={sentiment} onChange={e=>setSentiment(e.target.value)}><option value="all">All sentiment</option><option>Positive</option><option>Neutral</option><option>Negative</option></select><select value={urgency} onChange={e=>setUrgency(e.target.value)}><option value="all">All urgency</option><option>Critical</option><option>High</option><option>Medium</option><option>Low</option></select></div>
        <div className="tableHead"><span>Customer</span><span>Intent</span><span>Sentiment</span><span>Urgency</span><span>CSAT</span></div>
        <div className="table">{calls.map(c=><button className="callRow" key={c.id} onClick={()=>setSelected(c)}><span className="customer"><b>{c.customer_name}</b><small>{c.agent_name} · {Math.round(c.duration_sec/60)} min</small></span><span>{c.intent}</span><span><em className={`tag ${c.sentiment.toLowerCase()}`}>{c.sentiment}</em></span><span><em className={`tag ${c.urgency.toLowerCase()}`}>{c.urgency}</em></span><span>{c.csat ? c.csat.toFixed(1) : '—'}</span></button>)}</div>
      </div>
      <aside className="sideStack">
        <div className="panel analyzePanel"><div className="panelHead"><div><div className="tiny">LIVE ANALYZER</div><h3>Analyze a transcript</h3><p>Paste a call excerpt to run the intelligence pipeline.</p></div></div><textarea value={transcript} onChange={e=>setTranscript(e.target.value)} placeholder="Paste a conversation here... e.g. I was charged twice and need a refund today."></textarea><button className="primary" onClick={analyze} disabled={busy}>{busy?'Analyzing…':'Analyze conversation'} <Icon name="arrow"/></button><div className="upload"><label><Icon name="upload"/> Upload audio<input type="file" accept="audio/*,.m4a,.mp3,.wav,.webm" onChange={e=>e.target.files?.[0] && upload(e.target.files[0])}/></label>{uploadMessage && <span>{uploadMessage}</span>}</div></div>
        <div className="panel modelPanel"><div className="tiny">DEEP-LEARNING LAYER</div><h3>Open-source by design.</h3><p>Optional local models keep the inference path inspectable and portable.</p><div className="modelList"><div><b>Whisper</b><span>Speech recognition</span></div><div><b>DistilBERT</b><span>Sentiment</span></div><div><b>MiniLM</b><span>Semantic intent</span></div></div></div>
      </aside>
    </section>

    <footer>VoicePulse AI · synthetic demo data · built for customer-operations intelligence</footer>

    {(selected || analysis) && <div className="overlay" onClick={()=>{setSelected(null);setAnalysis(null)}}><div className="drawer" onClick={e=>e.stopPropagation()}><button className="close" onClick={()=>{setSelected(null);setAnalysis(null)}}><Icon name="x"/></button>{(()=>{const c=(analysis||selected)!;return <><div className="eyebrow">CONVERSATION REPORT</div><h2>{c.customer_name}</h2><div className="drawerMeta">{c.agent_name} · {c.id}</div><div className="scoreGrid"><div><small>SENTIMENT</small><strong className={c.sentiment==='Negative'?'neg':''}>{c.sentiment}</strong><span>{Math.round((c.sentiment_score||0)*100)}% confidence</span></div><div><small>INTENT</small><strong>{c.intent}</strong><span>{Math.round((c.intent_score||0)*100)}% match</span></div><div><small>URGENCY</small><strong>{c.urgency}</strong><span>{Math.round((c.urgency_score||0)*100)} signal</span></div><div><small>OUTCOME</small><strong>{c.resolution}</strong><span>CSAT {c.csat??'—'}</span></div></div><section className="drawerSection"><div className="tiny">AI SUMMARY</div><p>{c.summary}</p></section><section className="drawerSection"><div className="tiny">TOPICS</div><div className="topicList">{c.topics.map(t=><span key={t}>{t}</span>)}</div></section><section className="drawerSection"><div className="tiny">ACTION ITEMS</div>{c.action_items?.length ? c.action_items.map((a,i)=><div className="action" key={i}><div className="num">0{i+1}</div><div><b>{a.action}</b><small>{a.owner} · due {a.due}</small></div></div>) : <p className="muted">No action items detected.</p>}</section><section className="drawerSection"><div className="tiny">TRANSCRIPT</div><div className="transcript">{c.transcript}</div></section></>})()}</div></div>}
  </main>
}
