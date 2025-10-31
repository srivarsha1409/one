import { useState } from 'react';

const backend = "http://127.0.0.1:8000";

export default function Admin() {
  const [history, setHistory] = useState([]);
  const [currentId, setCurrentId] = useState(null);
  const [data, setData] = useState(null);
  const [messages, setMessages] = useState([]);
  const [eduTab, setEduTab] = useState('higher');

  function addMsg(type, text, icon) {
    setMessages((m)=>[{type,text,icon,id:Date.now()},...m]);
  }
  function clearMsgs(){ setMessages([]); }

  async function handleUpload(file) {
    if (!file) return;
    clearMsgs();
    addMsg('processing','Processing resume...','⏳');
    const form = new FormData();
    form.append('file', file);
    try {
      const res = await fetch(backend + "/upload_resume", { method:'POST', body: form });
      const json = await res.json();
      clearMsgs();
      if (!res.ok) {
        addMsg('error', `Resume processing failed: ${json.detail || 'Unknown error'}`, '❌');
        setHistory(h=>[{id:Date.now(), filename:file.name, status:'failed', created_at:new Date().toISOString(), error: json.detail || 'Processing failed'}, ...h]);
        return;
      }
      addMsg('success','Resume processed successfully!','✅');
      const targetRole = json.data?.role_match || 'Not detected';
      addMsg('info', `Detected target role: ${targetRole}`, '🎯');
      const id = json.id || Date.now();
      setCurrentId(id);
      setData(json.data);
      setHistory(h=>[
        { id, filename:file.name, status:'success', name: json.data.name, role: targetRole, ats_score: json.data.ats_score, summary: json.data.summary, created_at:new Date().toISOString(), data: json.data },
        ...h
      ]);
    } catch (err) {
      clearMsgs();
      addMsg('error', `Upload failed: ${err.message}`, '❌');
      setHistory(h=>[{id:Date.now(), filename:file.name, status:'failed', created_at:new Date().toISOString(), error: err.message}, ...h]);
    }
  }

  function renderPill(text) {
    return <div key={text} style={{background:'#dbeafe',color:'#1e40af',padding:'6px 14px',borderRadius:20,fontSize:13,fontWeight:500}}>{text}</div>;
  }

  function downloadReport() {
    if (!data) return;
    const reportContent = `
Resume Analysis Report
===========================
Name: ${data.name || "N/A"}
Email: ${data.email || "N/A"}
Phone: ${data.phone || "N/A"}
LinkedIn: ${data.linkedin || "N/A"}
GitHub: ${data.github || "N/A"}
LeetCode: ${data.leetcode || "N/A"}
CodeChef: ${data.codechef || "N/A"}
HackerRank: ${data.hackerrank || "N/A"}

--- Education ---
Degree: ${data.education?.degree || "N/A"}
University: ${data.education?.university || "N/A"}
Year: ${data.education?.year || "N/A"}
GPA: ${data.education?.gpa || "N/A"}

--- Skills ---
Technical: ${(data.skills?.technical || []).join(", ") || "N/A"}
Soft: ${(data.skills?.soft || []).join(", ") || "N/A"}

--- Summary ---
Word Count: ${data.word_count || "N/A"}
Role Match: ${data.role_match || "N/A"}
ATS Score: ${data.ats_score ? data.ats_score + "%" : "N/A"}
Summary: ${data.summary || "N/A"}
`;
    const blob = new Blob([reportContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${data.name || 'resume_analysis'}_report.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div style={{display:'flex',minHeight:'100vh',background:'linear-gradient(135deg, #e3f2fd 0%, #e8f5e9 50%, #fce4ec 100%)',color:'#111'}}>
      <div style={{width:280,background:'#fff',boxShadow:'2px 0 12px rgba(0,0,0,0.08)',display:'flex',flexDirection:'column'}}>
        <div style={{padding:20,background:'linear-gradient(135deg, #1e3a8a, #3b82f6)',color:'#fff'}}>
          <h2 style={{margin:0,marginBottom:8,fontSize:18,fontWeight:700}}>📊 Resume Insight</h2>
          <div style={{fontSize:13,opacity:0.9,display:'flex',alignItems:'center',gap:8}}>👤 <span>Admin User</span></div>
          <button onClick={()=>{ setCurrentId(null); setData(null); alert('Logged out successfully!'); }} style={{marginTop:12,padding:'8px 16px',background:'rgba(255,255,255,0.2)',border:'1px solid rgba(255,255,255,0.3)',color:'#fff',borderRadius:6,cursor:'pointer',fontSize:13,fontWeight:600,width:'100%'}}>🚪 Logout</button>
        </div>
        <div style={{flex:1,overflowY:'auto',padding:16}}>
          <h3 style={{margin:'0 0 16px 0',fontSize:14,color:'#6b7280',textTransform:'uppercase',letterSpacing:0.5}}>📊 Analysis History</h3>
          <div>
            {history.length===0 && (<div style={{textAlign:'center',color:'#9ca3af',padding:'40px 20px',fontSize:13}}>No analyses yet. Upload a resume to get started!</div>)}
            {history.map(item => (
              <div key={item.id} onClick={()=>{ if(item.data && item.status==='success'){ setCurrentId(item.id); setData(item.data); } }} style={{background: item.id===currentId? '#dbeafe':'#f9fafb', border:'1px solid '+(item.id===currentId?'#3b82f6':'#e5e7eb'), borderRadius:8, padding:12, marginBottom:12, cursor:'pointer'}}>
                <div style={{display:'flex',justifyContent:'space-between',alignItems:'start',marginBottom:8}}>
                  <div style={{fontWeight:600,fontSize:13,color:'#1f2937',flex:1}}>{item.filename || item.name || ('Resume #'+item.id)}</div>
                  <div style={{fontSize:11,padding:'2px 8px',borderRadius:12,fontWeight:600, background: item.status==='success'?'#d1fae5':'#fee2e2', color: item.status==='success'?'#065f46':'#991b1b'}}>{item.status==='success'?'✓ Success':'✗ Failed'}</div>
                </div>
                {item.role && <div style={{fontSize:11,color:'#6366f1',marginBottom:6,fontWeight:500}}>🎯 {item.role}</div>}
                <div style={{fontSize:11,color:'#9ca3af',display:'flex',gap:8}}>
                  {item.ats_score && <span>ATS: {item.ats_score}%</span>}
                  <span>{new Date(item.created_at).toLocaleString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div style={{flex:1,overflowY:'auto'}}>
        <div style={{maxWidth:1400, margin:'24px auto', padding:20}}>
          <header style={{display:'flex',justifyContent:'space-between',alignItems:'center',gap:16,marginBottom:20}}>
            <div>
              <div style={{fontSize:28,fontWeight:700}}>Resume Analysis Dashboard</div>
              <div style={{color:'#4b5563'}}>Upload a candidate resume (PDF) to extract details and compute ATS score</div>
            </div>
            <div>
              <button onClick={downloadReport} disabled={!data} style={{padding:'10px 14px',borderRadius:8,border:'none',cursor: data? 'pointer':'not-allowed',fontWeight:700, background:'#00aaff', color:'#fff', opacity: data?1:0.5}}>📥 Download Report</button>
            </div>
          </header>

          <div style={{marginTop:18, background:'linear-gradient(90deg,#1e90ff,#3a7bd5)', color:'#fff', padding:18, borderRadius:14, boxShadow:'0 6px 18px rgba(0,0,0,0.08)'}}>
            <div style={{fontWeight:700,fontSize:18}}>📤 Upload Your Resume</div>
            <div style={{marginTop:12, display:'flex', gap:10, alignItems:'center', flexWrap:'wrap'}}>
              <input type="file" accept="application/pdf" onChange={(e)=>handleUpload(e.target.files[0])} style={{padding:8, background:'rgba(255,255,255,0.9)', borderRadius:6, border:'none'}} />
              <button onClick={()=>{}} disabled style={{padding:'10px 14px',borderRadius:8,border:'none',fontWeight:700,background:'#00aaff',color:'#fff',opacity:0.5}}>Analyze Resume</button>
            </div>
            <div style={{marginTop:16, display:'flex', flexDirection:'column', gap:8}}>
              {messages.map(m => (
                <div key={m.id} style={{padding:'10px 14px',borderRadius:8,fontSize:13,fontWeight:600,display:'flex',alignItems:'center',gap:8,border:'1px solid rgba(255,255,255,0.3)', background: m.type==='processing'?'rgba(254, 243, 199, 0.3)': m.type==='success'?'rgba(209, 250, 229, 0.3)': m.type==='error'?'rgba(254, 226, 226, 0.3)':'rgba(219, 234, 254, 0.3)'}}>
                  <span>{m.icon}</span><span>{m.text}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Personal Information */}
          <div style={{fontSize:24,fontWeight:700,margin:'30px 0 20px 0',color:'#1a237e',display:'flex',alignItems:'center',gap:10}}>Personal Information</div>
          <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit, minmax(280px, 1fr))',gap:16,marginBottom:24}}>
            {[
              ['👤','Name','name'],['📧','Email','email'],['📱','Phone','phone'],['🔗','LinkedIn','linkedin'],['🐙','GitHub','github'],['💻','LeetCode','leetcode'],['🔗','Codechef','codechef'],['🔗','Hacker rank','hackerrank']
            ].map(([icon,label,key]) => (
              <div key={label} style={{background:'#fff',padding:20,borderRadius:12,boxShadow:'0 4px 12px rgba(0,0,0,0.06)'}}>
                <div style={{display:'flex',alignItems:'center',gap:8,fontSize:16,fontWeight:600,color:'#1f2937',marginBottom:12}}><span style={{fontSize:20}}>{icon}</span><span>{label}</span></div>
                <div style={{fontSize:15,color:'#4b5563',wordBreak:'break-word'}}>{data?.[key] || '—'}</div>
              </div>
            ))}
            <div style={{background:'#fff',padding:20,borderRadius:12,boxShadow:'0 4px 12px rgba(0,0,0,0.06)'}}>
              <div style={{display:'flex',alignItems:'center',gap:8,fontSize:16,fontWeight:600,color:'#1f2937',marginBottom:12}}><span style={{fontSize:20}}>🗣</span><span>Languages</span></div>
              <div>
                {(() => {
                  const langs = data?.languages;
                  let items = [];
                  if (!langs) return <div style={{color:'#6b7280',fontSize:14}}>No languages found</div>;
                  let arr = langs;
                  if (typeof langs === 'string') arr = langs.split(/[,;]/).map(s=>s.trim()).filter(Boolean);
                  if (Array.isArray(arr) && arr.length>0) {
                    items = arr.map(l => typeof l === 'string' ? l : `${l.language || '—'}${l.proficiency?` (${l.proficiency})`:''}`);
                    return <div style={{display:'flex',flexWrap:'wrap',gap:8}}>{items.map(renderPill)}</div>;
                  }
                  return <div style={{color:'#6b7280',fontSize:14}}>No languages found</div>;
                })()}
              </div>
            </div>
          </div>

          {/* Education (Tabbed) */}
          <div style={{fontSize:24,fontWeight:700,margin:'30px 0 12px 0',color:'#1a237e',display:'flex',alignItems:'center',gap:10}}>Education</div>
          <div style={{display:'flex',gap:8,marginBottom:12}}>
            {[
              ['higher','Higher Education'],
              ['school','School & Percentages']
            ].map(([key,label]) => (
              <button key={key} onClick={()=>setEduTab(key)} style={{padding:'8px 12px',borderRadius:8,border:'1px solid #e5e7eb',cursor:'pointer',fontWeight:600, background: eduTab===key? '#1e3a8a':'#fff', color: eduTab===key? '#fff':'#1f2937'}}>{label}</button>
            ))}
          </div>
          {eduTab==='higher' ? (
            <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit, minmax(280px, 1fr))',gap:16,marginBottom:24}}>
              {[
                ['🎓','Degree', data?.education?.degree], ['🏫','University', data?.education?.university], ['📅','Graduation Year', data?.education?.year], ['📊','GPA/CGPA', data?.education?.gpa]
              ].map(([icon,label,value]) => (
                <div key={label} style={{background:'#fff',padding:20,borderRadius:12,boxShadow:'0 4px 12px rgba(0,0,0,0.06)'}}>
                  <div style={{display:'flex',alignItems:'center',gap:8,fontSize:16,fontWeight:600,color:'#1f2937',marginBottom:12}}><span style={{fontSize:20}}>{icon}</span><span>{label}</span></div>
                  <div style={{fontSize:15,color:'#4b5563'}}>{value || '—'}</div>
                </div>
              ))}
            </div>
          ) : (
            <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit, minmax(280px, 1fr))',gap:16,marginBottom:24}}>
              {[
                ['🏫','School Name', data?.education?.school_name],
                ['📈','SSLC %', data?.education?.sslc_percentage],
                ['📈','HSC %', data?.education?.hsc_percentage]
              ].map(([icon,label,value]) => (
                <div key={label} style={{background:'#fff',padding:20,borderRadius:12,boxShadow:'0 4px 12px rgba(0,0,0,0.06)'}}>
                  <div style={{display:'flex',alignItems:'center',gap:8,fontSize:16,fontWeight:600,color:'#1f2937',marginBottom:12}}><span style={{fontSize:20}}>{icon}</span><span>{label}</span></div>
                  <div style={{fontSize:15,color:'#4b5563'}}>{value || '—'}</div>
                </div>
              ))}
            </div>
          )}

          {/* Certificates */}
          <div style={{fontSize:24,fontWeight:700,margin:'30px 0 20px 0',color:'#1a237e',display:'flex',alignItems:'center',gap:10}}>Certificates</div>
          <div style={{background:'#fff',padding:20,borderRadius:12,boxShadow:'0 4px 12px rgba(0,0,0,0.06)'}}>
            <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill, minmax(250px, 1fr))',gap:12}}>
              {(data?.certificates && data.certificates.length>0) ? data.certificates.map((c,idx)=>(
                <div key={idx} style={{background:'#f0f9ff',padding:12,borderRadius:8,borderLeft:'4px solid #3b82f6'}}>
                  <div style={{fontWeight:600,fontSize:14,color:'#1e3a8a'}}>{c.name || '—'}</div>
                  <div style={{fontSize:12,color:'#64748b',marginTop:4}}>{c.issuer || '—'}</div>
                </div>
              )) : <div style={{color:'#6b7280'}}>No certificates found</div>}
            </div>
          </div>

          {/* Skills & ATS */}
          <div style={{fontSize:24,fontWeight:700,margin:'30px 0 20px 0',color:'#1a237e',display:'flex',alignItems:'center',gap:10}}>Analysis Summary</div>
          <div style={{display:'grid',gridTemplateColumns:'2fr 1fr',gap:16}}>
            <div style={{background:'#fff',padding:20,borderRadius:12,boxShadow:'0 4px 12px rgba(0,0,0,0.06)'}}>
              <h3 style={{margin:'0 0 16px 0', color:'#1f2937'}}>🛠 Skills Analysis</h3>
              <div style={{display:'flex',gap:24,flexWrap:'wrap'}}>
                <div style={{flex:1,minWidth:250}}>
                  <h4 style={{fontSize:16,color:'#1f2937',marginBottom:12}}>Technical Skills</h4>
                  <div style={{display:'flex',flexWrap:'wrap',gap:8}}>
                    {(data?.skills?.technical && data.skills.technical.length>0) ? data.skills.technical.map(renderPill) : <span style={{color:'#6b7280'}}>—</span>}
                  </div>
                </div>
                <div style={{flex:1,minWidth:250}}>
                  <h4 style={{fontSize:16,color:'#1f2937',marginBottom:12}}>Soft Skills</h4>
                  <div style={{display:'flex',flexWrap:'wrap',gap:8}}>
                    {(data?.skills?.soft && data.skills.soft.length>0) ? data.skills.soft.map(renderPill) : <span style={{color:'#6b7280'}}>—</span>}
                  </div>
                </div>
              </div>
            </div>
            <div style={{background:'#fff',padding:20,borderRadius:12,boxShadow:'0 4px 12px rgba(0,0,0,0.06)'}}>
              <h3 style={{margin:'0 0 16px 0', color:'#1f2937'}}>🧾 ATS Score</h3>
              <div style={{textAlign:'center',padding:20}}>
                <div style={{fontSize:48,fontWeight:700,color:'#1e3a8a'}}>
                  <span>{data?.ats_score || '—'}</span>
                  <span style={{fontSize:24}}>{data?.ats_score? '%':''}</span>
                </div>
                <div style={{marginTop:10,color:'#6b7280',fontSize:14}}>Format, Keywords & Sections</div>
              </div>
            </div>
          </div>

          {/* Summary */}
          <div style={{background:'#fff',padding:20,borderRadius:12,boxShadow:'0 4px 12px rgba(0,0,0,0.06)', marginTop:16}}>
            <h3 style={{margin:'0 0 16px 0', color:'#1f2937'}}>📄 Resume Summary</h3>
            <div style={{display:'flex',marginBottom:10}}>
              <div style={{fontWeight:600,color:'#374151',minWidth:120}}>Word count:</div>
              <div style={{color:'#6b7280',flex:1}}>{data?.word_count || '—'}</div>
            </div>
            <div style={{display:'flex',marginBottom:10}}>
              <div style={{fontWeight:600,color:'#374151',minWidth:120}}>Role match:</div>
              <div style={{color:'#6b7280',flex:1}}>{data?.role_match || '—'}</div>
            </div>
            <div style={{marginTop:16}}>
              <div style={{marginBottom:8,fontWeight:600,color:'#374151'}}>Summary:</div>
              <div style={{color:'#4b5563',lineHeight:1.6,fontSize:14}}>{data?.summary || '—'}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}


