import streamlit as st
import json
from datetime import datetime
import os

st.set_page_config(page_title="SHAIM AI Agent", page_icon="🔍", layout="wide")

st.markdown("""
<style>
    .main {padding: 1rem;}
    h1 {color: #FF4B4B; font-size: 2.5rem; font-weight: 700;}
    .stButton>button {border-radius: 8px; font-weight: 600; transition: all 0.2s;}
    .stButton>button:hover {transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15);}
    .ai-analysis {background: linear-gradient(135deg, #E3F2FD 0%, #E8F5E9 100%); padding: 1.5rem; border-radius: 12px; border-left: 5px solid #4CAF50; margin: 1rem 0;}
    .recommendation {background: #FFF3E0; padding: 1rem; border-radius: 8px; border-left: 4px solid #FF9800; margin: 0.5rem 0;}
</style>
""", unsafe_allow_html=True)

# Initialize
if 'stage' not in st.session_state:
    st.session_state.update({
        'stage': 'home',
        'analyst_name': '',
        'problem': '',
        'mode': 'human',
        'messages': [],
        'answers': [],
        'why_level': 0,
        'library': [],
        'api_key': os.getenv('ANTHROPIC_API_KEY', ''),
        'ai_analysis': None,
        'ai_recommendations': None
    })

def call_ai(prompt, system="", max_tokens=2000):
    """Call Claude AI"""
    if not st.session_state.api_key:
        return "⚠️ Please add API key in sidebar (console.anthropic.com)"
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=st.session_state.api_key)
        
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            system=system if system else "You are SHAIM, an expert root cause analysis consultant.",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        if "401" in str(e) or "authentication" in str(e).lower():
            return "⚠️ Invalid API key. Get new key from console.anthropic.com"
        return f"⚠️ Error: {str(e)[:200]}"

def analyze_problem_with_ai(problem):
    """AI analyzes the problem and suggests root causes"""
    prompt = f"""Analyze this problem and provide deep root cause analysis:

PROBLEM: {problem}

Provide a comprehensive analysis in JSON format:
{{
  "problem_summary": "Brief summary",
  "potential_root_causes": [
    "First potential organizational/systemic root cause",
    "Second potential root cause",
    "Third potential root cause"
  ],
  "five_whys_analysis": {{
    "why_1": "First why - what immediately caused this?",
    "why_2": "Second why - why did that cause occur?",
    "why_3": "Third why - deeper systemic factor",
    "why_4": "Fourth why - organizational level",
    "why_5": "Fifth why - TRUE root cause (organizational/cultural)"
  }},
  "key_insights": [
    "Important insight 1",
    "Important insight 2",
    "Important insight 3"
  ],
  "evidence_needed": [
    "What documentation to check",
    "What data to gather",
    "What to verify"
  ]
}}

Focus on ORGANIZATIONAL and SYSTEMIC root causes, not individual blame.
Be specific and actionable."""

    system = "You are an expert root cause analyst. Analyze problems deeply, refuse shallow 'human error' conclusions, and identify organizational/systemic root causes. Always respond with valid JSON."
    
    response = call_ai(prompt, system, 2500)
    
    try:
        # Extract JSON
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]
        
        return json.loads(response.strip())
    except:
        return None

def generate_recommendations_with_ai(problem, root_cause):
    """AI generates specific recommendations"""
    prompt = f"""Based on this root cause analysis, generate detailed, actionable recommendations:

PROBLEM: {problem}

ROOT CAUSE: {root_cause}

Provide recommendations in JSON format:
{{
  "immediate_actions": [
    {{
      "action": "Specific immediate action",
      "timeline": "24-48 hours",
      "responsible": "Who should do this",
      "measurable": "How to measure success"
    }}
  ],
  "short_term_solutions": [
    {{
      "solution": "Short-term countermeasure",
      "timeline": "1-3 months",
      "resources": "What's needed",
      "expected_outcome": "Measurable result"
    }}
  ],
  "long_term_solutions": [
    {{
      "solution": "Strategic long-term solution",
      "timeline": "3-12 months",
      "investment": "Estimated cost/effort",
      "impact": "Expected organizational impact"
    }}
  ],
  "monitoring_plan": [
    {{
      "metric": "What to measure",
      "target": "Target value",
      "frequency": "How often",
      "responsibility": "Who tracks this"
    }}
  ]
}}

Make recommendations SPECIFIC, MEASURABLE, and ACTIONABLE."""

    system = "You are an expert in organizational improvement and countermeasure design. Generate specific, measurable, actionable recommendations."
    
    response = call_ai(prompt, system, 3000)
    
    try:
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]
        
        return json.loads(response.strip())
    except:
        return None

def save_analysis():
    """Save to library"""
    st.session_state.library.append({
        'id': datetime.now().strftime('%Y%m%d%H%M%S'),
        'time': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'analyst': st.session_state.analyst_name,
        'problem': st.session_state.problem,
        'mode': st.session_state.mode,
        'answers': st.session_state.answers.copy(),
        'messages': st.session_state.messages.copy(),
        'ai_analysis': st.session_state.ai_analysis,
        'ai_recommendations': st.session_state.ai_recommendations
    })

# SIDEBAR
with st.sidebar:
    st.markdown("### 🔍 SHAIM AI Agent")
    st.caption("AI-Powered Root Cause Analysis")
    st.markdown("---")
    
    if not st.session_state.api_key:
        st.error("⚠️ API Key Required")
        key = st.text_input("Claude API Key", type="password", help="From console.anthropic.com")
        if key:
            st.session_state.api_key = key
            st.success("✅ Key saved!")
            st.rerun()
        st.markdown("[Get free API key →](https://console.anthropic.com)")
    else:
        st.success("✅ AI Ready")
        if st.button("🔄 Change Key"):
            st.session_state.api_key = ''
            st.rerun()
    
    st.markdown("---")
    st.markdown("#### 📍 Navigation")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.stage = 'home'
            st.rerun()
    with c2:
        if st.button("📚 Library", use_container_width=True):
            st.session_state.stage = 'library'
            st.rerun()
    
    c3, c4 = st.columns(2)
    with c3:
        if st.button("📊 Stats", use_container_width=True):
            st.session_state.stage = 'dashboard'
            st.rerun()
    with c4:
        if st.button("💬 Chat", use_container_width=True):
            st.session_state.stage = 'chatbot'
            st.rerun()
    
    if st.session_state.library:
        st.markdown("---")
        st.metric("Total Analyses", len(st.session_state.library))
    
    st.markdown("---")
    st.caption("🎓 AUM Industrial Engineering")
    st.caption("v4.0 - AI Intelligence")

# HOME
if st.session_state.stage == 'home':
    st.title("🔍 SHAIM AI Agent")
    st.markdown("**AI-Powered Root Cause Analysis System**")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### ❌ Manual Analysis:")
        st.write("- Stops at 'human error'\n- No AI insights\n- Shallow conclusions\n- Generic solutions")
    with col2:
        st.markdown("### ✅ SHAIM AI:")
        st.write("- AI analyzes deeply\n- Suggests root causes\n- Organizational insights\n- Custom recommendations")
    
    st.markdown("---")
    st.markdown("### 👤 Enter Your Information")
    
    col1, col2 = st.columns(2)
    with col1:
        analyst = st.text_input("Your Name:", value=st.session_state.analyst_name)
        st.session_state.analyst_name = analyst
    
    st.markdown("### 📝 Describe Your Problem")
    problem = st.text_area("Problem Description:", value=st.session_state.problem, height=150,
                          placeholder="Describe what happened in detail. Include: when, where, who was involved, what evidence you have...")
    st.session_state.problem = problem
    
    if problem and len(problem) > 30:
        st.markdown("---")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🤖 Analyze with AI", type="primary", use_container_width=True):
                with st.spinner("🧠 AI is analyzing your problem deeply..."):
                    analysis = analyze_problem_with_ai(problem)
                    st.session_state.ai_analysis = analysis
                    
                    if analysis:
                        st.session_state.stage = 'ai_analysis'
                        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🎯 Or Choose Manual Analysis Mode")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👤 System 1\nHuman-Led", use_container_width=True):
            if analyst and problem:
                st.session_state.stage = 'analysis'
                st.session_state.mode = 'human'
                st.session_state.why_level = 1
                st.rerun()
    
    with col2:
        if st.button("🤖 System 2\nAI Interview", use_container_width=True):
            if analyst and problem:
                st.session_state.stage = 'analysis'
                st.session_state.mode = 'interview'
                st.rerun()
    
    with col3:
        if st.button("💬 System 3\nAI Chatbot", use_container_width=True):
            if analyst and problem:
                st.session_state.stage = 'chatbot'
                st.session_state.messages = []
                st.rerun()

# AI ANALYSIS RESULTS
elif st.session_state.stage == 'ai_analysis':
    st.title("🧠 AI Root Cause Analysis")
    st.caption(f"Analyst: {st.session_state.analyst_name}")
    
    st.info(f"**Problem:** {st.session_state.problem}")
    
    if st.session_state.ai_analysis:
        analysis = st.session_state.ai_analysis
        
        st.markdown("---")
        
        # Problem Summary
        st.markdown("### 📋 AI Problem Analysis")
        st.markdown(f"<div class='ai-analysis'><strong>Analysis:</strong> {analysis.get('problem_summary', 'N/A')}</div>", 
                   unsafe_allow_html=True)
        
        # Potential Root Causes
        st.markdown("### 🎯 AI-Identified Potential Root Causes")
        for i, cause in enumerate(analysis.get('potential_root_causes', []), 1):
            st.markdown(f"**{i}.** {cause}")
        
        # Five Whys
        st.markdown("### 🔍 AI-Generated Five Whys Analysis")
        five_whys = analysis.get('five_whys_analysis', {})
        
        for i in range(1, 6):
            why_key = f'why_{i}'
            if why_key in five_whys:
                with st.expander(f"**Why {i}:** {five_whys[why_key][:80]}...", expanded=(i==5)):
                    st.write(five_whys[why_key])
                    if i == 5:
                        st.success("✅ **THIS IS THE ROOT CAUSE** (Organizational/Systemic Level)")
        
        # Key Insights
        st.markdown("### 💡 Key Insights")
        for insight in analysis.get('key_insights', []):
            st.info(f"💡 {insight}")
        
        # Evidence Needed
        st.markdown("### 📊 Evidence to Gather")
        for evidence in analysis.get('evidence_needed', []):
            st.warning(f"📋 {evidence}")
        
        st.markdown("---")
        
        # Generate Recommendations
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📝 Generate Recommendations", type="primary", use_container_width=True):
                with st.spinner("🤖 AI generating detailed recommendations..."):
                    root_cause = five_whys.get('why_5', 'Unknown')
                    recs = generate_recommendations_with_ai(st.session_state.problem, root_cause)
                    st.session_state.ai_recommendations = recs
                    st.rerun()
        
        with col2:
            if st.button("💾 Save to Library", use_container_width=True):
                save_analysis()
                st.success("✅ Saved!")
        
        with col3:
            if st.button("🏠 New Analysis", use_container_width=True):
                st.session_state.stage = 'home'
                st.session_state.ai_analysis = None
                st.session_state.ai_recommendations = None
                st.rerun()
        
        # Show Recommendations if generated
        if st.session_state.ai_recommendations:
            recs = st.session_state.ai_recommendations
            
            st.markdown("---")
            st.markdown("## 🎯 AI-Generated Recommendations")
            
            # Immediate Actions
            st.markdown("### ⚡ Immediate Actions (24-48 hours)")
            for action in recs.get('immediate_actions', []):
                st.markdown(f"""
                <div class='recommendation'>
                <strong>Action:</strong> {action.get('action', 'N/A')}<br>
                <strong>Timeline:</strong> {action.get('timeline', 'N/A')}<br>
                <strong>Responsible:</strong> {action.get('responsible', 'N/A')}<br>
                <strong>Measurable:</strong> {action.get('measurable', 'N/A')}
                </div>
                """, unsafe_allow_html=True)
            
            # Short-term
            st.markdown("### 📅 Short-Term Solutions (1-3 months)")
            for sol in recs.get('short_term_solutions', []):
                with st.expander(f"**{sol.get('solution', 'N/A')[:60]}...**"):
                    st.write(f"**Timeline:** {sol.get('timeline', 'N/A')}")
                    st.write(f"**Resources:** {sol.get('resources', 'N/A')}")
                    st.write(f"**Expected Outcome:** {sol.get('expected_outcome', 'N/A')}")
            
            # Long-term
            st.markdown("### 🎯 Long-Term Solutions (3-12 months)")
            for sol in recs.get('long_term_solutions', []):
                with st.expander(f"**{sol.get('solution', 'N/A')[:60]}...**"):
                    st.write(f"**Timeline:** {sol.get('timeline', 'N/A')}")
                    st.write(f"**Investment:** {sol.get('investment', 'N/A')}")
                    st.write(f"**Impact:** {sol.get('impact', 'N/A')}")
            
            # Monitoring
            st.markdown("### 📊 Monitoring Plan")
            for metric in recs.get('monitoring_plan', []):
                st.write(f"**{metric.get('metric', 'N/A')}**")
                st.caption(f"Target: {metric.get('target', 'N/A')} | Frequency: {metric.get('frequency', 'N/A')} | Responsibility: {metric.get('responsibility', 'N/A')}")

# LIBRARY
elif st.session_state.stage == 'library':
    st.title("📚 Analysis Library")
    
    if not st.session_state.library:
        st.info("No analyses saved yet")
    else:
        for analysis in reversed(st.session_state.library):
            with st.expander(f"📄 {analysis['problem'][:60]}... - {analysis['time']}"):
                st.write(f"**Analyst:** {analysis['analyst']}")
                st.write(f"**Mode:** {analysis['mode']}")
                
                if analysis.get('ai_analysis'):
                    st.success("✅ AI Analysis Available")
                    st.write("**AI Root Cause:**")
                    five_whys = analysis['ai_analysis'].get('five_whys_analysis', {})
                    st.info(five_whys.get('why_5', 'N/A'))

# DASHBOARD
elif st.session_state.stage == 'dashboard':
    st.title("📊 Dashboard")
    
    if st.session_state.library:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Analyses", len(st.session_state.library))
        with col2:
            ai_analyses = len([a for a in st.session_state.library if a.get('ai_analysis')])
            st.metric("AI Analyses", ai_analyses)
        with col3:
            manual = len(st.session_state.library) - ai_analyses
            st.metric("Manual", manual)
    else:
        st.info("Complete analyses to see stats")

# CHATBOT
elif st.session_state.stage == 'chatbot':
    st.title("💬 AI Chatbot Analysis")
    st.caption(f"Analyst: {st.session_state.analyst_name}")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    if prompt := st.chat_input("Your response..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        sys = f"""You are SHAIM AI. Analyze this problem: {st.session_state.problem}

Refuse shallow answers, demand evidence, guide to root causes."""
        
        with st.chat_message("assistant"):
            response = call_ai(prompt, sys, 1500)
            st.write(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

# ANALYSIS (System 1 & 2)
elif st.session_state.stage == 'analysis':
    st.title("🔍 Analysis")
    st.info(f"**Problem:** {st.session_state.problem}")
    
    if st.session_state.mode == 'human':
        st.markdown(f"### Why Level {st.session_state.why_level}/5")
        answer = st.text_area("Your answer:", height=100)
        
        if st.button("Submit"):
            if answer:
                st.session_state.answers.append(answer)
                if st.session_state.why_level < 5:
                    st.session_state.why_level += 1
                    st.rerun()
                else:
                    save_analysis()
                    st.success("Complete!")

st.markdown("---")
st.caption("🎓 AUM Industrial Engineering | SHAIM v4.0 - AI Intelligence")
