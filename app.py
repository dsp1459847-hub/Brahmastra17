import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="MAYA AI - The Ultimate Engine", layout="wide")

st.title("MAYA AI 🦅: The Ultimate All-in-One Engine ⚡")
st.markdown("Aapke saare Master Rules Active hain: **1. Pattern Accuracy | 2. Cross-Shift Linker | 3. Black Box | 4. TIER LINKER | 5. MINIMUM MAX-FAIL PRIORITY! (Timeframes: 90)**")

if 'results_cache' not in st.session_state:
    st.session_state.results_cache = {}

def reset_memory():
    st.session_state.results_cache = {}

st.sidebar.header("📁 Data Settings")
uploaded_file = st.sidebar.file_uploader("Upload CSV/Excel", type=['csv', 'xlsx'], on_change=reset_memory)
selected_end_date = st.sidebar.date_input("Calculation Date (T)", on_change=reset_memory)

if st.sidebar.button("Clear Memory & Re-Run"):
    reset_memory()
    st.rerun()

shift_order = ["DB", "SG", "FD", "GD", "ZA", "GL", "DS"]

@st.cache_data
def load_data(file_val):
    if file_val.name.endswith('.csv'): df = pd.read_csv(file_val)
    else: df = pd.read_excel(file_val)
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
    df = df.sort_values(by='DATE').reset_index(drop=True)
    for col in shift_order:
        if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

if uploaded_file is not None:
    try:
        df = load_data(uploaded_file)
        filtered_df = df[df['DATE'].dt.date <= selected_end_date].copy()
        if len(filtered_df) == 0: st.stop()
        
        target_date_next = selected_end_date + timedelta(days=1)
        st.info(f"📅 **Data Read Up To:** {selected_end_date.strftime('%d %B %Y')} | 🎯 **Target Date:** {target_date_next.strftime('%A, %d %B %Y')}")

        @st.cache_data
        def get_all_tiers_cached(past_tuple):
            scores = {n: 0 for n in range(100)}
            for days in range(1, min(46, len(past_tuple) + 1)):
                sheet = past_tuple[-days:]
                for num, freq in Counter(sheet).items(): scores[num] += freq * (1 + (1/days)) 
            ranked = sorted(range(100), key=lambda x: scores[x], reverse=True)
            return {'H': ranked[0:33], 'M': ranked[33:66], 'L': ranked[66:100]}

        def get_tier_name(num, tiers_dict):
            if num in tiers_dict['H']: return 'H'
            elif num in tiers_dict['M']: return 'M'
            elif num in tiers_dict['L']: return 'L'
            return 'FAIL'

        @st.cache_data
        def get_doomed_timeframe_predictions(history_tuple):
            h_list = list(history_tuple)
            black_traps = set()
            # 🚀 Range badha kar 90 kar di gayi hai aapke order ke anusaar
            for tf in range(1, 91):
                hit_history = []
                for i in range(15, len(h_list)):
                    pat = h_list[:i][-tf:]
                    nxt = [h_list[:i][k+tf] for k in range(len(h_list[:i])-tf) if h_list[:i][k:k+tf] == pat]
                    if not nxt: hit_history.append(False)
                    else:
                        top = Counter(nxt).most_common(1)[0][0]
                        td = get_all_tiers_cached(tuple(h_list[:i]))
                        hit_history.append(get_tier_name(top, td) == get_tier_name(h_list[i], td))
                
                if len(hit_history) < 10: continue
                will_fail = False
                
                if hit_history[-1] == True:
                    pass_twice = sum(1 for i in range(1, len(hit_history)) if hit_history[i] and hit_history[i-1])
                    if pass_twice == 0: will_fail = True
                elif hit_history[-1] == False:
                    curr_f = 0
                    for k in range(len(hit_history)-1, -1, -1):
                        if not hit_history[k]: curr_f += 1
                        else: break
                    past_fails = []
                    f_count = 0
                    for h in hit_history[:-curr_f]:
                        if not h: f_count += 1
                        elif f_count > 0: 
                            past_fails.append(f_count)
                            f_count = 0
                    if past_fails:
                        if curr_f < min(past_fails): will_fail = True
                            
                if will_fail:
                    pat = h_list[-tf:]
                    nxt = [h_list[i+tf] for i in range(len(h_list)-tf) if h_list[i:i+tf] == pat]
                    if nxt:
                        doomed_preds = [item[0] for item in Counter(nxt).most_common(5)]
                        black_traps.update(doomed_preds)
            return list(black_traps)

        def get_unified_best_timeframe(history_tuple, dates_tuple, prev_shift_decisions):
            h_list = list(history_tuple)
            d_list = list(dates_tuple)
            zero_fail_candidates = []
            one_fail_candidates = []
            other_candidates = []
            
            # 🚀 Timeframe 90 din tak test honge Minimum fail dhoondhne ke liye
            for tf in range(1, 91):
                hit_history = []
                hit_dates = [] 
                for i in range(15, len(h_list)):
                    pat = h_list[:i][-tf:]
                    nxt = [h_list[:i][k+tf] for k in range(len(h_list[:i])-tf) if h_list[:i][k:k+tf] == pat]
                    if not nxt: 
                        hit_history.append(False)
                    else:
                        top = Counter(nxt).most_common(1)[0][0]
                        td = get_all_tiers_cached(tuple(h_list[:i]))
                        is_hit = (get_tier_name(top, td) == get_tier_name(h_list[i], td))
                        hit_history.append(is_hit)
                        if is_hit: hit_dates.append(d_list[i])
                
                if not hit_history: continue
                
                curr_f = 0
                for k in range(len(hit_history)-1, -1, -1):
                    if hit_history[k] == False: curr_f += 1
                    else: break
                
                pattern_matches = 0
                pattern_successes = 0
                for i in range(1, len(hit_history)-1):
                    if curr_f == 0:
                        if hit_history[i] == True:
                            pattern_matches += 1
                            if hit_history[i+1] == True: pattern_successes += 1
                    else:
                        if i >= curr_f:
                            is_exact_streak = True
                            for j in range(curr_f):
                                if hit_history[i-j] != False:
                                    is_exact_streak = False
                                    break
                            if is_exact_streak:
                                if (i - curr_f < 0) or hit_history[i - curr_f] == True:
                                    pattern_matches += 1
                                    if hit_history[i+1] == True: pattern_successes += 1

                base_accuracy = (pattern_successes / pattern_matches * 100) if pattern_matches > 0 else 0
                
                # Cross-Shift Correlation (Linker)
                cross_shift_msgs = []
                if prev_shift_decisions:
                    for prev_dec in prev_shift_decisions:
                        prev_hit_dates = prev_dec['hit_dates']
                        if not prev_hit_dates: continue
                        
                        common_hits = len(set(hit_dates) & set(prev_hit_dates))
                        prev_total = len(prev_hit_dates)
                        joint_prob = (common_hits / prev_total) if prev_total > 0 else 1.0
                        
                        if tf == prev_dec['tf']:
                            msg = f"{prev_dec['shift']} Overlap: {joint_prob*100:.0f}%"
                            if joint_prob < 0.5:
                                base_accuracy = base_accuracy * joint_prob
                                msg += " ⚠️ Penalized!"
                            cross_shift_msgs.append(msg)
                            
                final_cross_msg = " | ".join(cross_shift_msgs) if cross_shift_msgs else ""
                
                jan_apr = sum(1 for i in range(1, len(hit_history)) if hit_history[i] and hit_history[i-1] and (1 <= d_list[i+15].month <= 4))
                max_f = 0
                c_f = 0
                for h in hit_history:
                    if not h: 
                        c_f += 1
                        if c_f > max_f: max_f = c_f
                    else: c_f = 0

                tf_data = {
                    'tf': tf, 'score': jan_apr, 'max_f': max_f, 'curr_f': curr_f,
                    'p_match': pattern_matches, 'p_succ': pattern_successes, 'p_acc': base_accuracy,
                    'hit_dates': hit_dates, 'cross_msg': final_cross_msg
                }

                if curr_f == 0: zero_fail_candidates.append(tf_data)
                elif curr_f == 1: one_fail_candidates.append(tf_data)
                else: other_candidates.append(tf_data)

            # 🚀 THE FIX: SORTING BY MINIMUM MAX-FAIL FIRST! 
            # Ab 25 Max-Fail wale seedha aakhiri mein fek diye jayenge, minimum fail wale Rank 1 par aayenge!
            if zero_fail_candidates:
                best = sorted(zero_fail_candidates, key=lambda x: (x['max_f'], -x['p_acc'], -x['score']))[0]
                return best['tf'], "ZERO FAIL", 0, best['score'], best['max_f'], best['p_match'], best['p_succ'], best['p_acc'], best['hit_dates'], best['cross_msg']
            elif one_fail_candidates:
                best = sorted(one_fail_candidates, key=lambda x: (x['max_f'], -x['p_acc'], -x['score']))[0]
                return best['tf'], "ONE FAIL REBOUND", 1, best['score'], best['max_f'], best['p_match'], best['p_succ'], best['p_acc'], best['hit_dates'], best['cross_msg']
            elif other_candidates:
                best = sorted(other_candidates, key=lambda x: (x['max_f'], -x['p_acc'], -x['score']))[0]
                return best['tf'], f"GEAR SHIFT ({best['curr_f']} Fail)", best['curr_f'], best['score'], best['max_f'], best['p_match'], best['p_succ'], best['p_acc'], best['hit_dates'], best['cross_msg']
                
            return 15, "DEFAULT FALLBACK", 0, 0, 99, 0, 0, 0, [], ""

        # Aapka Purana Original Tier Linker Function (No Changes Here)
        def calculate_tier_link(curr_shift, prev_shift, prev_tier_actual):
            transitions = {'H': 0, 'M': 0, 'L': 0}
            temp_df = filtered_df.dropna(subset=[curr_shift, prev_shift]).tail(50) 
            
            for idx, row in temp_df.iterrows():
                p_hist = filtered_df.loc[:idx-1, prev_shift].dropna().astype(int).tolist()
                c_hist = filtered_df.loc[:idx-1, curr_shift].dropna().astype(int).tolist()
                
                if len(p_hist) < 15 or len(c_hist) < 15: continue
                
                p_tiers = get_all_tiers_cached(tuple(p_hist))
                c_tiers = get_all_tiers_cached(tuple(c_hist))
                
                p_act_tier = get_tier_name(row[prev_shift], p_tiers)
                c_act_tier = get_tier_name(row[curr_shift], c_tiers)
                
                if p_act_tier == prev_tier_actual and c_act_tier in transitions:
                    transitions[c_act_tier] += 1
                    
            total = sum(transitions.values())
            if total > 0:
                best_t = max(transitions, key=transitions.get)
                prob = (transitions[best_t] / total) * 100
                return best_t, prob
            return None, 0

        def render_ank(nums, traps, black_boxes):
            nums = list(set(nums)); nums.sort()
            html = "<div style='display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px;'>"
            for n in nums:
                if n in black_boxes:
                    bg = "#000000"; border = "#555"; font_c = "white"; extra = "box-shadow: 0 0 8px rgba(255,0,0,0.8);"
                elif n in traps:
                    bg = "#1a1a1a"; border = "#333"; font_c = "#555"; extra = "text-decoration: line-through;"
                else:
                    bg = "#00FF7F"; border = "#008000"; font_c = "black"; extra = ""
                html += f"<div style='background:{bg}; padding:10px; border-radius:8px; text-align:center; min-width:45px; border:2px solid {border}; {extra}'>" \
                        f"<span style='font-size:20px; font-weight:bold; color:{font_c};'>{n:02d}</span></div>"
            html += "</div>"
            return html

        prev_shift_decisions = []
        last_processed_shift = None
        last_shift_tier = None
        
        for shift in shift_order:
            if shift not in df.columns: continue
            
            st.markdown("---")
            
            if shift not in st.session_state.results_cache:
                with st.spinner(f"Searching {shift}... Minimum Max-Fail Filters Applying!"):
                    s_data = filtered_df[['DATE', shift]].dropna()
                    hist = s_data[shift].astype(int).tolist()
                    d_list = s_data['DATE'].tolist()
                    
                    if len(hist) < 60: continue
                    
                    res_vals = get_unified_best_timeframe(tuple(hist), tuple(d_list), prev_shift_decisions)
                    tf_final = res_vals[0]
                    
                    tiers = get_all_tiers_cached(tuple(hist))
                    nxt = [hist[i+tf_final] for i in range(len(hist)-tf_final) if hist[i:i+tf_final] == hist[-tf_final:]]
                    base_tier = get_tier_name(Counter(nxt).most_common(1)[0][0], tiers) if nxt else 'H'
                    
                    final_tier = base_tier
                    tier_msg = f"Default predicted tier '{base_tier}' selected."
                    
                    if last_processed_shift and last_shift_tier:
                        linked_tier, linked_prob = calculate_tier_link(shift, last_processed_shift, last_shift_tier)
                        if linked_tier:
                            final_tier = linked_tier
                            tier_msg = f"<b>{last_processed_shift}</b> mein <b>'{last_shift_tier}'</b> aane ke baad, <b>{shift}</b> mein <b>'{linked_tier}'</b> aane ki Probability <b>{linked_prob:.0f}%</b> hai!"
                    
                    last_n = hist[-1]
                    prev_n = hist[-2]
                    traps = set([(last_n+1)%100, (last_n-1)%100, int(str(last_n).zfill(2)[::-1]), (last_n + (last_n - prev_n))%100])
                    for n, count in Counter(hist[-5:]).items():
                        if count >= 2: traps.add(n)
                        
                    doomed_black_boxes = get_doomed_timeframe_predictions(tuple(hist))
                    pure_green_nums = [n for n in tiers[final_tier] if n not in traps and n not in doomed_black_boxes]
                    
                    st.session_state.results_cache[shift] = {
                        'logic': res_vals[1], 'tf': tf_final, 'curr_f': res_vals[2], 
                        'score': res_vals[3], 'max_f': res_vals[4], 
                        'p_match': res_vals[5], 'p_succ': res_vals[6], 'p_acc': res_vals[7],
                        'hit_dates': res_vals[8], 'cross_msg': res_vals[9],
                        'tier': final_tier, 'tier_linker_msg': tier_msg,
                        'traps': list(traps), 'black_boxes': doomed_black_boxes, 'raw_tier_nums': tiers[final_tier],
                        'pure_green': pure_green_nums
                    }

            res = st.session_state.results_cache[shift]
            
            prev_shift_decisions.append({
                'shift': shift, 'tf': res['tf'], 'hit_dates': res['hit_dates']
            })
            last_processed_shift = shift
            last_shift_tier = res['tier']
            
            dates_today = filtered_df[filtered_df[shift].notna()]['DATE'].tolist()
            date_kal = dates_today[-1].strftime('%d %b %Y') if len(dates_today) > 0 else ""
            date_parso = dates_today[-2].strftime('%d %b %Y') if len(dates_today) > 1 else ""
            date_start_fail = dates_today[-1 - res['curr_f']].strftime('%d %b %Y') if len(dates_today) > res['curr_f'] else ""
            
            st.subheader(f"🧩 Shift: {shift}")
            
            if res['curr_f'] == 0:
                banner_bg = "#28a745"; border_c = "#1e7e34"; text_col = "white"
                banner_text = f"✅ <b>ZERO FAIL:</b> Pichla din (<b>{date_kal}</b>) PAAS tha.<br><i>History: <b>{res['p_succ']}/{res['p_match']}</b> baar PAAS hua! (<b>{res['p_acc']:.1f}% Accuracy</b>)</i>"
            elif res['curr_f'] == 1:
                banner_bg = "#ffc107"; border_c = "#d39e00"; text_col = "black"
                banner_text = f"⚠️ <b>1-FAIL REBOUND:</b> <b>{date_parso}</b> ko Pass tha, kal Fail hua.<br><i>History: <b>{res['p_succ']}/{res['p_match']}</b> baar rebound PAAS hua! (<b>{res['p_acc']:.1f}% Accuracy</b>)</i>"
            else:
                banner_bg = "#FF4B4B"; border_c = "#c82333"; text_col = "white"
                banner_text = f"🔥 <b>GEAR SHIFT ({res['curr_f']} Fail):</b> <b>{date_start_fail}</b> se fail hai.<br><i>History: <b>{res['p_succ']}/{res['p_match']}</b> baar rebound PAAS hua! (<b>{res['p_acc']:.1f}% Accuracy</b>)</i>"

            st.markdown(f"<div style='background:{banner_bg}; padding:10px; border-radius:8px; border: 2px solid {border_c}; text-align:center; color:{text_col}; margin-bottom:10px;'>{banner_text}</div>", unsafe_allow_html=True)

            c1, c2 = st.columns([1, 2.5])
            with c1:
                actual_row = df[df['DATE'].dt.date == target_date_next]
                actual_val = int(actual_row.iloc[0][shift]) if not actual_row.empty and pd.notna(actual_row.iloc[0][shift]) else None
                
                is_hit = actual_val in res['pure_green'] if actual_val is not None else False
                
                if actual_val is not None:
                    m_color = "#28a745" if is_hit else "#FF4B4B"
                    st.markdown(f"<div style='background:{m_color}; padding:10px; border-radius:8px; text-align:center; color:white;'>Match Result ({target_date_next.strftime('%d %b')}):<br><b style='font-size:26px;'>{actual_val:02d}</b><br>{'HIT! ✅' if is_hit else 'MISS ❌'}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='background:#555; padding:10px; border-radius:8px; text-align:center; color:white;'>Result:<br><b>Waiting...</b></div>", unsafe_allow_html=True)
            
            with c2:
                border_col = "#00FF7F"
                bg_col = "#00FF7F15"
                st.markdown(f"<div style='border:2px solid {border_col}; padding:10px; border-radius:8px; background:{bg_col}; font-size:14px;'>"
                            f"<b>Logic:</b> {res['logic']} | <b>Selected Gear:</b> <code>{res['tf']}-Din TF</code><br>"
                            f"<i>🔗 <b>Cross-Shift Timeframe Links:</b> {res['cross_msg'] if res['cross_msg'] else 'Fresh Sequence (Independent)'}</i><br>"
                            f"<i>🔥 <b>MIN MAX-FAIL:</b> History ka sabse lamba fail sirf <b>{res['max_f']} din</b> gaya hai!</i><br>"
                            f"<hr style='margin:5px 0; border-top:1px solid #444;'>"
                            f"🏆 <b>TIER LINKER:</b> {res['tier_linker_msg']}<br>"
                            f"✅ <b>HARA (Play):</b> {len(res['pure_green'])} Nums | ⬛ <b>KAALA (Doomed):</b> {len([n for n in res['raw_tier_nums'] if n in res['black_boxes']])} Nums"
                            f"</div>", unsafe_allow_html=True)

            st.markdown(render_ank(res['raw_tier_nums'], res['traps'], res['black_boxes']), unsafe_allow_html=True)

    except Exception as e:
 
